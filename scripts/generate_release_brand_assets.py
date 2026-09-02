"""Generate original GitHub and README brand assets from current project captures."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "github"
SCREENSHOTS = ROOT / "reports" / "screenshots"

PAPER = "#F3F0E8"
PAPER_2 = "#EAE4D8"
HIGHLIGHT = "#FAF8F2"
BEIGE = "#D8CCBA"
TAUPE = "#A89984"
BROWN = "#6D5947"
DEEP = "#40352C"
CHARCOAL = "#1A1917"
INK = "#090909"
BORDER = "#D4CEC2"

SERIF_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
SERIF = Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
SANS_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
SANS = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def social_preview() -> Path:
    canvas = Image.new("RGB", (1280, 640), PAPER)
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, 1280, 18), fill=INK)
    draw.rectangle((72, 75, 760, 565), fill=HIGHLIGHT, outline=INK, width=3)
    draw.rectangle((72, 75, 760, 124), fill=INK)
    draw.text((96, 89), "THE NEWS INTELLIGENCE DESK", font=font(SANS_BOLD, 18), fill=HIGHLIGHT)
    draw.text((96, 168), "NewsLens AI", font=font(SERIF_BOLD, 70), fill=INK)
    draw.multiline_text(
        (98, 275),
        "Summarization · explainable\nlinguistic credibility-risk analysis",
        font=font(SERIF, 31),
        fill=DEEP,
        spacing=12,
    )
    draw.line((98, 392, 700, 392), fill=BORDER, width=3)
    draw.text((98, 427), "DEVEN GAIKWAD", font=font(SANS_BOLD, 20), fill=BROWN)
    draw.text((98, 468), "Responsible research software · uncertainty stays visible", font=font(SANS, 18), fill=CHARCOAL)

    # Original newspaper-and-lens line motif; no external artwork or data.
    draw.rounded_rectangle((825, 110, 1135, 440), radius=6, fill=PAPER_2, outline=INK, width=5)
    draw.rectangle((858, 148, 1102, 194), fill=DEEP)
    draw.text((877, 159), "NEWS  ·  ANALYSIS", font=font(SANS_BOLD, 15), fill=HIGHLIGHT)
    draw.rectangle((858, 226, 1065, 245), fill=TAUPE)
    draw.rectangle((858, 265, 1102, 278), fill=BEIGE)
    draw.rectangle((858, 302, 1068, 315), fill=BEIGE)
    draw.rectangle((858, 339, 1020, 352), fill=BEIGE)
    draw.ellipse((965, 316, 1190, 541), fill=PAPER, outline=INK, width=12)
    draw.ellipse((996, 347, 1159, 510), outline=BROWN, width=5)
    draw.line((1145, 497, 1215, 568), fill=INK, width=22)
    draw.line((1042, 429, 1082, 467), fill=BROWN, width=11)
    draw.line((1082, 467, 1131, 399), fill=BROWN, width=11)
    draw.text((848, 570), "LANGUAGE · CONTEXT · UNCERTAINTY", font=font(SANS_BOLD, 15), fill=BROWN)

    path = OUTPUT / "newslens-ai-social-preview.png"
    canvas.save(path, optimize=True)
    return path


def screenshot_collage() -> Path:
    entries = [
        ("01_home.png", "News Desk"),
        ("03_summary_and_risk_results.png", "Analyse Article"),
        ("06_model_accountability.png", "Model Accountability"),
        ("09_dataset_analysis.png", "Dataset Analysis"),
        ("10_newsroom_analytics.png", "Editorial Archive"),
        ("13_research_about.png", "Research & About"),
        ("14_home_mobile.png", "Mobile News Desk"),
    ]
    missing = [name for name, _ in entries if not (SCREENSHOTS / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing current screenshots: {', '.join(missing)}")

    canvas = Image.new("RGB", (1800, 1620), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1800, 14), fill=INK)
    draw.text((90, 54), "NewsLens AI · Current interface", font=font(SERIF_BOLD, 48), fill=INK)
    draw.text(
        (92, 118),
        "Six product areas and a mobile view · warm editorial newsroom design",
        font=font(SANS, 21),
        fill=BROWN,
    )

    card_w, card_h = 520, 405
    positions = [
        (90, 190), (640, 190), (1190, 190),
        (90, 630), (640, 630), (1190, 630),
        (640, 1070),
    ]
    for (name, label), (x, y) in zip(entries, positions, strict=True):
        height = 460 if "mobile" in name else card_h
        draw.rectangle((x, y, x + card_w, y + height), fill=HIGHLIGHT, outline=INK, width=2)
        draw.rectangle((x, y, x + card_w, y + 52), fill=DEEP)
        draw.text((x + 20, y + 14), label, font=font(SANS_BOLD, 18), fill=HIGHLIGHT)
        source = Image.open(SCREENSHOTS / name).convert("RGB")
        available = (card_w - 28, height - 78)
        fitted = ImageOps.contain(source, available, Image.Resampling.LANCZOS)
        px = x + (card_w - fitted.width) // 2
        py = y + 64 + (available[1] - fitted.height) // 2
        draw.rectangle((px - 1, py - 1, px + fitted.width, py + fitted.height), outline=BORDER, width=1)
        canvas.paste(fitted, (px, py))

    draw.text((90, 1571), "Designed and developed by Deven Gaikwad", font=font(SANS_BOLD, 17), fill=CHARCOAL)
    draw.text((1710, 1571), "© 2026", font=font(SANS, 16), fill=BROWN, anchor="ra")
    path = OUTPUT / "newslens-ai-interface-collage.png"
    canvas.save(path, optimize=True)
    return path


def place_capture(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    filename: str,
    label: str,
    box: tuple[int, int, int, int],
) -> None:
    """Place one uncropped interface capture inside a labelled editorial card."""

    source_path = SCREENSHOTS / filename
    if not source_path.is_file():
        raise FileNotFoundError(f"Missing current screenshot: {filename}")
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=HIGHLIGHT, outline=INK, width=2)
    draw.rectangle((x0, y0, x1, y0 + 54), fill=DEEP)
    draw.text((x0 + 20, y0 + 15), label, font=font(SANS_BOLD, 18), fill=HIGHLIGHT)
    with Image.open(source_path) as opened:
        source = opened.convert("RGB")
        available = (x1 - x0 - 30, y1 - y0 - 84)
        fitted = ImageOps.contain(source, available, Image.Resampling.LANCZOS)
    px = x0 + (x1 - x0 - fitted.width) // 2
    py = y0 + 68 + (available[1] - fitted.height) // 2
    draw.rectangle((px - 1, py - 1, px + fitted.width, py + fitted.height), outline=BORDER, width=1)
    canvas.paste(fitted, (px, py))


def two_capture_feature(
    filename: str,
    title: str,
    subtitle: str,
    left: tuple[str, str],
    right: tuple[str, str],
) -> Path:
    canvas = Image.new("RGB", (1600, 1000), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1600, 14), fill=INK)
    draw.text((76, 52), title, font=font(SERIF_BOLD, 48), fill=INK)
    draw.text((78, 116), subtitle, font=font(SANS, 20), fill=BROWN)
    place_capture(canvas, draw, left[0], left[1], (76, 178, 788, 915))
    place_capture(canvas, draw, right[0], right[1], (812, 178, 1524, 915))
    draw.text((78, 952), "NewsLens AI · dataset-relative signals · human authority retained", font=font(SANS_BOLD, 16), fill=CHARCOAL)
    path = OUTPUT / filename
    canvas.save(path, optimize=True)
    return path


def system_architecture() -> Path:
    canvas = Image.new("RGB", (1600, 980), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1600, 14), fill=INK)
    draw.text((76, 52), "NewsLens AI · system architecture", font=font(SERIF_BOLD, 48), fill=INK)
    draw.text(
        (78, 116),
        "The Streamlit application remains the functional product; training and benchmarking stay offline.",
        font=font(SANS, 20),
        fill=BROWN,
    )

    box_font = font(SERIF_BOLD, 23)
    note_font = font(SANS, 15)
    label_font = font(SANS_BOLD, 14)

    def box(bounds: tuple[int, int, int, int], number: str, title: str, note: str, fill: str = HIGHLIGHT) -> None:
        x0, y0, x1, y1 = bounds
        draw.rectangle(bounds, fill=fill, outline=INK, width=2)
        draw.text((x0 + 18, y0 + 16), number, font=label_font, fill=BROWN)
        draw.text((x0 + 18, y0 + 48), title, font=box_font, fill=INK)
        draw.multiline_text((x0 + 18, y0 + 86), note, font=note_font, fill=CHARCOAL, spacing=6)

    def arrow(start: tuple[int, int], end: tuple[int, int]) -> None:
        draw.line((*start, *end), fill=BROWN, width=4)
        ex, ey = end
        sx, sy = start
        if abs(ex - sx) >= abs(ey - sy):
            direction = 1 if ex > sx else -1
            points = [(ex, ey), (ex - 14 * direction, ey - 8), (ex - 14 * direction, ey + 8)]
        else:
            direction = 1 if ey > sy else -1
            points = [(ex, ey), (ex - 8, ey - 14 * direction), (ex + 8, ey - 14 * direction)]
        draw.polygon(points, fill=BROWN)

    boxes = [
        ((76, 205, 356, 355), "01 · INPUT", "Streamlit newsroom", "Text · URL · TXT · PDF"),
        ((420, 205, 700, 355), "02 · INGEST", "Validated article", "Extraction · cleaning\nquality and scope checks"),
        ((764, 205, 1044, 355), "03 · NLP", "Independent paths", "Extractive summary\nTF-IDF vectorisation"),
        ((1108, 205, 1524, 355), "04 · INFERENCE", "Saved LR pipeline", "No runtime retraining\nlocal coefficient influence"),
        ((1108, 455, 1524, 620), "05 · CONFIDENCE", "Private calibration", "Platt mapping · 0.59 policy\nresponsible abstention"),
        ((764, 455, 1044, 620), "06 · DECISION", "Editorial signal", "Three cautious outcomes\nvisible limitations"),
        ((420, 455, 700, 620), "07 · HUMAN", "Review workflow", "Status · notes · sources\nfinal assessment"),
        ((76, 455, 356, 620), "08 · SESSION", "Scoped archive", "SQLite isolation · exports\nprivacy-safe aggregates"),
    ]
    for bounds, number, title, note in boxes:
        box(bounds, number, title, note)

    arrow((356, 280), (420, 280))
    arrow((700, 280), (764, 280))
    arrow((1044, 280), (1108, 280))
    arrow((1316, 355), (1316, 455))
    arrow((1108, 538), (1044, 538))
    arrow((764, 538), (700, 538))
    arrow((420, 538), (356, 538))

    draw.rectangle((76, 705, 1524, 867), fill=PAPER_2, outline=INK, width=2)
    draw.text((98, 728), "OFFLINE EVIDENCE PIPELINE", font=label_font, fill=BROWN)
    draw.text((98, 765), "Licensed data → leakage controls → three-model benchmark → calibration fitting → fixed artefacts", font=box_font, fill=INK)
    draw.text(
        (98, 814),
        "GitHub is the active canonical release history; Streamlit and Vercel remain blocked pending a legally redistributable public model.",
        font=note_font,
        fill=CHARCOAL,
    )
    draw.text((76, 925), "Warm editorial interface · same-tab Streamlit navigation · no automatic moderation", font=font(SANS_BOLD, 16), fill=CHARCOAL)
    path = OUTPUT / "system-architecture.png"
    canvas.save(path, optimize=True)
    return path


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paths = (
        social_preview(),
        screenshot_collage(),
        system_architecture(),
        two_capture_feature(
            "model-benchmarking.png",
            "Controlled model benchmarking",
            "Three classical candidates, identical leakage-controlled partitions, one unchanged production artefact.",
            ("07_model_benchmarking.png", "Candidate comparison"),
            ("08_calibration_reliability.png", "Calibration and review policy"),
        ),
        two_capture_feature(
            "editorial-review.png",
            "Human editorial review",
            "Calibrated abstention and the final human assessment remain deliberately separate.",
            ("05_editorial_review_required.png", "Responsible abstention"),
            ("12_editorial_review_workflow.png", "Evidence and assessment"),
        ),
        two_capture_feature(
            "newsroom-analytics.png",
            "Newsroom analytics and drift readiness",
            "Visitor-scoped aggregates support monitoring without exporting article text, notes, URLs, or identifiers.",
            ("10_newsroom_analytics.png", "Privacy-safe aggregates"),
            ("11_drift_readiness.png", "Distribution checks"),
        ),
    )
    for path in paths:
        with Image.open(path) as image:
            print(f"{path.relative_to(ROOT)}: {image.width}x{image.height}, {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
