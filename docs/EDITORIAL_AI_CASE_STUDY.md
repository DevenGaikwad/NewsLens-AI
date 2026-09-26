# Editorial AI Case Study: From Blocked Artifact to Synthetic-Only System

## Problem

The original demonstration depended on a private classifier whose training-data redistribution position did not support public deployment. Publishing source without a working model would create a misleading portfolio artifact; publishing the private artifact would violate the project's evidence and rights policy.

## Intervention

NewsLens AI introduced an independently authored fictional benchmark of 24,000 articles / 12,000 paired events. Each article exposes a Reference note and Article account. Consistent examples repeat the authored facts; contradicting examples alter one or more fields. Event-grouped partitions prevent paired variants from crossing training and evaluation boundaries.

Three candidates were compared on model validation. A compact Logistic Regression pipeline was retained, Platt calibration was fitted on a separate partition, and the review threshold was selected on another partition. The final test remained locked until all decisions were fixed.

## Results

The locked test achieved 1.0 accuracy, balanced accuracy, and macro F1 with a `[[600, 0], [0, 600]]` confusion matrix. Brier score was 0.000001497 and ECE 0.000742. Surface text and fact-block ablation remained at chance, metadata was near chance, and swapping only Article account values flipped every paired prediction.

## Product integration

The public model and calibration are hash-bound. Missing structured blocks force human review. Deterministic summarisation remains separate from classification. The app preserves explanations, exports, privacy-safe session history, responsive presentation, and honest limitations without an external checkpoint or paid API.

## Lesson

The central engineering achievement is not a claim of universal fake-news detection. It is a traceable replacement of an unpublishable dependency with a bounded, reproducible, original, deployable system whose success criteria match its declared task.
