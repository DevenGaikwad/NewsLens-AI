# Phase 5X candidate gate (fixed before confirmation evaluation)

The Phase 5W 60-case set is diagnostic and may be used to explain the failure; it is **not** a final acceptance set. The separate Phase 5X set was authored and sealed before candidate fitting/evaluation: 60 cases from 12 new fictional event groups, with 24 agreements, 24 conflicts, and 12 review cases. Its canonical case SHA-256 is `645332dc171bae21f3881b28d244e4e890416801d02b8ae5742c0413d9f261a3`; source and counts are fixed in `reports/results/phase5x_confirmation_seal.json`. No confirmation row may enter training, validation, calibration, or threshold selection.

## Candidate and partitions

Try one lightweight feature-design candidate trained on the existing v1.0.0 **training** partition. It may add label-independent normalized field-comparison features to the TF-IDF representation; it may not replace the dataset, consult private material, or fit on the Phase 5W or Phase 5X challenges. Use the existing **model_validation** partition for selection, **calibration** partition for Platt fitting, and **abstention_policy** partition for the review threshold. The original **final_test** is read only after the candidate clears the independent gate and release policy is frozen. All five original partitions remain grouped by fictional event.

The candidate must keep the PR #52 ambiguity and contradiction guard until the full release checks support an explicit replacement. Report raw model scores separately from selective public outcomes. The model's numerical confidence concerns only comparison with its fictional reference, never real-world truth.

## Acceptance thresholds

All of the following must pass on the untouched Phase 5X confirmation set in one evaluation:

| Dimension | Required result |
|---|---|
| Raw structured classification (48 cases) | Agreement recall ≥ 0.90; conflict recall ≥ 0.90; balanced accuracy ≥ 0.90; macro F1 ≥ 0.90. |
| Probability quality across both structured classes | Brier score ≤ 0.10 and ten-bin ECE ≤ 0.10. Small-sample estimates are exploratory, not population guarantees. |
| Selective automatic routing | Coverage ≥ 0.80 of the 48 structured cases; automatic precision ≥ 0.95 for each class with nonzero class coverage. |
| Exact-to-single-field counterfactuals | Prediction flips in at least 11 of 12 fictional event pairs. |
| Review and unsupported prose | 12/12 expected-review cases routed to review, all public directional scores withheld; every ordinary-prose case withheld. |
| Operational bounds | Median single-item inference ≤ 15 ms on this environment; model package ≤ 1 MiB; no paid runtime service or private dataset/artifact. |
| In-distribution model validation | Balanced accuracy and macro F1 each ≥ 0.99 before confirmation; calibrated Brier ≤ 0.01 on the separate abstention-policy partition. |

If a criterion fails, do not publish a replacement model or calibration. Record the failure and retain the v1.0.0 package and PR #52 guard. A further development cycle or corpus expansion requires separate evidence; no holdout-driven tuning is allowed. If every criterion passes, freeze the candidate and evaluate the original locked final test once for release evidence, then verify model-calibration hash binding, artifact reproducibility, package rights, runtime regression, protected CI/CodeQL, and public-release gates before any merge. A pass on this synthetic set still cannot establish general real/fake-news accuracy.

## One-time result and disposition

The original **training** rows contain 9,000 zero-mismatch consistent articles and 9,000 contradicting articles with **two or more** mismatches (2: 2,390; 3: 3,013; 4 or more: 3,597). The frozen TF-IDF vocabulary has `signal_mismatch_count_0` and field-specific mismatch terms, but no `signal_mismatch_count_1`. In an unfamiliar one-field change, many learned field-match features can outweigh the mismatch. This is direct feature/training-distribution evidence; it does not establish paired-event leakage. The earlier private classifier supplies no lawful public artifact or valid comparison for this task. Publisher, topic, and style shortcuts are plausible for an unrelated real/fake corpus, but we make no claim about its actual behavior.

One experimental linear pipeline added a label-independent `rel_any_mismatch` token and an explicit equivalence for simple zero-to-ninety-nine quantity words and digits. It was fitted only on the original 18,000 training rows; Platt scaling used the 1,200 calibration rows and the 1,200 abstention-policy rows selected a 0.50 threshold. No new dataset rows were generated and no original locked-test decision was re-used. The candidate was evaluated once on the sealed confirmation cases, after the gate above was written.

| Gate evidence | Candidate result | Decision |
|---|---:|---|
| Model-validation balanced accuracy / macro F1 | 1.000 / 1.000 | Pass |
| Abstention-policy Brier | 0.000001921 | Pass |
| Confirmation raw matrix (actual agree/conflict rows) | `[[24, 0], [0, 24]]` | Pass |
| Agreement / conflict recall; balanced accuracy; macro F1 | 1.000 / 1.000; 1.000; 1.000 | Pass |
| Confirmation Brier / ten-bin ECE | 0.000000387 / 0.000229 | Pass on this small set |
| Exact-to-single-field class flips | 12/12 | Pass |
| Expected-review routing / score withholding | 12/12 / 12/12 | Pass |
| Automatic structured coverage | **36/48 = 75%**, required **≥80%** | **Fail** |
| Automatic precision, each represented class | 1.000 | Pass, conditional on coverage |
| Median inference / package size | 4.6 ms / 161,610 bytes | Pass |

The existing PR #52 guard withheld a directional result on twelve numeric-paraphrase agreements because its literal-field comparison saw a visible difference while the experimental model predicted agreement. The guarded path is safer than silently overriding the review decision. The predeclared coverage gate therefore **rejects** the candidate despite its raw 48/48 matrix. The confirmation cases have correlated variants within 12 fictional events and are too small to establish generalisation or reliable population calibration. There was no holdout-driven change, second candidate cycle, dataset expansion, new public model, new calibration, or production routing change. The accepted v1.0.0 artifacts and conservative guard remain authoritative. The final source tree retains the sealed result but excludes the rejected candidate's experimental fitting and feature code. Machine-readable details: [`reports/results/phase5x_candidate_study.json`](../reports/results/phase5x_candidate_study.json).
