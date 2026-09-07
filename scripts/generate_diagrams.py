"""Generate original high-resolution engineering diagrams for the academic report."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "diagrams"
OUTPUT.mkdir(parents=True, exist_ok=True)

NAVY = "#40352C"
BLUE = "#6D5947"
CYAN = "#A89984"
TEAL = "#496454"
VIOLET = "#735B48"
AMBER = "#8A693D"
RED = "#813F39"
INK = "#1A1917"
MUTED = "#77736C"
PALE = "#FAF8F2"
WHITE = "#F3F0E8"
LINE = "#D4CEC2"


def canvas(title: str, subtitle: str = ""):
    fig, ax = plt.subplots(figsize=(14, 8), dpi=180)
    fig.patch.set_facecolor(WHITE)
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.035, top=0.975)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.04, 0.96, title, fontsize=22, fontweight="bold", color=NAVY, va="top")
    if subtitle:
        ax.text(0.04, 0.915, subtitle, fontsize=10.5, color=MUTED, va="top")
    ax.plot([0.04, 0.96], [0.89, 0.89], color=CYAN, linewidth=2.5)
    return fig, ax


def wrapped(text: str, width: float, size: float, *, minimum: int = 10) -> str:
    """Wrap diagram copy to an approximate character width derived from its box."""
    if not text:
        return text
    limit = max(minimum, int(width * 118 * (9.0 / max(size, 6.5))))
    return "\n".join(fill(part, width=limit, break_long_words=False) for part in str(text).split("\n"))


def box(ax, x, y, w, h, label, *, color=BLUE, fill=PALE, size=10, detail=None, radius=0.015, lw=1.6):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.008,rounding_size={radius}",
        linewidth=lw, edgecolor=color, facecolor=fill, zorder=2,
    )
    ax.add_patch(patch)
    label_text = wrapped(label, w, size)
    ax.text(
        x + w / 2,
        y + h * (0.64 if detail else 0.50),
        label_text,
        ha="center",
        va="center",
        fontsize=size,
        fontweight="bold",
        color=INK,
        linespacing=1.05,
        zorder=4,
    )
    if detail:
        detail_size = max(6.8, size - 2.2)
        ax.text(
            x + w / 2,
            y + h * 0.25,
            wrapped(detail, w * 0.92, detail_size),
            ha="center",
            va="center",
            fontsize=detail_size,
            color=MUTED,
            linespacing=1.05,
            zorder=4,
        )
    return patch


def arrow(
    ax,
    start,
    end,
    *,
    color=MUTED,
    label=None,
    rad=0.0,
    style="-|>",
    lw=1.6,
    dashed=False,
    label_offset=(0.0, 0.016),
    label_position=0.5,
):
    patch = FancyArrowPatch(
        start, end, arrowstyle=style, mutation_scale=13, linewidth=lw,
        color=color, connectionstyle=f"arc3,rad={rad}", linestyle="--" if dashed else "-",
        shrinkA=1.5, shrinkB=2.5, zorder=1.5, clip_on=False,
    )
    ax.add_patch(patch)
    if label:
        mx = start[0] + (end[0] - start[0]) * label_position
        my = start[1] + (end[1] - start[1]) * label_position
        ax.text(
            mx + label_offset[0],
            my + label_offset[1],
            label,
            fontsize=8,
            color=MUTED,
            ha="center",
            va="bottom",
            bbox={"facecolor": WHITE, "edgecolor": "none", "pad": 1.8},
            zorder=5,
        )


def label_band(ax, x, y, w, text, color=NAVY):
    ax.add_patch(FancyBboxPatch((x, y), w, 0.045, boxstyle="round,pad=0.004,rounding_size=0.008", linewidth=0, facecolor=color))
    ax.text(x + 0.012, y + 0.0225, text, color=WHITE, fontsize=10, fontweight="bold", va="center")


def save(fig, name: str):
    path = OUTPUT / name
    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0.12, facecolor=WHITE, dpi=180)
    path.write_bytes(buffer.getvalue())
    plt.close(fig)
    print(path.name)


def overall_architecture():
    fig, ax = canvas("Figure 4.1 · Overall system architecture", "Implemented six-layer modular architecture; arrows show runtime dependency direction.")
    rows = [
        (0.79, "1 · PRESENTATION", ["Streamlit pages", "Editorial UI system", "Plotly analytics", "Downloads"], CYAN),
        (0.655, "2 · INGESTION", ["Direct text", "Public URL", "TXT / PDF", "Input validation"], BLUE),
        (0.52, "3 · NLP PROCESSING", ["Cleaning", "Sentence split", "Metadata", "Statistics"], TEAL),
        (0.385, "4 · AI", ["Extractive summary", "Optional DistilBART", "TF-IDF + LR", "Local XAI"], VIOLET),
        (0.25, "5 · PERSISTENCE", ["Joblib model", "Model metadata", "SQLite history", "Configuration"], AMBER),
        (0.115, "6 · EVALUATION", ["Classification metrics", "ROUGE", "Error analysis", "Figures / tests"], RED),
    ]
    for y, band, items, color in rows:
        label_band(ax, 0.04, y, 0.15, band, color)
        for index, item in enumerate(items):
            x = 0.22 + index * 0.185
            box(ax, x, y - 0.005, 0.16, 0.056, item, color=color, fill="#FAF8F2", size=8.7)
    for (upper_y, *_), (lower_y, *__) in zip(rows, rows[1:]):
        arrow(ax, (0.50, upper_y - 0.010), (0.50, lower_y + 0.058), color=NAVY, lw=1.7)
    ax.text(0.96, 0.038, "Core mode: local CPU · no paid API", ha="right", fontsize=9, color=TEAL, fontweight="bold")
    save(fig, "01_overall_system_architecture.png")


def end_to_end_flow():
    fig, ax = canvas("Figure 4.2 · End-to-end data flow", "Classifier and summarizer receive the original cleaned article independently.")
    xs = [0.04, 0.19, 0.34]
    names = ["User input", "Validate / extract", "Clean + metadata"]
    details = ["Text · URL · TXT · PDF", "SSRF / type / size / length", "Display text + model text"]
    colors = [CYAN, BLUE, TEAL]
    for x, name, detail, color in zip(xs, names, details, colors):
        box(ax, x, 0.60, 0.125, 0.15, name, color=color, detail=detail, size=9)
    arrow(ax, (0.165, 0.675), (0.19, 0.675))
    arrow(ax, (0.315, 0.675), (0.34, 0.675))
    ax.add_patch(Circle((0.50, 0.675), 0.008, color=NAVY, zorder=3))
    arrow(ax, (0.465, 0.675), (0.492, 0.675))
    ax.text(
        0.505,
        0.835,
        "Cleaned article\nfan-out",
        ha="center",
        va="center",
        fontsize=8.2,
        color=MUTED,
        bbox={"facecolor": WHITE, "edgecolor": LINE, "pad": 3},
        zorder=5,
    )
    box(ax, 0.55, 0.70, 0.17, 0.14, "A · Summarization", color=VIOLET, fill="#EAE4D8", detail="TF-IDF centroid or DistilBART", size=9)
    box(ax, 0.55, 0.47, 0.17, 0.14, "B · Risk classification", color=RED, fill="#F1E2DF", detail="Saved TF-IDF + Logistic Regression", size=9)
    arrow(ax, (0.508, 0.682), (0.55, 0.77))
    arrow(ax, (0.508, 0.668), (0.55, 0.54))
    box(ax, 0.78, 0.58, 0.17, 0.16, "Combined dashboard", color=CYAN, detail="Summary · probability · XAI · timing", size=9)
    arrow(ax, (0.72, 0.77), (0.78, 0.69))
    arrow(ax, (0.72, 0.54), (0.78, 0.63))
    box(ax, 0.58, 0.24, 0.14, 0.11, "SQLite history", color=AMBER, fill="#F1E9DA", detail="hash-based duplicate check", size=8.5)
    box(ax, 0.79, 0.24, 0.14, 0.11, "JSON / PDF", color=TEAL, fill="#E7ECE6", detail="user-triggered export", size=8.5)
    arrow(ax, (0.84, 0.58), (0.66, 0.35))
    arrow(ax, (0.865, 0.58), (0.86, 0.35))
    ax.text(0.50, 0.11, "Failure paths return student-friendly messages; no branch is allowed to crash the page.", ha="center", fontsize=10, color=MUTED)
    save(fig, "02_end_to_end_data_flow.png")


def dfd_level_0():
    fig, ax = canvas("Figure 4.3 · DFD Level 0 (context diagram)", "External entities exchange only the data required by the NewsLens AI system boundary.")
    box(ax, 0.38, 0.37, 0.24, 0.26, "PROCESS 0\nNewsLens AI", color=NAVY, fill="#EAE4D8", size=13, detail="Summarize, classify,\nexplain and store")
    box(ax, 0.05, 0.42, 0.18, 0.15, "User", color=CYAN, detail="article + settings", size=11)
    box(ax, 0.77, 0.65, 0.18, 0.13, "Public news website", color=BLUE, detail="HTML article", size=9)
    box(ax, 0.77, 0.40, 0.18, 0.13, "Saved model files", color=VIOLET, detail="Joblib + metadata", size=9)
    box(ax, 0.77, 0.15, 0.18, 0.13, "Local SQLite", color=AMBER, detail="structured history", size=9)
    arrow(ax, (0.23, 0.52), (0.38, 0.52), label="text / URL / file", label_offset=(0, 0.018))
    arrow(ax, (0.38, 0.45), (0.23, 0.45), label="summary · risk · export", label_offset=(0, -0.035))
    arrow(ax, (0.62, 0.57), (0.77, 0.70), label="HTTP GET", label_offset=(-0.015, 0.022))
    arrow(ax, (0.77, 0.66), (0.62, 0.53), label="HTML", label_offset=(0.020, -0.032))
    arrow(ax, (0.77, 0.47), (0.62, 0.47), label="pipeline", label_offset=(0, 0.018))
    arrow(ax, (0.62, 0.40), (0.77, 0.23), label="insert / query", label_offset=(-0.018, 0.020))
    arrow(ax, (0.77, 0.19), (0.62, 0.37), label="history rows", label_offset=(0.020, -0.032))
    save(fig, "03_dfd_level_0.png")


def dfd_level_1():
    fig, ax = canvas("Figure 4.4 · DFD Level 1", "Decomposition of Process 0 into implemented ingestion, NLP, AI, presentation, and storage processes.")
    steps = [
        (0.04, 0.60, "1.0\nAcquire input", "text / URL / upload", CYAN),
        (0.23, 0.60, "2.0\nValidate + clean", "public URL · ≥40 words", BLUE),
        (0.42, 0.60, "3.0\nSummarize", "method + length", VIOLET),
        (0.42, 0.33, "4.0\nClassify + explain", "probabilities + terms", RED),
        (0.63, 0.47, "5.0\nCompose result", "metrics + disclaimer", TEAL),
        (0.82, 0.47, "6.0\nPersist / export", "SQLite · JSON · PDF", AMBER),
    ]
    for x, y, label, detail, color in steps:
        box(ax, x, y, 0.15, 0.13, label, color=color, detail=detail, size=9)
    arrow(ax, (0.19, 0.665), (0.23, 0.665)); arrow(ax, (0.38, 0.665), (0.42, 0.665))
    arrow(ax, (0.38, 0.62), (0.42, 0.395), label="original cleaned")
    arrow(ax, (0.57, 0.665), (0.63, 0.56)); arrow(ax, (0.57, 0.395), (0.63, 0.50))
    arrow(ax, (0.78, 0.535), (0.82, 0.535))
    box(ax, 0.05, 0.22, 0.15, 0.10, "D1 · Web page", color=BLUE, fill="#FAF8F2", size=8.5)
    box(ax, 0.25, 0.14, 0.15, 0.10, "D2 · Joblib model", color=VIOLET, fill="#EAE4D8", size=8.5)
    box(ax, 0.81, 0.18, 0.16, 0.10, "D3 · analyses table", color=AMBER, fill="#F1E9DA", size=8.5)
    arrow(ax, (0.12, 0.32), (0.10, 0.60), label="HTML", dashed=True)
    arrow(ax, (0.33, 0.24), (0.47, 0.33), label="load once", dashed=True)
    arrow(ax, (0.89, 0.47), (0.89, 0.28), label="CRUD", dashed=True)
    ax.text(0.04, 0.82, "External entity: USER", fontsize=10, fontweight="bold", color=NAVY)
    arrow(ax, (0.13, 0.80), (0.11, 0.73), label="article / settings")
    save(fig, "04_dfd_level_1.png")


def use_case():
    fig, ax = canvas("Figure 4.5 · Use-case diagram", "One primary actor; optional network services are supporting actors rather than trusted decision-makers.")
    # Actor
    ax.add_patch(Circle((0.10, 0.69), 0.035, fill=False, edgecolor=NAVY, linewidth=2))
    ax.plot([0.10, 0.10], [0.655, 0.52], color=NAVY, linewidth=2)
    ax.plot([0.04, 0.16], [0.61, 0.61], color=NAVY, linewidth=2)
    ax.plot([0.10, 0.05], [0.52, 0.43], color=NAVY, linewidth=2)
    ax.plot([0.10, 0.15], [0.52, 0.43], color=NAVY, linewidth=2)
    ax.text(0.10, 0.37, "User", ha="center", fontsize=11, fontweight="bold", color=INK)
    boundary = FancyBboxPatch((0.24, 0.13), 0.58, 0.68, boxstyle="round,pad=0.01,rounding_size=0.02", fill=False, edgecolor=LINE, linewidth=2)
    ax.add_patch(boundary); ax.text(0.27, 0.78, "NewsLens AI boundary", fontsize=10, color=MUTED)
    cases = [
        (0.31, 0.63, "Submit article"), (0.56, 0.63, "Choose summary mode"),
        (0.31, 0.45, "View summary + metadata"), (0.56, 0.45, "Inspect risk + XAI"),
        (0.31, 0.27, "Search/delete history"), (0.56, 0.27, "Download JSON / PDF"),
    ]
    for x, y, text in cases:
        patch = FancyBboxPatch((x, y), 0.19, 0.095, boxstyle="round,pad=0.01,rounding_size=0.05", facecolor="#FAF8F2", edgecolor=CYAN if x < 0.5 else VIOLET, linewidth=1.5)
        ax.add_patch(patch); ax.text(x + 0.095, y + 0.048, text, ha="center", va="center", fontsize=8.5, color=INK)
        arrow(ax, (0.16, 0.61), (x, y + 0.048), style="-", color=LINE, lw=1.0)
    box(ax, 0.87, 0.60, 0.10, 0.10, "News site", color=BLUE, size=8)
    box(ax, 0.87, 0.33, 0.10, 0.10, "Hugging Face", color=TEAL, size=8, detail="first cache only")
    arrow(ax, (0.82, 0.67), (0.87, 0.65), label="URL fetch", dashed=True)
    arrow(ax, (0.75, 0.67), (0.87, 0.38), label="optional model", dashed=True)
    save(fig, "05_use_case_diagram.png")


def activity():
    fig, ax = canvas("Figure 4.6 · Activity diagram", "Control flow includes validation decisions, parallel AI work, duplicate detection, and recovery paths.")
    ax.add_patch(Circle((0.10, 0.76), 0.018, color=NAVY))
    box(ax, 0.17, 0.71, 0.14, 0.10, "Select input method", color=CYAN, size=9)
    arrow(ax, (0.118, 0.76), (0.17, 0.76))
    diamond = Polygon([[0.40, 0.81], [0.47, 0.76], [0.40, 0.71], [0.33, 0.76]], closed=True, facecolor="#F1E9DA", edgecolor=AMBER, linewidth=1.6)
    ax.add_patch(diamond); ax.text(0.40, 0.76, "Valid?", ha="center", va="center", fontsize=8.5, fontweight="bold")
    arrow(ax, (0.31, 0.76), (0.33, 0.76))
    box(ax, 0.54, 0.71, 0.15, 0.10, "Extract + clean", color=BLUE, size=9)
    arrow(ax, (0.47, 0.76), (0.54, 0.76), label="yes")
    box(ax, 0.30, 0.54, 0.20, 0.09, "Show actionable error", color=RED, fill="#F1E2DF", size=9)
    arrow(ax, (0.40, 0.71), (0.40, 0.63), label="no")
    arrow(ax, (0.30, 0.585), (0.10, 0.585), rad=-0.2, label="correct input")
    ax.plot([0.70, 0.97], [0.75, 0.75], color=NAVY, linewidth=5, solid_capstyle="butt", zorder=2)
    arrow(ax, (0.69, 0.76), (0.70, 0.75))
    box(ax, 0.70, 0.56, 0.13, 0.10, "Summarize", color=VIOLET, size=9)
    box(ax, 0.85, 0.56, 0.13, 0.10, "Classify + XAI", color=RED, size=9)
    arrow(ax, (0.765, 0.75), (0.765, 0.66))
    arrow(ax, (0.915, 0.75), (0.915, 0.66))
    ax.plot([0.70, 0.98], [0.47, 0.47], color=NAVY, linewidth=5, solid_capstyle="butt", zorder=2)
    arrow(ax, (0.765, 0.56), (0.765, 0.47))
    arrow(ax, (0.915, 0.56), (0.915, 0.47))
    box(ax, 0.59, 0.31, 0.18, 0.10, "Compose dashboard", color=TEAL, size=9)
    arrow(ax, (0.82, 0.47), (0.68, 0.41))
    diamond2 = Polygon([[0.45, 0.38], [0.52, 0.33], [0.45, 0.28], [0.38, 0.33]], closed=True, facecolor="#F1E9DA", edgecolor=AMBER, linewidth=1.6)
    ax.add_patch(diamond2); ax.text(0.45, 0.33, "Duplicate?", ha="center", va="center", fontsize=8)
    arrow(ax, (0.59, 0.36), (0.52, 0.33))
    box(ax, 0.18, 0.27, 0.15, 0.10, "Insert SQLite row", color=AMBER, size=8.5)
    arrow(ax, (0.38, 0.33), (0.33, 0.32), label="no")
    box(ax, 0.38, 0.14, 0.20, 0.08, "Display existing ID warning", color=AMBER, size=8.5)
    arrow(ax, (0.45, 0.28), (0.48, 0.22), label="yes")
    ax.add_patch(Circle((0.12, 0.18), 0.027, fill=False, edgecolor=NAVY, linewidth=2)); ax.add_patch(Circle((0.12, 0.18), 0.014, color=NAVY))
    arrow(ax, (0.22, 0.27), (0.14, 0.20)); arrow(ax, (0.38, 0.18), (0.15, 0.18))
    save(fig, "06_activity_diagram.png")


def sequence():
    fig, ax = canvas("Figure 4.7 · Sequence diagram", "Synchronous analysis flow; optional model download occurs only on the first abstractive request.")
    participants = [(0.08, "User"), (0.24, "Streamlit UI"), (0.40, "Ingestion"), (0.56, "Summarizer"), (0.72, "Classifier/XAI"), (0.88, "SQLite")]
    for x, name in participants:
        box(ax, x - 0.06, 0.79, 0.12, 0.07, name, color=CYAN if x < 0.3 else BLUE, size=8)
        ax.plot([x, x], [0.18, 0.79], color=LINE, linewidth=1.2, linestyle="--")
    messages = [
        (0.08, 0.24, 0.75, "submit(article, settings)"),
        (0.24, 0.40, 0.68, "validate / extract"),
        (0.40, 0.24, 0.61, "ArticleData or error"),
        (0.24, 0.56, 0.54, "summarize(original cleaned)"),
        (0.24, 0.72, 0.46, "predict(original cleaned)"),
        (0.56, 0.24, 0.38, "summary + metrics"),
        (0.72, 0.24, 0.31, "probabilities + terms"),
        (0.24, 0.88, 0.24, "insert_analysis(hash, result)"),
        (0.88, 0.24, 0.18, "analysis_id, duplicate"),
    ]
    for start, end, y, text in messages:
        offset = 0.012 if end > start else -0.012
        arrow(ax, (start, y), (end + offset, y), label=text, color=NAVY if y > 0.4 else MUTED, lw=1.25)
    ax.text(
        0.64,
        0.575,
        "alt · cached DistilBART\nor extractive fallback",
        fontsize=7.2,
        color=MUTED,
        ha="center",
        va="center",
        bbox={"facecolor": "#EAE4D8", "edgecolor": VIOLET, "pad": 2.5},
        zorder=5,
    )
    save(fig, "07_sequence_diagram.png")


def component():
    fig, ax = canvas("Figure 4.8 · Component/module diagram", "Solid arrows are Python imports/calls; dashed arrows are file or database I/O.")
    clusters = [
        (0.04, 0.59, 0.23, 0.22, "Presentation", ["app.py", "pages/*", "ui/* + src/ui.py"], CYAN),
        (0.34, 0.59, 0.27, 0.22, "Ingestion + NLP", ["article_extractor.py", "file_parser.py", "text_preprocessor.py", "utils.py"], BLUE),
        (0.68, 0.59, 0.27, 0.22, "AI + XAI", ["summarizers + predictor", "calibration.py", "model_diagnostics.py", "explainability.py"], VIOLET),
        (0.15, 0.25, 0.27, 0.22, "Session services", ["database.py + editorial_review.py", "newsroom_analytics.py", "report_exporter.py"], AMBER),
        (0.55, 0.25, 0.31, 0.22, "Offline evidence", ["prepare_dataset.py", "benchmark_models.py", "fixed evaluation artifacts"], RED),
    ]
    for x, y, w, h, title, items, color in clusters:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015", facecolor="#FAF8F2", edgecolor=color, linewidth=2))
        ax.text(x + 0.015, y + h - 0.035, title, fontsize=10, fontweight="bold", color=color)
        for idx, item in enumerate(items):
            ax.text(x + 0.02, y + h - 0.075 - idx * 0.035, f"• {item}", fontsize=8.4, color=INK)
    arrow(ax, (0.27, 0.70), (0.34, 0.70), label="calls")
    arrow(ax, (0.61, 0.70), (0.68, 0.70), label="clean article")
    arrow(ax, (0.17, 0.59), (0.27, 0.47), label="CRUD / export")
    arrow(ax, (0.78, 0.59), (0.34, 0.47), label="result bytes", rad=-0.10)
    arrow(ax, (0.70, 0.47), (0.78, 0.59), label="Joblib + metrics", dashed=True)
    box(ax, 0.05, 0.10, 0.16, 0.08, "analysis_history.db", color=AMBER, size=8)
    box(ax, 0.29, 0.10, 0.16, 0.08, "JSON / PDF", color=TEAL, size=8)
    box(ax, 0.57, 0.10, 0.16, 0.08, "model.joblib", color=VIOLET, size=8)
    box(ax, 0.78, 0.10, 0.16, 0.08, "results / figures", color=RED, size=8)
    arrow(ax, (0.25, 0.25), (0.13, 0.18), dashed=True); arrow(ax, (0.35, 0.25), (0.37, 0.18), dashed=True)
    arrow(ax, (0.66, 0.25), (0.65, 0.18), dashed=True); arrow(ax, (0.78, 0.25), (0.86, 0.18), dashed=True)
    save(fig, "08_component_module_diagram.png")


def training_pipeline():
    fig, ax = canvas(
        "Figure 5.1 · Leakage-controlled benchmarking and calibration",
        "The untouched final test is excluded from fitting, confidence calibration, threshold selection and model choice.",
    )
    top = [
        (0.03, "Verified ISOT CSVs", CYAN),
        (0.17, "Clean + exact dedupe", BLUE),
        (0.31, "Balanced 24k sample", TEAL),
        (0.45, "Near-duplicate screen", AMBER),
    ]
    for x, text, color in top:
        box(ax, x, 0.72, 0.12, 0.10, text, color=color, size=7.9)
    for a, b in zip(top[:-1], top[1:]):
        arrow(ax, (a[0] + 0.12, 0.77), (b[0], 0.77))
    box(ax, 0.62, 0.72, 0.13, 0.10, "Training\n19,200 rows", color=NAVY, size=8.1)
    box(ax, 0.78, 0.72, 0.13, 0.10, "Validation\n1,199 + 1,200", color=VIOLET, size=8.1)
    box(ax, 0.84, 0.53, 0.13, 0.10, "Final test\n2,399 rows", color=RED, fill="#F1E2DF", size=8.1)
    arrow(ax, (0.57, 0.77), (0.62, 0.77), label="fixed split", label_offset=(0, 0.018))
    arrow(ax, (0.57, 0.77), (0.78, 0.77), dashed=True)
    arrow(ax, (0.57, 0.75), (0.84, 0.58), dashed=True)

    models = [(0.15, "Logistic Regression"), (0.36, "Linear SVC"), (0.57, "Multinomial NB")]
    for x, name in models:
        box(ax, x, 0.49, 0.17, 0.10, name, color=VIOLET if "Logistic" in name else BLUE, size=8.1)
        arrow(ax, (0.685, 0.72), (x + 0.085, 0.59))
    box(ax, 0.23, 0.28, 0.24, 0.12, "Predeclared selection rule", color=TEAL, detail="policy macro-F1 tolerance 0.01 · XAI · size · latency", size=8.6)
    for x, _ in models:
        arrow(ax, (x + 0.085, 0.49), (0.35, 0.40))
    arrow(ax, (0.80, 0.72), (0.75, 0.44), label="policy metrics", dashed=True, label_offset=(0.025, 0.0))
    arrow(ax, (0.75, 0.44), (0.47, 0.40), dashed=True)
    box(ax, 0.52, 0.28, 0.20, 0.12, "Production LR retained", color=VIOLET, fill="#EAE4D8", detail="verified Joblib hash unchanged", size=8.6)
    arrow(ax, (0.47, 0.34), (0.52, 0.34))
    box(ax, 0.76, 0.28, 0.20, 0.12, "Platt + review policy", color=AMBER, detail="1,199 calibration · 1,200 policy rows", size=8.4)
    arrow(ax, (0.845, 0.72), (0.86, 0.40), dashed=True)
    arrow(ax, (0.72, 0.34), (0.76, 0.34))
    arrow(ax, (0.905, 0.53), (0.905, 0.40), label="report once", dashed=True, label_offset=(0.045, 0.0))
    ax.text(
        0.04,
        0.10,
        "Controls: 41,994 candidates screened · 17 near-duplicate pairs found · 2 holdout rows quarantined · 0 cross-partition pairs after controls",
        fontsize=8.8,
        color=MUTED,
    )
    ax.text(
        0.04,
        0.06,
        "Outputs: unchanged fake_news_pipeline.joblib · private confidence_calibration.json · benchmark/calibration evidence · figures",
        fontsize=8.8,
        color=MUTED,
    )
    save(fig, "09_ml_training_pipeline.png")


def inference_pipeline():
    fig, ax = canvas("Figure 6.1 · Calibrated editorial inference pipeline", "Scientific invariant: the classifier never receives only the generated summary, and runtime never retrains.")
    box(ax, 0.04, 0.52, 0.16, 0.14, "Validated article", color=CYAN, detail="display-cleaned text + metadata", size=9)
    box(ax, 0.27, 0.52, 0.16, 0.14, "Original cleaned article", color=TEAL, detail="single source for both branches", size=9)
    arrow(ax, (0.20, 0.59), (0.27, 0.59))
    ax.add_patch(Circle((0.49, 0.59), 0.009, color=NAVY, zorder=3))
    arrow(ax, (0.43, 0.59), (0.481, 0.59))
    box(ax, 0.55, 0.68, 0.19, 0.12, "Summary branch", color=VIOLET, detail="extractive or sentence-chunked DistilBART", size=9)
    box(ax, 0.55, 0.38, 0.19, 0.12, "Classification branch", color=RED, detail="text_for_model → TF-IDF → LR", size=9)
    arrow(ax, (0.498, 0.598), (0.55, 0.74))
    arrow(ax, (0.498, 0.582), (0.55, 0.44))
    box(ax, 0.78, 0.68, 0.17, 0.12, "SummaryResult", color=VIOLET, detail="summary · compression · latency", size=8.5)
    box(ax, 0.78, 0.38, 0.17, 0.12, "Native LR score", color=RED, detail="class score · local terms · latency", size=8.5)
    arrow(ax, (0.74, 0.74), (0.78, 0.74)); arrow(ax, (0.74, 0.44), (0.78, 0.44))
    box(ax, 0.48, 0.15, 0.19, 0.13, "Calibration + diagnostics", color=AMBER, detail="Platt mapping · scope/OOV · 0.59 policy", size=8.5)
    box(ax, 0.73, 0.15, 0.22, 0.13, "Editorial result", color=CYAN, fill="#EAE4D8", detail="three outcomes · XAI · review · export", size=8.7)
    arrow(ax, (0.86, 0.68), (0.84, 0.28)); arrow(ax, (0.86, 0.38), (0.60, 0.28))
    arrow(ax, (0.67, 0.215), (0.73, 0.215))
    ax.text(
        0.28,
        0.25,
        "Invariant\nSummary is never classifier input",
        fontsize=8.5,
        color=RED,
        fontweight="bold",
        ha="center",
        va="center",
        bbox={"facecolor": "#F1E2DF", "edgecolor": RED, "pad": 4},
        zorder=5,
    )
    ax.plot([0.40, 0.53], [0.30, 0.53], color=RED, linewidth=1.4, linestyle="--", zorder=1.5)
    ax.text(0.535, 0.545, "×", fontsize=22, color=RED, fontweight="bold", ha="center", va="center", zorder=5)
    save(fig, "10_combined_inference_pipeline.png")


def er_diagram():
    fig, ax = canvas("Figure 4.9 · SQLite ER diagram", "One local table stores structured outputs; original uploaded files and complete article bodies are not persisted.")
    x, y, w, h = 0.12, 0.13, 0.58, 0.68
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012", facecolor="#FAF8F2", edgecolor=NAVY, linewidth=2))
    ax.add_patch(FancyBboxPatch((x, y + h - 0.09), w, 0.09, boxstyle="round,pad=0.006,rounding_size=0.012", facecolor=NAVY, edgecolor=NAVY))
    ax.text(x + 0.02, y + h - 0.045, "analyses", color=WHITE, fontsize=15, fontweight="bold", va="center")
    fields = [
        ("PK", "analysis_id", "INTEGER AUTOINCREMENT"), ("", "timestamp", "TEXT NOT NULL"), ("", "input_type", "TEXT NOT NULL"),
        ("", "source_url / source_domain", "TEXT"), ("", "article_title", "TEXT"), ("UQ", "article_hash", "TEXT NOT NULL UNIQUE"),
        ("", "original_word_count", "INTEGER CHECK ≥ 0"), ("", "summary_method / length", "TEXT NOT NULL"),
        ("", "generated_summary", "TEXT NOT NULL"), ("", "prediction_label / band", "TEXT NOT NULL"),
        ("", "reliable / misleading p", "REAL CHECK 0..1"), ("", "calibrated_confidence", "REAL CHECK 0..1"),
        ("", "review_required / reason", "INTEGER · TEXT"), ("", "review_status / notes", "TEXT · visitor scoped"),
        ("", "sources / assessment", "TEXT · human review"), ("", "coverage / OOV flags", "REAL · INTEGER"),
        ("", "model_version / latency", "TEXT · REAL CHECK ≥ 0"),
    ]
    row_h = (h - 0.11) / len(fields)
    for idx, (key, field, dtype) in enumerate(fields):
        yy = y + h - 0.11 - (idx + 0.5) * row_h
        if idx % 2 == 0:
            ax.add_patch(FancyBboxPatch((x + 0.006, yy - row_h / 2), w - 0.012, row_h, boxstyle="square,pad=0", facecolor="#EAE4D8", edgecolor="none"))
        ax.text(x + 0.018, yy, key, fontsize=7.5, fontweight="bold", color=VIOLET, va="center")
        ax.text(x + 0.075, yy, field, fontsize=8.2, fontweight="bold" if key else "normal", color=INK, va="center")
        ax.text(x + 0.35, yy, dtype, fontsize=7.6, color=MUTED, va="center")
    box(ax, 0.76, 0.62, 0.18, 0.13, "Indexes", color=CYAN, detail="timestamp DESC · prediction_label", size=9)
    box(ax, 0.76, 0.39, 0.18, 0.13, "Duplicate rule", color=AMBER, detail="SHA-256 normalized article hash", size=9)
    box(ax, 0.76, 0.16, 0.18, 0.13, "Privacy boundary", color=TEAL, detail="no upload blob · no full article", size=9)
    arrow(ax, (0.70, 0.67), (0.76, 0.68), dashed=True); arrow(ax, (0.70, 0.47), (0.76, 0.45), dashed=True); arrow(ax, (0.70, 0.25), (0.76, 0.22), dashed=True)
    save(fig, "11_sqlite_er_diagram.png")


def navigation():
    fig, ax = canvas("Figure 9.1 · Streamlit navigation diagram", "app.py uses st.navigation and st.Page so all six sections, direct routes and browser history remain in one tab.")
    box(ax, 0.36, 0.73, 0.28, 0.13, "Native Streamlit router", color=NAVY, fill="#FAF8F2", detail="app.py · st.navigation · st.Page · same tab", size=10)
    pages = [
        (0.03, 0.45, "News Desk", "orientation · methodology · boundary", CYAN),
        (0.28, 0.45, "Analyse Article", "summary · calibrated risk · abstention · XAI", BLUE),
        (0.53, 0.45, "Model Accountability", "benchmark · calibration · metrics · limits", VIOLET),
        (0.78, 0.45, "Dataset Analysis", "quality · plots · leakage controls", TEAL),
        (0.22, 0.16, "Editorial Archive", "review · analytics · drift · session archive", AMBER),
        (0.58, 0.16, "Research & About", "papers · references · ethics", RED),
    ]
    for x, y, name, detail, color in pages:
        box(ax, x, y, 0.19, 0.13, name, color=color, detail=detail, size=8.7)
        arrow(ax, (0.50, 0.73), (x + 0.095, y + 0.13), rad=0.05 if x < 0.4 else -0.05)
    ax.text(0.50, 0.07, "Direct URL · refresh · back/forward · keyboard activation · mobile menu", fontsize=9.5, color=MUTED, ha="center", va="center")
    save(fig, "12_streamlit_navigation_diagram.png")


def deployment():
    fig, ax = canvas("Figure 4.10 · Target public deployment architecture", "Public GitHub repository active; Streamlit and Vercel remain blocked pending a legally redistributable public model.")
    box(ax, 0.04, 0.67, 0.19, 0.13, "Active public GitHub", color=NAVY, detail="code · docs · issues · releases", size=9)
    box(ax, 0.31, 0.67, 0.20, 0.13, "Vercel website", color=CYAN, detail="web/ · Next.js presentation shell", size=9)
    box(ax, 0.59, 0.67, 0.24, 0.13, "Streamlit Community Cloud", color=BLUE, detail="main · app.py · Python 3.12", size=9)
    box(ax, 0.04, 0.35, 0.19, 0.13, "Visitor browser", color=CYAN, detail="responsive landing + /app", size=9)
    box(ax, 0.31, 0.35, 0.20, 0.13, "Responsive iframe", color=TEAL, detail="public URL · ?embed=true", size=9)
    box(ax, 0.59, 0.35, 0.17, 0.13, "Python / ML", color=VIOLET, detail="src · UI · saved model", size=9)
    box(ax, 0.79, 0.35, 0.17, 0.13, "Session SQLite", color=AMBER, detail="temporary · visitor-isolated", size=8.7)
    arrow(ax, (0.23, 0.735), (0.31, 0.735), label="planned web", dashed=True)
    arrow(ax, (0.20, 0.80), (0.63, 0.80), label="planned app", dashed=True, rad=-0.16, label_offset=(0.0, 0.012))
    arrow(ax, (0.135, 0.48), (0.41, 0.48), label="open /app")
    arrow(ax, (0.51, 0.415), (0.59, 0.415), label="embed")
    arrow(ax, (0.76, 0.415), (0.79, 0.415), label="private CRUD")
    box(ax, 0.21, 0.10, 0.24, 0.11, "Optional external access", color=RED, detail="public article URL · DistilBART download", size=8.8)
    box(ax, 0.55, 0.10, 0.28, 0.11, "Privacy + durability boundary", color=TEAL, detail="no upload retention · no permanent cloud history claim", size=8.6)
    arrow(ax, (0.67, 0.35), (0.40, 0.21), label="scoped HTTPS", dashed=True)
    save(fig, "13_deployment_diagram.png")


if __name__ == "__main__":
    overall_architecture()
    end_to_end_flow()
    dfd_level_0()
    dfd_level_1()
    use_case()
    activity()
    sequence()
    component()
    training_pipeline()
    inference_pipeline()
    er_diagram()
    navigation()
    deployment()
