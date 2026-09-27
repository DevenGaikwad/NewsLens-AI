# Placement Interview Guide — NewsLens AI

## Thirty-second explanation

NewsLens AI is a Streamlit NLP portfolio project with two independent paths: deterministic extractive summarisation and a public classifier trained only on an original synthetic fact-consistency benchmark. I designed group-safe splits, separate calibration and policy partitions, shortcut baselines, a counterfactual test, exact artifact binding, abstention, explanations, security gates, and deployment evidence. I explicitly avoid claiming that synthetic consistency equals real-world truth detection.

## Key technical decisions

- **Why Logistic Regression?** It matched the best bounded candidate within a declared tolerance, gives fast CPU inference, exposes linear coefficients, and provides a stable calibration score.
- **Why five partitions?** Training, selection, calibration fitting, threshold selection, and final evaluation must not reuse the same evidence.
- **Why group by event?** A consistent and contradicting article describe the same fictional event; separating them would leak paired content.
- **Why Platt calibration?** It maps the raw linear score to an empirically fitted probability and can be stored in a small, inspectable, hash-bound artifact.
- **What do the two displayed probabilities mean?** `Fields agree` corresponds to the synthetic ledger-consistent class; `Fields conflict` corresponds to the synthetic ledger-contradicting class. They measure benchmark-class agreement, not whether real-world reporting is true or fake.
- **What is reference-comparison confidence?** It is the calibrated confidence in the selected synthetic consistency class, not factual certainty.
- **Why abstain?** A confident internal score is unsafe outside the supported paired-ledger format. Missing blocks therefore show `Outside supported comparison scope`, and the UI/PDF/CSV withhold directional values.
- **Why did two unrelated articles appear to score about 87–88%?** Both lacked the required ledger pair and shared the dominant `signal_fact_blocks_unavailable` feature. Controlled tests ruled out caching or class-mapping bugs. The maintenance UI now withholds that out-of-domain number rather than presenting it as credibility.
- **How were shortcuts tested?** Surface-only and metadata-only baselines, fact-block ablation, and a paired account-block counterfactual.
- **How is supply-chain integrity enforced?** SHA-256 manifest checks, calibration binding, pinned dependencies, CI, release scanning, branch protection, and exact-head verification.

## Honest limitations

Perfect locked-test performance belongs to a deliberately structured synthetic task. It does not demonstrate factual reasoning, publisher assessment, multilingual robustness, or open-world misinformation detection. The application should be described as a responsible technical demonstration, not a production fact-checker.
