"""Run the release browser audit against a local Streamlit process.

Install Playwright separately for this optional audit; it is intentionally not a
production dependency: ``pip install playwright && playwright install chromium``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "release_audit" / "streamlit"
BASE_URL = "http://localhost:8511"
ROUTES = {
    "News Desk": "/",
    "Analyse Article": "/analyse-article",
    "Model Accountability": "/model-accountability",
    "Dataset Analysis": "/dataset-analysis",
    "Editorial Archive": "/editorial-archive",
    "Research & About": "/research-about",
}
VIEWPORTS = ((360, 800), (390, 844), (768, 1024), (1366, 900), (1920, 1080))


def wait_for_server(process: subprocess.Popen[bytes]) -> None:
    for _ in range(120):
        if process.poll() is not None:
            raise RuntimeError(f"Streamlit exited with code {process.returncode}")
        try:
            with urllib.request.urlopen(BASE_URL, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Streamlit did not become ready")


def ready(page: Page, marker: str = "NewsLens AI") -> None:
    page.locator("[data-testid='stAppViewContainer']").wait_for(timeout=30_000)
    page.wait_for_function(
        "marker => document.body.innerText.includes(marker)", arg=marker, timeout=30_000
    )
    page.wait_for_timeout(500)


def page_geometry(page: Page) -> dict[str, object]:
    return page.evaluate(
        """() => ({
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
          horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
          minimumInteractiveHeight: Math.min(...Array.from(document.querySelectorAll('a, button, input, textarea, select'))
            .filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; })
            .map(el => el.getBoundingClientRect().height)),
        })"""
    )


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["NEWSLENS_HISTORY_MODE"] = "session"
    environment["NEWSLENS_DATABASE_PATH"] = "/tmp/newslens-release-audit-persistent.db"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.address=127.0.0.1",
            "--server.port=8511",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    audit: dict[str, object] = {
        "same_tab_navigation": [],
        "direct_routes": {},
        "viewports": {},
        "console_errors": [],
        "failed_responses": [],
    }
    try:
        wait_for_server(process)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=os.getenv("NEWSLENS_CHROMIUM_PATH") or None,
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--no-proxy-server"],
            )
            context_a = browser.new_context(viewport={"width": 1366, "height": 900})
            def register_page(observed_page: Page) -> None:
                observed_page.on(
                    "console",
                    lambda message: audit["console_errors"].append(
                        {"type": message.type, "text": message.text, "url": observed_page.url}
                    )
                    if message.type == "error"
                    else None,
                )
                observed_page.on(
                    "response",
                    lambda response: audit["failed_responses"].append(
                        {"status": response.status, "url": response.url, "page": observed_page.url}
                    )
                    if response.status >= 400
                    else None,
                )

            page = context_a.new_page()
            register_page(page)
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30_000)
            ready(page, "PUBLIC HISTORY")
            starting_tabs = len(context_a.pages)

            for label, path in ROUTES.items():
                before = len(context_a.pages)
                page.get_by_role("link", name=label, exact=True).click()
                page.wait_for_url(f"**{path}")
                ready(page)
                audit["same_tab_navigation"].append(
                    {
                        "label": label,
                        "path": path,
                        "tabs_before": before,
                        "tabs_after": len(context_a.pages),
                        "passed": before == len(context_a.pages) == starting_tabs,
                    }
                )

            # Browser history and refresh retain native routes and the Streamlit session.
            page.get_by_role("link", name="Analyse Article", exact=True).click()
            page.wait_for_url("**/analyse-article")
            page.go_back(wait_until="domcontentloaded")
            ready(page)
            back_path = page.url.endswith("/research-about")
            page.go_forward(wait_until="domcontentloaded")
            ready(page)
            forward_path = page.url.endswith("/analyse-article")
            page.reload(wait_until="domcontentloaded")
            ready(page)
            audit["browser_history"] = {
                "back": back_path,
                "forward": forward_path,
                "refresh": page.url.endswith("/analyse-article"),
            }

            sample = (ROOT / "data" / "sample" / "misleading_style_article.txt").read_text(
                encoding="utf-8"
            )
            page.get_by_label("Article title (optional)").fill("Browser audit session A")
            page.get_by_label("Full article text").fill(sample)
            page.get_by_role("button", name="Analyse Article", exact=True).click()
            page.get_by_role("heading", name="Browser audit session A", exact=True).first.wait_for(
                timeout=30_000
            )
            page.wait_for_timeout(700)
            audit["analysis"] = {
                "summary": page.get_by_text("Executive Summary", exact=True).is_visible(),
                "classification": page.get_by_text("Editorial risk signal", exact=False).first.is_visible(),
                "calibrated_confidence": page.get_by_text("calibrated confidence", exact=True).is_visible(),
                "calibration_policy": page.get_by_text("Calibration and review policy", exact=False).first.is_visible(),
                "explainability": page.get_by_role(
                    "heading", name="Why the linear model leaned this way", exact=True
                ).is_visible(),
                "no_undefined_chart_titles": page.evaluate(
                    """() => {
                      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                      let node;
                      while ((node = walker.nextNode())) {
                        if (node.nodeValue.trim() === "undefined") return false;
                      }
                      return true;
                    }"""
                ),
            }
            with page.expect_download(timeout=15_000) as download_event:
                page.get_by_role("button", name="Download Analysis JSON", exact=True).click()
            audit["analysis"]["json_download"] = download_event.value.suggested_filename.endswith(".json")
            with page.expect_download(timeout=15_000) as download_event:
                page.get_by_role("button", name="Download Analysis PDF", exact=True).click()
            audit["analysis"]["pdf_download"] = download_event.value.suggested_filename.endswith(".pdf")

            page.get_by_role("link", name="Editorial Archive", exact=True).click()
            page.wait_for_url("**/editorial-archive")
            ready(page)
            audit["session_a_archive"] = page.get_by_text(
                "Browser audit session A", exact=False
            ).first.is_visible()
            audit["newsroom_analytics"] = page.get_by_role(
                "heading", name="Session-local editorial signals", exact=True
            ).is_visible()
            audit["drift_insufficient_observations"] = page.get_by_text(
                "Insufficient observations for a reliable drift assessment.", exact=False
            ).is_visible()
            with page.expect_download(timeout=15_000) as download_event:
                page.get_by_role("button", name="Export Privacy-Safe Analytics as CSV", exact=True).click()
            audit["privacy_safe_analytics_csv_download"] = download_event.value.suggested_filename.endswith(".csv")
            with page.expect_download(timeout=15_000) as download_event:
                page.get_by_role("button", name="Export Filtered Archive as CSV", exact=True).click()
            audit["session_a_archive_csv_download"] = download_event.value.suggested_filename.endswith(".csv")

            review_status = page.get_by_role("combobox", name="Review status")
            review_status.click()
            page.keyboard.press("Home")
            for _ in range(3):
                page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            page.get_by_label("Reviewer notes", exact=True).fill("Browser audit human review")
            page.get_by_label("Supporting-source URLs (one public HTTP(S) URL per line)").fill(
                "https://example.com/evidence"
            )
            page.get_by_label("Final editorial assessment", exact=True).fill(
                "Evidence remains insufficient for a conclusive assessment."
            )
            page.get_by_role("button", name="Save Editorial Review", exact=True).click()
            ready(page, "Inconclusive")
            audit["human_review_workflow"] = page.get_by_text(
                "Inconclusive", exact=True
            ).first.is_visible()

            context_b = browser.new_context(viewport={"width": 1366, "height": 900})
            visitor_b = context_b.new_page()
            visitor_b.goto(f"{BASE_URL}/editorial-archive", wait_until="domcontentloaded")
            ready(visitor_b, "No archived analyses yet")
            audit["cross_visitor_isolation"] = {
                "visitor_b_empty": visitor_b.get_by_text("No archived analyses yet", exact=True).is_visible(),
                "visitor_a_record_hidden": visitor_b.get_by_text(
                    "Browser audit session A", exact=False
                ).count() == 0,
            }
            context_b.close()

            # Direct routes and refresh.
            for label, path in ROUTES.items():
                page.goto(f"{BASE_URL}{path}", wait_until="domcontentloaded")
                ready(page)
                page.reload(wait_until="domcontentloaded")
                ready(page)
                audit["direct_routes"][label] = {
                    "path": path,
                    "title": page.title(),
                    "passed": path == "/" or page.url.endswith(path),
                }

            # Keyboard activation of a native route.
            page.goto(BASE_URL, wait_until="domcontentloaded")
            ready(page, "PUBLIC HISTORY")
            keyboard_link = page.get_by_role("link", name="Analyse Article", exact=True)
            keyboard_link.focus()
            focus_visible = keyboard_link.evaluate("el => document.activeElement === el")
            page.keyboard.press("Enter")
            page.wait_for_url("**/analyse-article")
            audit["keyboard_navigation"] = {
                "focus": focus_visible,
                "enter_activation": page.url.endswith("/analyse-article"),
                "tabs_unchanged": len(context_a.pages) == starting_tabs,
            }

            # Exact requested responsive widths.
            for width, height in VIEWPORTS:
                page.set_viewport_size({"width": width, "height": height})
                page.goto(BASE_URL, wait_until="domcontentloaded")
                ready(page, "PUBLIC HISTORY")
                geometry = page_geometry(page)
                page.screenshot(
                    path=OUTPUT / f"news_desk_{width}.png", full_page=False
                )
                audit["viewports"][str(width)] = geometry

            # All six product sections have rendered content.
            section_markers = {
                "News Desk": ("A two-layer news intelligence engine",),
                "Analyse Article": ("Article source and analysis settings",),
                "Model Accountability": ("Model Accountability",),
                "Dataset Analysis": ("Dataset Analysis",),
                "Editorial Archive": ("Personal Editorial Archive", "No archived analyses yet"),
                "Research & About": ("Research & About",),
            }
            audit["six_sections"] = {}
            for label, path in ROUTES.items():
                page.goto(f"{BASE_URL}{path}", wait_until="domcontentloaded")
                ready(page)
                page.wait_for_function(
                    "expected => document.title.includes(expected)",
                    arg=label,
                    timeout=30_000,
                )
                page.wait_for_timeout(700)
                body_text = page.locator("body").inner_text()
                audit["six_sections"][label] = {
                    "title": page.title(),
                    "content_markers": section_markers[label],
                    "marker_visible": any(marker in body_text for marker in section_markers[label]),
                    "rendered": len(body_text) > 300,
                }

            audit["all_same_tab"] = all(
                item["passed"] for item in audit["same_tab_navigation"]
            ) and audit["keyboard_navigation"]["tabs_unchanged"]
            audit["all_viewports_no_overflow"] = all(
                not item["horizontalOverflow"] for item in audit["viewports"].values()
            )
            audit["all_six_sections"] = all(
                item["marker_visible"] and item["rendered"]
                for item in audit["six_sections"].values()
            )
            audit["known_streamlit_route_probes"] = [
                item
                for item in audit["failed_responses"]
                if item["status"] == 404
                and any(
                    marker in item["url"]
                    for marker in ("/_stcore/health", "/_stcore/host-config")
                )
            ]
            audit["unexpected_failed_responses"] = [
                item
                for item in audit["failed_responses"]
                if item not in audit["known_streamlit_route_probes"]
            ]
            generic_resource_error = (
                "Failed to load resource: the server responded with a status of 404 (Not Found)"
            )
            audit["unexpected_console_errors"] = [
                item
                for item in audit["console_errors"]
                if item["text"] != generic_resource_error
                or audit["unexpected_failed_responses"]
            ]
            context_a.close()
            browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    output_path = OUTPUT / "streamlit_browser_audit.json"
    output_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(audit, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
