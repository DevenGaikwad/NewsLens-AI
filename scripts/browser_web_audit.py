"""Audit the production Next.js presentation shell at the required widths."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
OUTPUT = ROOT / "reports" / "release_audit" / "web"
BASE_URL = "http://localhost:3011"
VIEWPORTS = ((360, 800), (390, 844), (768, 1024), (1366, 900), (1920, 1080))


def wait_for_server(process: subprocess.Popen[bytes]) -> None:
    for _ in range(120):
        if process.poll() is not None:
            raise RuntimeError(f"Next.js exited with code {process.returncode}")
        try:
            with urllib.request.urlopen(BASE_URL, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Next.js did not become ready")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["NEXT_TELEMETRY_DISABLED"] = "1"
    process = subprocess.Popen(
        [str(WEB / "node_modules" / ".bin" / "next"), "start", "-H", "127.0.0.1", "-p", "3011"],
        cwd=WEB,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    audit: dict[str, object] = {"viewports": {}, "console_errors": []}
    try:
        wait_for_server(process)
        with urllib.request.urlopen(BASE_URL, timeout=5) as response:
            response_headers = {key.lower(): value for key, value in response.headers.items()}
        required_headers = (
            "content-security-policy",
            "referrer-policy",
            "permissions-policy",
            "x-content-type-options",
            "x-frame-options",
            "strict-transport-security",
        )
        audit["security_headers"] = {
            "values": {name: response_headers.get(name) for name in required_headers},
            "all_present": all(response_headers.get(name) for name in required_headers),
            "frame_src_restricted": "frame-src https://your-app.streamlit.app"
            in response_headers.get("content-security-policy", "").lower(),
            "frame_ancestors_restricted": "frame-ancestors 'self'"
            in response_headers.get("content-security-policy", "").lower(),
        }
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=os.getenv("NEWSLENS_CHROMIUM_PATH") or None,
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--no-proxy-server"],
            )
            context = browser.new_context()
            page = context.new_page()
            page.on(
                "console",
                lambda message: audit["console_errors"].append(
                    {"type": message.type, "text": message.text, "url": page.url}
                )
                if message.type == "error"
                else None,
            )
            for width, height in VIEWPORTS:
                page.set_viewport_size({"width": width, "height": height})
                page.goto(BASE_URL, wait_until="networkidle")
                page.get_by_role("heading", name="Investigate language. Keep the uncertainty.").wait_for()
                geometry = page.evaluate(
                    """() => ({
                      scrollWidth: document.documentElement.scrollWidth,
                      clientWidth: document.documentElement.clientWidth,
                      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                      cardsSingleColumn: innerWidth > 560 || getComputedStyle(document.querySelector('.featureGrid')).gridTemplateColumns.split(' ').length === 1,
                      mobileMenuVisible: innerWidth > 860 || document.querySelector('.mobileMenu').getBoundingClientRect().height >= 44,
                      heroHeadingClearOfArtwork: innerWidth <= 860 || document.querySelector('.hero h1').getBoundingClientRect().right <= document.querySelector('.heroArtwork').getBoundingClientRect().left + 0.5,
                      touchTargetViolations: Array.from(document.querySelectorAll('a, button, summary'))
                        .filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && !el.classList.contains('skipLink'); })
                        .map(el => ({label: (el.textContent || '').trim(), width: el.getBoundingClientRect().width, height: el.getBoundingClientRect().height}))
                        .filter(item => item.height < 43.5),
                      overflowElements: Array.from(document.querySelectorAll('body *'))
                        .map(el => ({tag: el.tagName, className: String(el.className), left: el.getBoundingClientRect().left, right: el.getBoundingClientRect().right, width: el.getBoundingClientRect().width}))
                        .filter(item => item.left < -0.5 || item.right > innerWidth + 0.5)
                        .slice(0, 12),
                    })"""
                )
                audit["viewports"][str(width)] = geometry
                page.screenshot(path=OUTPUT / f"landing_{width}.png", full_page=True)

            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(BASE_URL, wait_until="networkidle")
            menu = page.locator(".mobileMenu")
            menu.locator("summary").click()
            audit["mobile_menu"] = {
                "opened": menu.get_attribute("open") is not None,
                "app_link_visible": menu.get_by_role("link", name="Open application").is_visible(),
            }

            tabs_before = len(context.pages)
            menu.get_by_role("link", name="Open application").click()
            page.wait_for_url("**/app")
            iframe = page.get_by_title("NewsLens AI Streamlit application")
            audit["embedded_app"] = {
                "same_tab": len(context.pages) == tabs_before,
                "iframe_title": iframe.get_attribute("title"),
                "iframe_src": iframe.get_attribute("src"),
                "embed_parameter": "embed=true" in (iframe.get_attribute("src") or ""),
                "sandbox": iframe.get_attribute("sandbox"),
                "referrer_policy": iframe.get_attribute("referrerpolicy"),
                "sandbox_is_restricted": set((iframe.get_attribute("sandbox") or "").split())
                == {"allow-downloads", "allow-forms", "allow-popups", "allow-same-origin", "allow-scripts"},
                "supported_placeholder_shape": (
                    (iframe.get_attribute("src") or "").lower()
                    == "https://your-app.streamlit.app/?embed=true"
                ),
                "fallback_same_tab": page.get_by_role(
                    "link", name="Open Streamlit in this tab", exact=True
                ).get_attribute("target") in (None, "", "_self"),
                "fallback_touch_target_height": page.get_by_role(
                    "link", name="Open Streamlit in this tab", exact=True
                ).evaluate("el => el.getBoundingClientRect().height"),
            }
            page.screenshot(path=OUTPUT / "embedded_app_390.png", full_page=False)
            page.set_viewport_size({"width": 1366, "height": 900})
            page.screenshot(path=OUTPUT / "embedded_app_1366.png", full_page=False)

            style_text = (WEB / "app" / "styles.css").read_text(encoding="utf-8")
            required_tokens = (
                "#F3F0E8", "#EAE4D8", "#FAF8F2", "#D8CCBA", "#A89984",
                "#6D5947", "#40352C", "#1A1917", "#090909", "#D4CEC2", "#393631",
            )
            audit["design_tokens"] = {
                token: token in style_text for token in required_tokens
            }
            audit["all_viewports_no_overflow"] = all(
                not item["horizontalOverflow"] for item in audit["viewports"].values()
            )
            audit["all_hero_headings_clear_artwork"] = all(
                item["heroHeadingClearOfArtwork"] for item in audit["viewports"].values()
            )
            audit["all_touch_targets_at_least_44px"] = all(
                not item["touchTargetViolations"] for item in audit["viewports"].values()
            ) and audit["embedded_app"]["fallback_touch_target_height"] >= 43.5
            context.close()
            browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    output_path = OUTPUT / "web_browser_audit.json"
    output_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(audit, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
