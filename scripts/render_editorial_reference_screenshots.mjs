/**
 * Render deterministic editorial-layout reference captures.
 *
 * This QA helper imports the exact CSS string from ui/theme.py and renders the
 * same component class names in Chromium. It is useful when the Python package
 * mirror is unavailable. The canonical end-to-end capture remains
 * capture_streamlit_screenshots.py and should be preferred in an installed
 * project environment.
 *
 * Environment:
 *   NEWSLENS_CHROMIUM_PATH=/path/to/chromium
 *   NODE_PATH=/path/containing/playwright/node_modules
 */

import fs from "node:fs";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";


const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(SCRIPT_DIR, "..");
// Static layouts are non-canonical visual references. Genuine product
// screenshots are captured from the running Streamlit application.
const OUTPUT = path.join(ROOT, "reports", "reference_screenshots");
const HTML_OUTPUT = path.join(ROOT, "reports", "html_previews");
const RESULTS = path.join(ROOT, "reports", "results");
const CHROMIUM_PATH = process.env.NEWSLENS_CHROMIUM_PATH;
const HTML_ONLY = process.argv.includes("--emit-html-only");
const CAPTURE_DATE = new Intl.DateTimeFormat("en-GB", {
  day: "2-digit",
  month: "short",
  year: "numeric",
  timeZone: "Asia/Kolkata",
}).format(new Date());
const require = createRequire(import.meta.url);
const { chromium } = HTML_ONLY ? { chromium: null } : require("playwright");

if (!HTML_ONLY && (!CHROMIUM_PATH || !fs.existsSync(CHROMIUM_PATH))) {
  throw new Error("Set NEWSLENS_CHROMIUM_PATH to a working Chromium executable.");
}

const read = (relative) => fs.readFileSync(path.join(ROOT, relative), "utf8");
const json = (relative) => JSON.parse(read(relative));
const esc = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

function dataUri(relative) {
  const target = path.join(ROOT, relative);
  const extension = path.extname(target).toLowerCase();
  const mime = {
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
  }[extension];
  return `data:${mime};base64,${fs.readFileSync(target).toString("base64")}`;
}

const themeSource = read("ui/theme.py");
const themeMatch = themeSource.match(/GLOBAL_CSS\s*=\s*"""([\s\S]*?)"""/);
if (!themeMatch) throw new Error("Could not extract GLOBAL_CSS from ui/theme.py.");
const exactTheme = themeMatch[1];

const metrics = json("reports/results/model_metrics.json");
const profile = json("reports/results/dataset_profile.json");
const metadata = json("models/model_metadata.json");
const heroArt = dataUri("assets/editorial_masthead.svg");
const logo = dataUri("assets/logo.svg");

const previewCss = `
<style>
* { box-sizing: border-box; }
html, body { margin: 0; min-height: 100%; }
body { overflow-x: hidden; }
main { display: block; }
.preview-columns {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.preview-columns.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.preview-columns.verdict {
  grid-template-columns: minmax(0, .88fr) minmax(0, 1.22fr);
}
.preview-controls {
  display: grid;
  gap: 1rem 1.4rem;
  grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr);
  margin-bottom: 1.2rem;
}
.preview-field { min-width: 0; }
.preview-field > label {
  color: var(--charcoal);
  display: block;
  font-size: .8rem;
  font-weight: 700;
  margin-bottom: .42rem;
}
.preview-input,
.preview-select,
.preview-textarea {
  background: var(--paper-highlight);
  border: 1px solid var(--border-light);
  border-radius: 2px;
  color: var(--charcoal);
  font-family: var(--sans);
  font-size: .82rem;
  padding: .72rem .78rem;
  width: 100%;
}
.preview-textarea {
  height: 225px;
  line-height: 1.55;
  overflow: auto;
  resize: none;
}
.preview-segments {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: .35rem;
}
.preview-segment {
  background: var(--paper-highlight);
  border: 1px solid var(--border-light);
  color: var(--deep-brown);
  font-size: .72rem;
  font-weight: 700;
  padding: .58rem .72rem;
}
.preview-segment.active {
  background: var(--ink-black);
  border-color: var(--ink-black);
  color: var(--paper-highlight);
}
.preview-primary {
  background: var(--ink-black);
  border: 1px solid var(--ink-black);
  border-radius: 2px;
  color: var(--paper-highlight);
  display: block;
  font-family: var(--sans);
  font-size: .8rem;
  font-weight: 750;
  margin-top: .85rem;
  min-height: 46px;
  padding: .75rem 1rem;
  text-align: center;
  width: 100%;
}
.preview-chart {
  background: var(--paper-highlight);
  border: 1px solid var(--border-light);
  min-width: 0;
  padding: .35rem;
}
.preview-chart img {
  display: block;
  height: 300px;
  object-fit: contain;
  width: 100%;
}
.preview-caption {
  color: var(--soft-grey);
  font-size: .72rem;
  line-height: 1.5;
  margin: .5rem .15rem 0;
}
.probability-bar {
  background: var(--paper-secondary);
  border: 1px solid var(--border-light);
  height: 12px;
  margin-top: 1rem;
  overflow: hidden;
}
.probability-bar span {
  background: var(--danger-muted);
  display: block;
  height: 100%;
  width: 78%;
}
.preview-table-wrap {
  background: var(--paper-highlight);
  border: 1px solid var(--border-light);
  overflow-x: auto;
}
.preview-table {
  border-collapse: collapse;
  font-size: .72rem;
  min-width: 720px;
  width: 100%;
}
.preview-table th,
.preview-table td {
  border-bottom: 1px solid var(--border-light);
  padding: .62rem .7rem;
  text-align: left;
  vertical-align: top;
}
.preview-table th {
  color: var(--editorial-brown);
  font-family: var(--mono);
  font-size: .61rem;
  letter-spacing: .06em;
  text-transform: uppercase;
}
.preview-pair {
  border-top: 1px solid var(--border-dark);
  padding: .9rem 0;
}
.preview-pair strong {
  display: block;
  font-family: var(--serif);
  font-size: 1.05rem;
}
.preview-pair span {
  color: var(--soft-grey);
  font-size: .78rem;
}
@media (max-width: 900px) {
  .preview-columns,
  .preview-columns.three,
  .preview-columns.verdict,
  .preview-controls {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 560px) {
  .preview-chart img { height: 220px; }
  .preview-textarea { height: 190px; }
}
</style>`;

const pages = [
  ["home", "./", "News Desk"],
  ["analyse", "./Analyse_Article", "Analyse Article"],
  ["performance", "./Model_Performance", "Model Accountability"],
  ["eda", "./Dataset_EDA", "Dataset Analysis"],
  ["history", "./Analysis_History", "Editorial Archive"],
  ["about", "./Research_About", "Research & About"],
];

function navigation(active) {
  const links = pages
    .map(([key, href, label]) => {
      const current = key === active ? ' aria-current="page"' : "";
      const klass = key === "analyse" ? ' class="nl-nav-cta"' : "";
      return `<a href="${href}"${klass}${current}>${label}</a>`;
    })
    .join("");
  return `
<header class="nl-masthead">
  <a class="nl-brand" href="./"><img src="${logo}" alt="" aria-hidden="true"><span>NewsLens AI</span></a>
  <div class="nl-descriptor">Editorial Credibility-Risk System</div>
</header>
<nav class="nl-nav" aria-label="Primary navigation">${links}</nav>`;
}

function pageHeader(eyebrow, title, description) {
  return `
<header class="page-hero">
  <div><div class="eyebrow">${esc(eyebrow)}</div><h1>${esc(title).replaceAll("\n", "<br>")}</h1></div>
  <p>${esc(description)}</p>
</header>`;
}

function strip(items) {
  return `<div class="editorial-strip">${items.map(esc).join(" ◆ ")}</div>`;
}

function section(kicker, title, body = "") {
  return `
<section class="section-heading">
  <div><div class="section-kicker">${esc(kicker)}</div><h2>${esc(title)}</h2></div>
  <p>${esc(body)}</p>
</section>`;
}

function metricsStrip(items) {
  return `<div class="metric-strip">${items
    .map(
      ([label, value, note]) => `
  <div class="metric-item">
    <div class="metric-label">${esc(label)}</div>
    <div class="metric-value">${esc(value)}</div>
    <div class="metric-note">${esc(note)}</div>
  </div>`,
    )
    .join("")}</div>`;
}

function card(label, title, body) {
  return `<article class="editorial-card"><div class="technical-label">${esc(label)}</div><h3>${esc(title)}</h3><p>${esc(body)}</p></article>`;
}

function footer(left, right) {
  return `<footer class="nl-footer"><span>${esc(left)}</span><span>${esc(right)}</span></footer>`;
}

function shell(active, content) {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
${exactTheme}${previewCss}</head>
<body><div class="stApp" data-testid="stAppViewContainer"><main><div class="block-container">
${navigation(active)}${content}
</div></main></div></body></html>`;
}

function homePage() {
  return shell(
    "home",
    `
<section class="editorial-hero">
  <div class="editorial-hero-copy">
    <div class="eyebrow">AI News Intelligence · Local and Explainable</div>
    <h1>News<br>intelligence,<br>with uncertainty<br>intact.</h1>
    <p>NewsLens AI condenses long-form reporting and independently estimates linguistic credibility risk from the original article. Each result includes calibrated confidence, observed textual signals, responsible-use limits, and a visitor-scoped review record.</p>
    <div class="hero-actions">
      <a class="editorial-button primary" href="#">Analyse an Article</a>
      <a class="editorial-button secondary" href="#">Open Archive</a>
    </div>
    <div class="technical-tags">TF-IDF CLASSIFICATION · CALIBRATED CONFIDENCE · HUMAN REVIEW · LOCAL EXPLANATIONS · SQLITE ARCHIVE</div>
  </div>
  <div class="editorial-hero-art"><img src="${heroArt}" alt="Original abstract editorial illustration of layered news pages"></div>
</section>
${strip(["Article Summarization", "TF-IDF Analysis", "Calibrated Risk", "Human Review", "Newsroom Analytics"])}
${metricsStrip([
  ["Champion model", metadata.champion_model ?? "Logistic Regression", "Saved pipeline · no runtime retraining"],
  ["Held-out Macro F1", Number(metrics.macro_f1).toFixed(3), "Measured on the packaged ISOT split"],
  ["Paid API", "Not required", "Hosting, compute, network and third-party terms may still apply"],
  ["History storage", "SQLite", "Structured records stay on this computer"],
])}
${section("Methodology", "A two-layer news intelligence engine", "Summarization and classification answer different questions. They process the same validated article independently.")}
<div class="preview-columns">
  <div>${card("Layer 01 · Summarization", "Readable compression", "The extractive summarizer ranks original sentences around a TF-IDF centroid. Optional DistilBART can produce new wording.")}</div>
  <div class="workflow-list">
    ${["Submit|Paste text, provide a public URL, or upload TXT/PDF.", "Extract|Validate and recover readable article text.", "Summarize|Generate a selected reading view.", "Classify|Estimate dataset-relative linguistic risk.", "Calibrate|Apply held-out confidence calibration and review policy.", "Review|Keep the model signal distinct from human assessment."]
      .map((value) => {
        const parts = value.split("|");
        return `<div class="workflow-item"><div><strong>${parts[0]}</strong><span>${parts[1]}</span></div></div>`;
      })
      .join("")}
  </div>
</div>
${footer("NewsLens AI · Engineering mini-project · Local-first", "Saved TF-IDF + Logistic Regression · Local academic prototype")}`,
  );
}

const syntheticText = read("data/sample/misleading_style_article.txt").trim();

function analysisInput() {
  return shell(
    "analyse",
    `
${pageHeader("Primary Analysis Desk", "Analyse one article.\nInspect two independent AI views.", "Summarization creates a compact reading view. Credibility classification examines the original cleaned article and reports a cautious, explainable risk estimate.")}
<div id="analysis-form-capture">
${strip(["Submit", "Extract", "Summarize", "Classify", "Explain", "Archive"])}
${section("01 · Prepare", "Article source and analysis settings", "Choose a source, summary method, and reading length.")}
<div class="preview-controls">
  <div class="preview-field"><label>Summarization method</label><div class="preview-select">Extractive · TF-IDF centroid</div></div>
  <div class="preview-field"><label>Summary length</label><div class="preview-segments"><span class="preview-segment active">Short</span><span class="preview-segment">Medium</span><span class="preview-segment">Detailed</span></div></div>
</div>
<div class="preview-field"><label>Article source</label><div class="preview-segments"><span class="preview-segment active">Paste text</span><span class="preview-segment">Public URL</span><span class="preview-segment">TXT / PDF upload</span></div></div>
<div style="height:.9rem"></div>
<div class="preview-field"><label>Article title (optional)</label><div class="preview-input">Viral cure claim — synthetic demonstration</div></div>
<div style="height:.9rem"></div>
<div class="preview-field"><label>Full article text</label><div class="preview-textarea">${esc(syntheticText)}</div></div>
<div class="preview-primary">Analyse Article</div>
${footer("NewsLens AI · Primary Analysis Desk", "Independent summary and classification paths")}
</div>`,
  );
}

function resultPage() {
  return shell(
    "analyse",
    `
${pageHeader("Analysis Complete", "Viral cure claim —\nsynthetic demonstration", "Structured local report · the summary and credibility-risk branches remain independent.")}
${metricsStrip([
  ["Article words", "143", "Validated source text"],
  ["Reading time", "1 min", "Estimated at normal pace"],
  ["Summary words", "28", "Short"],
  ["Compression", "80.4%", "Word-count reduction"],
  ["Total latency", "0.07s", "Local end-to-end runtime"],
])}
<div class="preview-columns verdict">
  <section class="verdict-panel misleading">
    <div class="verdict-label">Editorial risk signal · Above the review threshold</div>
    <div class="verdict-title">Higher misleading-content risk indicated</div>
    <p>The article more closely resembles misleading-labelled writing patterns in the training data. The score is dataset-relative; independent verification is still required.</p>
    <div class="verdict-probability"><strong>calibrated</strong><span>confidence · threshold 0.59</span></div>
    <div class="probability-bar"><span></span></div>
  </section>
  <section class="reading-panel">
    <div class="technical-label">Executive Summary</div>
    <h3>Viral cure claim — synthetic demonstration</h3>
    <p>Scientists have finally admitted that a common kitchen spice can replace every vaccine and cure almost any disease overnight, according to a shocking message spreading across social media.</p>
    <div class="reading-meta">Extractive · TF-IDF centroid · Short · 0.019s</div>
  </section>
</div>
${section("03 · Article Information", "Source, extraction and linguistic context", "These fields describe the processed input. They are not independent evidence for or against the article.")}
<div class="metadata-panel metadata-grid">
  ${[
    ["Input method", "Paste text"],
    ["Source domain", "Not available"],
    ["Author", "Not available"],
    ["Extraction method", "Direct input"],
    ["Language hint", "English-like"],
    ["Sentence count", "7"],
    ["Average sentence length", "20.4 words"],
    ["Analysis date", CAPTURE_DATE],
  ]
    .map(([label, value]) => `<div class="metadata-item"><span class="label">${label}</span><span class="value">${value}</span></div>`)
    .join("")}
</div>
${footer("NewsLens AI · Primary Analysis Desk", "Result language is colour-independent")}`,
  );
}

function explanationPage() {
  const misleadingTerms = ["viral · +0.2231", "share immediately · +0.1884", "unnamed · +0.1427", "claim · +0.1098"];
  const reliableTerms = ["official · −0.0815", "journal · −0.0674", "researcher · −0.0521", "verification · −0.0438"];
  const chips = (terms, klass) =>
    terms.map((term) => `<span class="evidence-chip ${klass}">${term}</span>`).join("");
  return shell(
    "analyse",
    `
${pageHeader("Model Explanation", "Why the linear model\nleaned this way.", "Observed TF-IDF × coefficient contributions describe model behaviour, not factual evidence or causality.")}
${section("04 · Evidence Signals", "Local terms from this article", "Direction and magnitude show how observed terms moved the saved linear score.")}
<div class="preview-chart" style="padding:1.2rem">
  ${[
    ["viral", 82, "danger-muted"],
    ["share immediately", 69, "danger-muted"],
    ["unnamed", 57, "danger-muted"],
    ["official", 35, "success-muted"],
    ["journal", 29, "success-muted"],
  ]
    .map(
      ([term, width, color]) => `<div style="display:grid;grid-template-columns:130px 1fr 55px;gap:.7rem;align-items:center;margin:.7rem 0;font:700 .68rem var(--mono)">
      <span>${term}</span><span style="height:13px;background:var(--paper-secondary);display:block"><span style="display:block;width:${width}%;height:100%;background:var(--${color})"></span></span><span>${color === "danger-muted" ? "+" : "−"}${(Number(width) / 367).toFixed(4)}</span>
    </div>`,
    )
    .join("")}
</div>
<div class="preview-columns">
  <div class="evidence-group"><div class="technical-label">Observed signals toward misleading</div><div>${chips(misleadingTerms, "misleading")}</div></div>
  <div class="evidence-group"><div class="technical-label">Observed signals toward reliable</div><div>${chips(reliableTerms, "reliable")}</div></div>
</div>
<div class="callout warning"><strong>Important disclaimer:</strong> This is an AI-assisted credibility-risk estimate based on linguistic patterns. It does not verify claims against independent evidence.</div>
${section("05 · Export", "Keep a portable copy of this analysis", "Exports are generated in memory. The original full article is not retained.")}
<div class="preview-columns"><div class="preview-primary">Download Analysis JSON</div><div class="preview-primary">Download Analysis PDF</div></div>
${footer("NewsLens AI · Primary Analysis Desk", "Independent verification remains necessary")}`,
  );
}

function performancePage() {
  return shell(
    "performance",
    `
${pageHeader("Model Accountability Report", "Measured performance.\nVisible limitations.", "All values come from committed evaluation artifacts. Classification uses a held-out ISOT split after duplicate removal.")}
${section("01 · Classification", "Champion-model results", "Macro-F1 gives both classes equal importance. ROC-AUC evaluates ranking, not universal reliability.")}
${metricsStrip([
  ["Accuracy", Number(metrics.accuracy).toFixed(4), "Overall held-out correctness"],
  ["Precision", Number(metrics.precision).toFixed(4), "Purity of misleading predictions"],
  ["Recall", Number(metrics.recall).toFixed(4), "Coverage of misleading-labelled rows"],
  ["Macro F1", Number(metrics.macro_f1).toFixed(4), "Equal weight for both classes"],
  ["ROC-AUC", Number(metrics.roc_auc).toFixed(4), "Threshold-independent ranking"],
])}
${section("02 · Held-Out Diagnostics", "Error distribution and threshold behaviour", "Saved figures use the same warm publication palette and preserve labels and margins.")}
<div class="preview-columns">
  <div><div class="preview-chart"><img src="${dataUri("reports/figures/confusion_matrix.png")}" alt="Held-out confusion matrix"></div><p class="preview-caption">Off-diagonal cells are errors: 10 false positives and 21 false negatives.</p></div>
  <div><div class="preview-chart"><img src="${dataUri("reports/figures/roc_pr_curves.png")}" alt="ROC and precision-recall curves"></div><p class="preview-caption">Near-perfect same-dataset curves may not transfer to unseen publishers or events.</p></div>
</div>
${footer("NewsLens AI · Model Accountability", "Measured artifacts only · no fabricated metrics")}`,
  );
}

function edaPage() {
  return shell(
    "eda",
    `
${pageHeader("Dataset Analysis · Research Appendix", "Know the collection\nbefore trusting the score.", "This report documents class balance, cleaning outcomes, language patterns, duplicates, leakage controls, and remaining limits.")}
${section("01 · Dataset Overview", "From raw collection to modelling sample", "Rows were screened, deduplicated before splitting, and sampled evenly for reproducibility.")}
${metricsStrip([
  ["Raw articles", Number(profile.raw_rows).toLocaleString("en-US"), "True.csv + Fake.csv"],
  ["Clean rows", Number(profile.clean_rows).toLocaleString("en-US"), "After filtering and deduplication"],
  ["Duplicates removed", Number(profile.duplicates_removed).toLocaleString("en-US"), "Normalised-text hashes"],
  ["Sample reliable", Number(profile.reliable_rows).toLocaleString("en-US"), "Balanced modelling rows"],
  ["Sample misleading", Number(profile.misleading_rows).toLocaleString("en-US"), "Balanced modelling rows"],
])}
${section("02 · Core Distributions", "Class balance and article length", "Balanced modelling prevents majority-class dominance. Length can still become an accidental shortcut.")}
<div class="preview-columns">
  <div><div class="preview-chart"><img src="${dataUri("reports/figures/class_distribution.png")}" alt="Balanced class distribution"></div><p class="preview-caption">The working sample is exactly balanced.</p></div>
  <div><div class="preview-chart"><img src="${dataUri("reports/figures/word_count_distribution.png")}" alt="Article word-count distribution"></div><p class="preview-caption">Length differences reflect collection and editorial patterns, not factual truth.</p></div>
</div>
${footer("NewsLens AI · Dataset Analysis", "Research appendix · measured artifacts")}`,
  );
}

function historyPage() {
  const rows = [
    [`#3 · ${CAPTURE_DATE} · Local input · Higher misleading-content risk indicated · review pending`, "Viral cure claim — synthetic demonstration", "A viral post makes an extraordinary medical claim without named researchers or clinical evidence."],
    [`#2 · ${CAPTURE_DATE} · Local input · Editorial review required · inconclusive`, "Developing policy report — synthetic demonstration", "The report presents mixed signals while important evidence remains incomplete."],
    [`#1 · ${CAPTURE_DATE} · Local input · Lower misleading-content risk indicated · review pending`, "Local council budget update — synthetic demonstration", "The council published a dated budget update with named officials and supporting documents."],
  ];
  return shell(
    "history",
    `
${pageHeader("Personal Editorial Archive", "Your analysis record,\nkept locally.", "Search, filter, sort, inspect, export, or explicitly delete structured analysis records. Full original text is not stored.")}
${section("01 · Find Records", "Search and filter the archive", "Filters operate only on the local SQLite result set.")}
<div class="preview-columns three">
  <div class="preview-field"><label>Search title, source, or summary</label><div class="preview-input">synthetic demonstration</div></div>
  <div class="preview-field"><label>Verdict</label><div class="preview-select">All</div></div>
  <div class="preview-field"><label>Sort order</label><div class="preview-select">Newest first</div></div>
</div>
${metricsStrip([
  ["Matching records", "3", "Current filter result"],
  ["Average risk", "49.9%", "Mean misleading probability"],
  ["Latest record", CAPTURE_DATE, "Newest first"],
  ["Storage", "Local SQLite", "No uploaded files retained"],
])}
${section("02 · Archive Index", "Compact editorial records", "Long titles and summaries wrap inside bounded rows.")}
${rows
  .map(
    ([meta, title, summary]) => `<article class="archive-row"><div class="archive-meta">${meta}</div><h3>${title}</h3><div class="archive-preview">${summary}</div></article>`,
  )
  .join("")}
${footer("NewsLens AI · Editorial Archive", "SQLite · searchable local history")}`,
  );
}

function aboutPage() {
  return shell(
    "about",
    `
${pageHeader("Research & About", "A transparent academic\nnews-intelligence prototype.", "NewsLens AI combines robust ingestion, independent NLP branches, explainable classification, local persistence, measured evaluation, and explicit limits.")}
${section("01 · Purpose", "The problem being addressed", "Readers need concise access to long articles and a cautious indication of linguistic credibility risk.")}
<div class="preview-columns">
  ${card("Need 01", "Article overload", "Extractive or optional abstractive summarization creates a shorter reading view while preserving the full article as classifier input.")}
  ${card("Need 02", "Opaque model outputs", "Probabilities, confidence bands, observed term contributions, measured limitations, and downloadable records make the prediction inspectable.")}
</div>
${section("02 · Architecture", "Six implemented runtime stages", "Training remains offline and is never triggered by application startup.")}
<div class="preview-columns three">
  ${["Presentation|Editorial Streamlit pages and exports.", "Ingestion|Text, URL, TXT/PDF and validation.", "NLP preparation|Cleaning, segmentation and metadata.", "AI processing|Summary plus saved linear classifier.", "Persistence|Joblib, metadata and SQLite.", "Evaluation|Metrics, errors, tests and figures."]
    .map((value) => {
      const [title, body] = value.split("|");
      return `<div class="preview-pair"><strong>${title}</strong><span>${body}</span></div>`;
    })
    .join("")}
</div>
${section("03 · Responsible AI", "Capabilities and explicit limits", "Linguistic classification is not evidence retrieval or factual verification.")}
<div class="preview-columns">
  ${card("What it can do", "Inspection and triage", "Compress text, estimate dataset-pattern similarity, expose influential terms, quantify uncertainty, and preserve a local record.")}
  ${card("What it cannot do", "No truth oracle", "It cannot verify claims, infer intent, guarantee fairness, or replace journalists and professional fact-checkers.")}
</div>
<div class="callout warning"><strong>Important disclaimer:</strong> Treat the result as an AI-assisted credibility-risk estimate and verify consequential claims through trusted independent sources.</div>
${footer("NewsLens AI · Research & About", "Local academic prototype")}`,
  );
}

const captures = [
  ["01_home.png", homePage, { width: 1440, height: 1000 }, {}],
  ["02_analysis_input.png", analysisInput, { width: 1440, height: 1000 }, { fullPage: true }],
  ["03_summary_and_risk_results.png", resultPage, { width: 1440, height: 930 }, {}],
  ["04_explainability_and_downloads.png", explanationPage, { width: 1440, height: 1000 }, { fullPage: true }],
  ["05_model_performance.png", performancePage, { width: 1440, height: 1000 }, { fullPage: true }],
  ["06_dataset_eda.png", edaPage, { width: 1440, height: 1000 }, { fullPage: true }],
  ["07_analysis_history.png", historyPage, { width: 1440, height: 1000 }, { fullPage: true }],
  ["08_research_about.png", aboutPage, { width: 1440, height: 1000 }, { fullPage: true }],
  ["09_home_mobile.png", homePage, { width: 390, height: 844 }, {}],
  ["10_analysis_mobile.png", analysisInput, { width: 390, height: 844 }, { selector: "#analysis-form-capture" }],
];

function pngDimensions(data) {
  if (data.length < 24 || data.toString("ascii", 1, 4) !== "PNG") {
    throw new Error("Screenshot output is not a valid PNG.");
  }
  return {
    width: data.readUInt32BE(16),
    height: data.readUInt32BE(20),
  };
}

async function assertLayout(page, viewport, filename) {
  const result = await page.evaluate(({ width, height }) => {
    const documentWidth = document.documentElement.scrollWidth;
    const bodyWidth = document.body.scrollWidth;
    const bad = [];
    for (const element of document.querySelectorAll("body *")) {
      const rect = element.getBoundingClientRect();
      if (rect.right > width + 1 || rect.left < -1) {
        bad.push(`${String(element.className || element.tagName).slice(0, 60)}: ${rect.left.toFixed(1)}..${rect.right.toFixed(1)}`);
        if (bad.length >= 20) break;
      }
    }
    const unloadedImages = [...document.images]
      .filter((image) => !image.complete || image.naturalWidth === 0)
      .map((image) => image.alt || image.src.slice(0, 40));
    const clippedHeadings = [...document.querySelectorAll("h1, h2, h3")]
      .filter((heading) => heading.scrollWidth > heading.clientWidth + 1)
      .map((heading) => heading.textContent.trim().slice(0, 80));
    return { documentWidth, bodyWidth, viewportWidth: width, viewportHeight: height, bad, unloadedImages, clippedHeadings };
  }, viewport);
  if (
    result.documentWidth > viewport.width + 1 ||
    result.bodyWidth > viewport.width + 1 ||
    result.bad.length ||
    result.unloadedImages.length ||
    result.clippedHeadings.length
  ) {
    throw new Error(`${filename} layout failure: ${JSON.stringify(result)}`);
  }
}

async function main() {
  fs.mkdirSync(OUTPUT, { recursive: true });
  fs.mkdirSync(RESULTS, { recursive: true });
  const rendered = [];
  const browser = await chromium.launch({
    executablePath: CHROMIUM_PATH,
    headless: true,
    args: ["--no-sandbox", "--no-zygote", "--single-process", "--disable-dev-shm-usage"],
  });
  try {
    const context = await browser.newContext({
      viewport: captures[0][2],
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    for (const [filename, build, viewport, captureOptions] of captures) {
      await page.setViewportSize(viewport);
      await page.setContent(build(), { waitUntil: "load" });
      await page.emulateMedia({ reducedMotion: "reduce" });
      await assertLayout(page, viewport, filename);
      const screenshotOptions = {
        path: path.join(OUTPUT, filename),
        animations: "disabled",
      };
      if (captureOptions.selector) {
        await page.locator(captureOptions.selector).screenshot(screenshotOptions);
      } else {
        await page.screenshot({
          ...screenshotOptions,
          fullPage: Boolean(captureOptions.fullPage),
        });
      }
      const outputPath = path.join(OUTPUT, filename);
      const data = fs.readFileSync(outputPath);
      const bytes = data.byteLength;
      const dimensions = pngDimensions(data);
      rendered.push({
        filename,
        width: dimensions.width,
        height: dimensions.height,
        size_bytes: bytes,
        sha256: createHash("sha256").update(data).digest("hex"),
      });
      console.log(`${filename} ${bytes} bytes`);
    }
    await context.close();
    const manifest = {
      interface_name: "NewsLens AI warm editorial newsroom",
      design_system: "Warm editorial newsroom",
      capture_date: CAPTURE_DATE,
      generated_at_utc: new Date().toISOString(),
      source_css: "ui/theme.py::GLOBAL_CSS",
      captures: rendered,
    };
    fs.writeFileSync(
      path.join(RESULTS, "reference_ui_screenshot_manifest.json"),
      `${JSON.stringify(manifest, null, 2)}\n`,
      "utf8",
    );
    console.log(`reference_ui_screenshot_manifest.json ${rendered.length} captures`);
  } finally {
    await browser.close();
  }
}

function emitHtml() {
  fs.mkdirSync(HTML_OUTPUT, { recursive: true });
  for (const [filename, build, viewport, captureOptions] of captures) {
    const htmlName = filename.replace(/\.png$/i, ".html");
    const metadata = {
      filename,
      viewport,
      full_page: Boolean(captureOptions.fullPage),
      selector: captureOptions.selector ?? null,
    };
    const document = build().replace(
      "</head>",
      `<script type="application/json" id="capture-metadata">${JSON.stringify(metadata)}</script></head>`,
    );
    fs.writeFileSync(path.join(HTML_OUTPUT, htmlName), document, "utf8");
    console.log(`${htmlName} ${Buffer.byteLength(document, "utf8")} bytes`);
  }
}

if (HTML_ONLY) {
  emitHtml();
} else {
  await main();
}
