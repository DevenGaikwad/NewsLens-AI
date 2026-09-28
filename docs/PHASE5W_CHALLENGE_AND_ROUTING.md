# Phase 5W — Reference-comparison challenge and review routing

This is an exploratory check of the public **synthetic Reference comparison**
task. It is not a real-world fake-news evaluation. The accepted locked final
test and its training, model-validation, calibration, and policy partitions
were not rerun or used for this investigation.

## Sealed challenge

`scripts/phase5w_challenge.py` authors 60 new fictional inputs across eight
fictional events: 22 expected agreements, 22 conflicts, and 16 required-review
cases. The categories cover exact and paraphrased agreement, single factual
changes, negation, field order, long distracting prose, missing and repeated
fields, malformed headings, and ordinary prose. The case text and expectations
were fixed before the first model run. Canonical case-set SHA-256:
`e3eebcb355278b6615bba474ae17e5b7a8b91c255ec0a1eb18d5b8aeb2ebb95e`.
No challenge case was used to fit the model or calibration or select a new
threshold. Cases share eight events, so they are correlated and cannot be
treated as 60 independent estimates of deployment performance.

## Observed frozen-model weakness

The unchanged model classified all 44 structured challenge cases as agreement.
For the 22 agreement / 22 conflict labels, its confusion matrix (rows and
columns ordered agreement, conflict) was `[[22, 0], [22, 0]]`; class precision
was `0.500 / 0.000`, recall `1.000 / 0.000`, balanced accuracy `0.500`, macro-F1
`0.333`, false-positive rate `0`, and false-negative rate `1.000`. Brier score
was `0.4688` and ten-bin ECE `0.4792` on these 44 unfamiliar structured cases.
The eight exact agreement-to-single-change counterfactual pairs had a `0/8`
class-flip rate. In representative cases a single visible
quantity or status mismatch had a conflict probability near `2%` while the
feature explanation did show a mismatch token. This is a real limitation in
the supported task; the accepted in-distribution locked-test score does not
cover this variation.

The three existing packaged samples remain useful: the complete matching pair
receives agreement, the deliberately multi-field contradictory pair receives
conflict, and ordinary prose without both blocks receives review with public
probabilities withheld. The old mid-80% example shown for ordinary prose was
from an earlier/stale display of internal numbers. The current source does not
make those numbers a general-news truth estimate.

## Conservative runtime correction

The model, dataset, calibration, and binding are unchanged. Input diagnostics
now reject incomplete or repeated comparison fields/headings. When the model
would automatically report agreement despite a visible field difference, the
runtime requires human review and withholds directional scores in the UI, PDF,
and archive CSV. Ordinary prose still follows the out-of-scope review path.
The JSON export preserves existing diagnostic values and identifies withheld
reporting through `score_reporting_status`; it must not be read as a public
probability claim for an unsupported input.

On the unchanged sealed cases, all 16 expected-review cases route to review.
Only 14 of the 44 structured cases (`31.8%`) receive an automatic result; all
14 are agreement cases. Their `14/14` covered accuracy is not evidence of
conflict discrimination. Brier/ECE for the covered subset are not reported
because it contains only one class. The raw model's challenge confusion matrix
and counterfactual weakness remain unchanged. Median local inference time was
about `4.8 ms`; model and calibration files remain `161,709` and `728` bytes.
The machine-readable [before](../reports/results/phase5w_challenge_before_guard.json)
and [after](../reports/results/phase5w_challenge.json) reports retain per-case
review reasons, scope decisions, and leading feature contributions. The before
report includes internal diagnostic probabilities for unsupported cases; the
after report records public probabilities only where applicable.

## Model and data decision

This challenge supplies a reason to investigate a future, separately versioned
synthetic benchmark with single-field and semantic variation. It does not by
itself supply a validated replacement model. No new dataset or model was
accepted: the current challenge has already exposed the weakness, and a
candidate would require independent development partitions, an untouched new
holdout, calibration and abstention validation, reproducible hashes, and a
separate protected release. More rows or more extreme probabilities alone
would not pass that gate. The completed general-news licensing and task-fit
audit still does not support a separate real/fake classifier, so none was
trained or deployed.

For a faculty demonstration, use the three packaged fictional samples described
in [`data/sample/README.md`](../data/sample/README.md). A single-field change
may deliberately receive review rather than an automatic direction. Human
verification against independent sources remains necessary for any real article.
