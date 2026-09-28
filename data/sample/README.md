# NewsLens AI — Demonstration Data

The articles in this folder are original, synthetic teaching examples. They
were not used for training, selection, calibration, policy tuning, or locked
evaluation. The consistent and contradicting files demonstrate the supported
paired-ledger format; the uncertain file deliberately omits the two fact blocks
to demonstrate abstention. Real-world credibility cannot be established from
these examples or from wording alone.

In **Analyse Article → Paste text**, choose **Fictional demonstration sample**,
then **Load Selected Sample → Analyse Article**:

1. **Fields agree** loads `reliable_style_article.txt` and shows the supported
   reference/account agreement path.
2. **Fields conflict** loads `misleading_style_article.txt` and shows a supported
   multi-field contradiction.
3. **Outside scope** loads `uncertain_style_article.txt`; it has no paired fact
   blocks, so the app requests human review and withholds public probabilities.

These examples are for the declared structured comparison. A single changed
field or ambiguous pair may also require review because the frozen model is
not validated for every natural-language variation. Ordinary external news
cannot be submitted as a real/fake test of this model.
