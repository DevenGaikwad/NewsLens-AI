"""Run the complete lightweight AI path on all three packaged demonstration articles."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.extractive_summarizer import summarize_extractive  # noqa: E402
from src.fake_news_predictor import load_model, predict_credibility  # noqa: E402
from src.model_diagnostics import assess_input  # noqa: E402
from src.utils import word_count  # noqa: E402


def main() -> None:
    model = load_model()
    rows = []
    for path in sorted((ROOT / "data" / "sample").glob("*_style_article.txt")):
        text = path.read_text(encoding="utf-8")
        summary = summarize_extractive(text, "Short")
        diagnostics = assess_input(text, model)
        prediction = predict_credibility(text, model, diagnostics=diagnostics)
        rows.append(
            {
                "sample_file": path.name,
                "original_words": word_count(text),
                "summary_words": summary.summary_word_count,
                "compression_ratio_pct": summary.compression_ratio_pct,
                "prediction_label": prediction.display_label,
                "reliable_probability": prediction.reliable_probability,
                "misleading_probability": prediction.misleading_probability,
                "calibrated_confidence": prediction.confidence,
                "confidence_band": prediction.confidence_band,
                "calibration_method": prediction.calibration_method,
                "editorial_review_threshold": prediction.editorial_review_threshold,
                "review_required": prediction.review_required,
                "vocabulary_coverage": diagnostics.vocabulary_coverage,
                "oov_rate": diagnostics.out_of_vocabulary_rate,
                "model_version": prediction.model_version,
                "summary": summary.summary,
                "usage_note": "Synthetic demonstration only; not ground-truth evaluation",
            }
        )
    output = ROOT / "reports" / "results" / "packaged_sample_analyses.csv"
    pd.DataFrame(rows).to_csv(output, index=False)
    print(pd.DataFrame(rows).drop(columns=["summary"]).to_string(index=False))


if __name__ == "__main__":
    main()
