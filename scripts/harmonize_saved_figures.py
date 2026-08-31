"""Harmonise saved chart colours with the NewsLens editorial palette.

This is a deterministic pixel-palette operation, not a chart redraw: geometry,
labels, numeric annotations, and image dimensions remain unchanged. Training
scripts emit the same colours; this helper harmonises the
committed figures when raw datasets are intentionally absent from the package.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "reports" / "figures"

FILES = (
    "average_sentence_length.png",
    "class_distribution.png",
    "confusion_matrix.png",
    "feature_importance.png",
    "missing_values_heatmap.png",
    "ngram_frequency_comparison.png",
    "numerical_feature_correlation.png",
    "research_matrix_preview.png",
    "roc_pr_curves.png",
    "subject_distribution.png",
    "title_length_distribution.png",
    "top_ngrams.png",
    "vocabulary_size_comparison.png",
    "word_count_distribution.png",
)

# Representative source colours emitted by Seaborn and Matplotlib.
SOURCE_COLOURS = np.asarray(
    [
        (21, 214, 162),   # neon green
        (45, 190, 151),   # green variant
        (24, 191, 230),   # cyan
        (66, 189, 216),   # cyan antialias/curve
        (255, 93, 143),   # bright pink
        (235, 113, 151),  # pink variant
        (124, 92, 252),   # violet
        (117, 87, 255),   # violet variant
        (38, 188, 196),   # teal/cyan table accent
        (37, 101, 133),   # blue table accent
    ],
    dtype=np.float32,
)

TARGET_COLOURS = np.asarray(
    [
        (73, 100, 84),    # success-muted
        (73, 100, 84),
        (73, 100, 84),
        (73, 100, 84),
        (129, 63, 57),    # danger-muted
        (129, 63, 57),
        (109, 89, 71),    # editorial-brown
        (109, 89, 71),
        (109, 89, 71),
        (64, 53, 44),     # deep-brown
    ],
    dtype=np.float32,
)

PAPER_HIGHLIGHT = np.asarray((250, 248, 242), dtype=np.float32)
PAPER_SECONDARY = np.asarray((234, 228, 216), dtype=np.float32)
MUTED_TAUPE = np.asarray((168, 153, 132), dtype=np.float32)


def _palette_map(rgb: np.ndarray) -> np.ndarray:
    """Return a warm-palette RGB array with shape and content preserved."""

    original = rgb.astype(np.float32)
    output = original.copy()

    # Warm the achromatic background/grid system without touching dark text.
    chroma = original.max(axis=2) - original.min(axis=2)
    value = original.mean(axis=2)
    neutral = chroma < 13

    near_white = neutral & (value >= 248)
    output[near_white] = PAPER_HIGHLIGHT

    light_grey = neutral & (value >= 220) & (value < 248)
    if np.any(light_grey):
        t = ((value[light_grey] - 220) / 28)[:, None]
        output[light_grey] = PAPER_SECONDARY * (1 - t) + PAPER_HIGHLIGHT * t

    mid_grey = neutral & (value >= 150) & (value < 220)
    if np.any(mid_grey):
        t = ((value[mid_grey] - 150) / 70)[:, None]
        output[mid_grey] = MUTED_TAUPE * (1 - t) + PAPER_SECONDARY * t

    # Map saturated source hues. Projection toward white preserves antialiasing
    # and light/dark variants around the original canonical chart colour.
    flat = original.reshape(-1, 3)
    deltas = flat[:, None, :] - SOURCE_COLOURS[None, :, :]
    distances = np.sqrt(np.sum(deltas * deltas, axis=2))
    nearest = np.argmin(distances, axis=1)
    nearest_distance = distances[np.arange(len(flat)), nearest]
    saturated = chroma.reshape(-1) >= 13
    if not np.any(saturated & (nearest_distance <= 75)):
        return np.clip(output, 0, 255).astype(np.uint8)
    selected = saturated & (nearest_distance <= 155)

    if np.any(selected):
        source = SOURCE_COLOURS[nearest[selected]]
        target = TARGET_COLOURS[nearest[selected]]
        pixels = flat[selected]
        direction = PAPER_HIGHLIGHT[None, :] - source
        denominator = np.sum(direction * direction, axis=1)
        blend = np.sum((pixels - source) * direction, axis=1) / denominator
        blend = np.clip(blend, -0.45, 1.0)[:, None]
        mapped = np.where(
            blend >= 0,
            target * (1 - blend) + PAPER_HIGHLIGHT[None, :] * blend,
            target * (1 + blend),
        )
        output.reshape(-1, 3)[selected] = mapped

    return np.clip(output, 0, 255).astype(np.uint8)


def retheme(path: Path) -> None:
    image = Image.open(path).convert("RGBA")
    rgba = np.asarray(image).copy()
    rgba[:, :, :3] = _palette_map(rgba[:, :, :3])
    result = Image.fromarray(rgba, mode="RGBA")
    save_kwargs: dict[str, object] = {"optimize": True}
    dpi = image.info.get("dpi")
    if dpi:
        save_kwargs["dpi"] = dpi
    result.save(path, **save_kwargs)


def main() -> None:
    for name in FILES:
        path = FIGURES / name
        if not path.exists():
            print(f"skip {name}: missing")
            continue
        size = path.stat().st_size
        retheme(path)
        print(f"{name}: {size:,} -> {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
