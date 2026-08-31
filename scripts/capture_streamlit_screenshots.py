"""Capture genuine Streamlit screenshots for documentation QA.

This is an optional documentation helper, not a runtime dependency. Start the
application first, install Playwright/Chromium, then run this script.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "screenshots"
BASE_URL = os.getenv("NEWSLENS_SCREENSHOT_URL", "http://127.0.0.1:8501")


def ready(page: Page, milliseconds: int = 1800) -> None:
    page.wait_for_timeout(milliseconds)
    page.locator("[data-testid='stAppViewContainer']").wait_for(state="visible", timeout=20_000)


def viewport_shot(page: Page, filename: str, capture_height: int | None = None) -> None:
    """Capture a clean viewport region without cutting through visible content."""

    viewport = page.viewport_size or {"width": 1440, "height": 1000}
    if capture_height is None or capture_height == viewport["height"]:
        page.screenshot(path=str(OUTPUT / filename), full_page=False, animations="disabled")
        return
    if capture_height < viewport["height"]:
        page.screenshot(
            path=str(OUTPUT / filename),
            clip={"x": 0, "y": 0, "width": viewport["width"], "height": capture_height},
            animations="disabled",
        )
        return
    page.set_viewport_size({"width": viewport["width"], "height": capture_height})
    page.wait_for_timeout(900)
    page.screenshot(path=str(OUTPUT / filename), full_page=False, animations="disabled")
    page.set_viewport_size(viewport)
    page.wait_for_timeout(400)


def navigate(page: Page, name: str) -> None:
    page.get_by_role("link", name=name, exact=True).click()
    ready(page)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)


def scroll_element_to_top(page: Page, locator, offset: int = 110) -> None:
    locator.evaluate(
        """(el, offset) => {
            el.scrollIntoView({block: 'start', inline: 'nearest', behavior: 'instant'});
            const main = el.closest('[data-testid="stMain"]') || document.querySelector('[data-testid="stMain"]');
            if (main) main.scrollTop = Math.max(0, main.scrollTop - offset);
        }""",
        offset,
    )
    page.wait_for_timeout(500)


def wait_for_server() -> None:
    for _ in range(60):
        try:
            with urllib.request.urlopen(BASE_URL, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError(f"Streamlit did not start at {BASE_URL}")


def capture() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for existing in OUTPUT.glob("*.png"):
        existing.unlink()
    misleading_sample = (ROOT / "data" / "sample" / "misleading_style_article.txt").read_text(encoding="utf-8")
    review_sample = (ROOT / "data" / "sample" / "uncertain_style_article.txt").read_text(encoding="utf-8")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=os.getenv("NEWSLENS_CHROMIUM_PATH") or None,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--no-proxy-server"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30_000)
        ready(page, 2500)
        viewport_shot(page, "01_home.png", 900)

        navigate(page, "Analyse Article")
        page.get_by_label("Article title (optional)").fill("Viral cure claim — synthetic demonstration")
        page.get_by_label("Full article text").fill(misleading_sample)
        page.get_by_label("Full article text").press("Tab")
        page.wait_for_timeout(1000)
        scroll_element_to_top(page, page.get_by_label("Article title (optional)"), 180)
        viewport_shot(page, "02_analysis_input.png")
        page.get_by_role("button", name="Analyse Article", exact=True).click()
        page.get_by_role("heading", name="Viral cure claim — synthetic demonstration", exact=True).first.wait_for(timeout=30_000)
        scroll_element_to_top(page, page.get_by_text("Editorial risk signal", exact=False).first, 90)
        page.wait_for_timeout(1500)
        viewport_shot(page, "03_summary_and_risk_results.png", 930)
        scroll_element_to_top(page, page.get_by_role("heading", name="Why the linear model leaned this way", exact=True), 90)
        page.wait_for_timeout(800)
        viewport_shot(page, "04_explainability_and_downloads.png", 940)

        navigate(page, "Analyse Article")
        page.get_by_label("Article title (optional)").fill("Developing traffic proposal — synthetic demonstration")
        page.get_by_label("Full article text").fill(review_sample)
        page.get_by_role("button", name="Analyse Article", exact=True).click()
        page.get_by_role(
            "heading", name="Developing traffic proposal — synthetic demonstration", exact=True
        ).first.wait_for(timeout=30_000)
        scroll_element_to_top(page, page.get_by_text("Editorial risk signal", exact=False).first, 90)
        page.wait_for_timeout(1200)
        viewport_shot(page, "05_editorial_review_required.png", 840)

        navigate(page, "Model Accountability")
        viewport_shot(page, "06_model_accountability.png", 925)
        scroll_element_to_top(page, page.get_by_role("heading", name="Three controlled classical candidates", exact=True), 90)
        viewport_shot(page, "07_model_benchmarking.png", 940)
        scroll_element_to_top(page, page.get_by_role("heading", name="Probability reliability and editorial review", exact=True), 90)
        viewport_shot(page, "08_calibration_reliability.png", 1350)
        navigate(page, "Dataset Analysis")
        viewport_shot(page, "09_dataset_analysis.png", 960)
        navigate(page, "Editorial Archive")
        viewport_shot(page, "10_newsroom_analytics.png", 1320)
        scroll_element_to_top(page, page.get_by_role("heading", name="Distribution checks without automatic retraining", exact=True), 90)
        viewport_shot(page, "11_drift_readiness.png")
        scroll_element_to_top(page, page.get_by_role("heading", name="Record evidence and a final assessment", exact=True), 90)
        review_status = page.get_by_role("combobox", name="Review status")
        review_status.click()
        page.keyboard.press("Home")
        for _ in range(3):
            page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        page.get_by_label("Reviewer notes", exact=True).fill(
            "Synthetic demonstration review; evidence remains incomplete."
        )
        page.get_by_label(
            "Supporting-source URLs (one public HTTP(S) URL per line)", exact=True
        ).fill(
            "https://example.com/supporting-source"
        )
        page.get_by_label("Final editorial assessment", exact=True).fill(
            "Further reporting and independent evidence are required before an editorial decision."
        )
        page.get_by_label("Final editorial assessment", exact=True).press("Tab")
        page.wait_for_timeout(900)
        viewport_shot(page, "12_editorial_review_workflow.png", 945)
        navigate(page, "Research & About")
        viewport_shot(page, "13_research_about.png", 945)

        page.set_viewport_size({"width": 390, "height": 844})
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30_000)
        ready(page, 1500)
        viewport_shot(page, "14_home_mobile.png")
        page.goto(f"{BASE_URL}/analyse-article", wait_until="domcontentloaded", timeout=30_000)
        ready(page, 1500)
        viewport_shot(page, "15_analysis_mobile.png")
        browser.close()

    for path in sorted(OUTPUT.glob("*.png")):
        print(path.name, path.stat().st_size)


def main() -> None:
    environment = os.environ.copy()
    environment.setdefault("NEWSLENS_DATABASE_PATH", "/tmp/newslens_screenshot_history.db")
    environment["NEWSLENS_HISTORY_MODE"] = "session"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.address",
            "127.0.0.1",
            "--server.port",
            "8501",
            "--server.headless",
            "true",
        ],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_server()
        capture()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    main()
