import fs from "node:fs/promises";
import { execFileSync } from "node:child_process";

async function loadArtifactTool() {
  try {
    return await import("@oai/artifact-tool");
  } catch (error) {
    const runtimeModules = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
    if (!runtimeModules || error?.code !== "ERR_MODULE_NOT_FOUND") throw error;
    return import(`${runtimeModules}/@oai/artifact-tool/dist/artifact_tool.mjs`);
  }
}

const { SpreadsheetFile, Workbook } = await loadArtifactTool();

const projectRoot = process.env.NEWSLENS_PROJECT_ROOT
  ? `${process.env.NEWSLENS_PROJECT_ROOT.replace(/\/$/, "")}/`
  : new URL("../", import.meta.url).pathname;
const papers = JSON.parse(await fs.readFile(`${projectRoot}docs/research_papers.json`, "utf8"));
const outputPath = `${projectRoot}docs/NewsLens_AI_Research_Paper_Matrix.xlsx`;
const previewPath = `${projectRoot}reports/figures/research_matrix_preview.png`;

const workbook = Workbook.create();
const overview = workbook.worksheets.add("Overview");
const matrix = workbook.worksheets.add("Literature Matrix");
const scope = workbook.worksheets.add("Coverage Map");

const espresso = "#2A241F";
const camel = "#9B8066";
const bronze = "#806A5A";
const sage = "#526458";
const ivory = "#F8F4EA";
const sand = "#E8DDCA";
const ink = "#1A1917";
const muted = "#6F685F";

for (const sheet of [overview, matrix, scope]) {
  sheet.showGridLines = false;
}

overview.getRange("A1:H2").merge();
overview.getRange("A1").values = [["NEWSLENS AI · VERIFIED LITERATURE SURVEY"]];
overview.getRange("A1:H2").format = {
  fill: espresso,
  font: { bold: true, color: "#FFFFFF", size: 22 },
  verticalAlignment: "center",
  horizontalAlignment: "left",
};
overview.getRange("A3:H3").merge();
overview.getRange("A3").values = [["10 peer-reviewed papers · 6 IEEE Xplore records · access status disclosed · metadata checked 30 July 2026"]];
overview.getRange("A3:H3").format = {
  fill: sand,
  font: { color: ink, italic: true, size: 10 },
  verticalAlignment: "center",
};

overview.getRange("A5:B5").values = [["Metric", "Value"]];
overview.getRange("A6:A10").values = [
  ["Total papers"],
  ["IEEE Xplore papers"],
  ["Open Access"],
  ["2020 or newer"],
  ["Summarization-focused"],
];
overview.getRange("B6:B10").formulas = [
  ["=COUNTA('Literature Matrix'!A7:A16)"],
  ["=COUNTIF('Literature Matrix'!G7:G16,\"<>Not applicable\")"],
  ["=COUNTIF('Literature Matrix'!H7:H16,\"Open Access\")"],
  ["=COUNTIF('Literature Matrix'!D7:D16,\">=2020\")"],
  ["=COUNTIF('Coverage Map'!B7:B16,\"Summarization\")"],
];
overview.getRange("A5:B10").format.borders = { preset: "inside", style: "thin", color: "#C9D6EA" };
overview.getRange("A5:B5").format = { fill: camel, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
overview.getRange("A6:A10").format = { fill: ivory, font: { color: ink } };
overview.getRange("B6:B10").format = { fill: "#FFFFFF", font: { bold: true, color: bronze, size: 14 }, horizontalAlignment: "center", numberFormat: "0" };

overview.getRange("D5:H5").merge();
overview.getRange("D5").values = [["Reading and access note"]];
overview.getRange("D5:H5").format = { fill: bronze, font: { bold: true, color: "#FFFFFF" } };
overview.getRange("D6:H10").merge();
overview.getRange("D6").values = [["Open Access indicates a lawful public full-text route located during review. Institutional Access Required means IEEE metadata and available author/preprint material were checked, but publisher-formatted access can depend on the student's institute. No paywalled full text is represented as fully reviewed. DOI and source URLs are clickable in Excel."]];
overview.getRange("D6:H10").format = { fill: "#F2ECE1", font: { color: ink, size: 10 }, wrapText: true, verticalAlignment: "top" };

overview.getRange("A12:C12").values = [["Year", "IEEE papers", "Other papers"]];
const years = [2017, 2018, 2020, 2021, 2022, 2024];
overview.getRange("A13:A18").values = years.map((year) => [year]);
overview.getRange("B13:B18").formulas = years.map((_, index) => [`=COUNTIFS('Literature Matrix'!D$7:D$16,A${13 + index},'Literature Matrix'!G$7:G$16,\"<>Not applicable\")`]);
overview.getRange("C13:C18").formulas = years.map((_, index) => [`=COUNTIFS('Literature Matrix'!D$7:D$16,A${13 + index},'Literature Matrix'!G$7:G$16,\"Not applicable\")`]);
overview.getRange("A12:C18").format.borders = { preset: "inside", style: "thin", color: "#D7E0EE" };
overview.getRange("A12:C12").format = { fill: sage, font: { bold: true, color: "#FFFFFF" } };
const chart = overview.charts.add("bar", overview.getRange("A12:C18"));
chart.title = "Selected literature by publication year";
chart.hasLegend = true;
chart.yAxis = { numberFormatCode: "0", min: 0, max: 6 };
chart.setPosition("D12", "H27");
const chartSeries = chart.series.items;
if (chartSeries[0]) chartSeries[0].fill = bronze;
if (chartSeries[1]) chartSeries[1].fill = sage;

overview.getRange("A29:H29").merge();
overview.getRange("A29").values = [["Selection rule"]];
overview.getRange("A29:H29").format = { fill: espresso, font: { bold: true, color: "#FFFFFF" } };
overview.getRange("A30:H33").merge();
overview.getRange("A30").values = [["The survey intentionally combines recent IEEE work with foundational ACL papers. It covers at least two summarization papers, two fake-news papers, transformer architecture, explainability, benchmark bias/generalisation, and an evidence-oriented fact-checking direction. Older XSum and LIAR papers are retained because they define datasets directly evaluated or compared in this project."]];
overview.getRange("A30:H33").format = { fill: "#F7FAFF", font: { color: ink }, wrapText: true, verticalAlignment: "top" };
overview.getRange("A35:H35").merge();
overview.getRange("A35").values = [["Ownership and permitted use"]];
overview.getRange("A35:H35").format = { fill: bronze, font: { bold: true, color: "#FFFFFF" } };
overview.getRange("A36:H37").merge();
overview.getRange("A36").values = [["NewsLens AI was designed and developed by Deven Sachin Gaikwad. © 2026 Deven Sachin Gaikwad. All Rights Reserved. This research matrix is proprietary project documentation; viewing the public source does not grant permission to copy, modify, redistribute, sublicense or commercially exploit it."]];
overview.getRange("A36:H37").format = { fill: "#F2ECE1", font: { color: ink, size: 10 }, wrapText: true, verticalAlignment: "top" };
overview.getRange("A1:H37").format.font.name = "Aptos";
overview.getRange("A1:H37").format.rowHeight = 22;
overview.getRange("A1:H2").format.rowHeight = 32;
overview.getRange("A3:H3").format.rowHeight = 25;
overview.getRange("D6:H10").format.rowHeight = 24;
overview.getRange("A30:H33").format.rowHeight = 24;
overview.getRange("A36:H37").format.rowHeight = 24;
overview.getRange("A:A").format.columnWidth = 28;
overview.getRange("B:B").format.columnWidth = 15;
overview.getRange("C:C").format.columnWidth = 15;
overview.getRange("D:H").format.columnWidth = 17;
overview.freezePanes.freezeRows(3);

const headers = Object.keys(papers[0]);
matrix.getRange("A1:P2").merge();
matrix.getRange("A1").values = [["RESEARCH PAPER COMPARISON MATRIX"]];
matrix.getRange("A1:P2").format = { fill: espresso, font: { bold: true, color: "#FFFFFF", size: 20 }, verticalAlignment: "center" };
matrix.getRange("A3:P4").merge();
matrix.getRange("A3").values = [["Scope: automated text/news summarization, fake-news detection, explainability, benchmark bias and generalisation. Findings reflect reviewed full text where publicly available; access constraints are stated per row."]];
matrix.getRange("A3:P4").format = { fill: sand, font: { color: ink, italic: true }, wrapText: true, verticalAlignment: "center" };
matrix.getRange("A6:P6").values = [headers];
matrix.getRange("A7:P16").values = papers.map((paper) => headers.map((header) => paper[header]));
const table = matrix.tables.add("A6:P16", true, "LiteratureMatrix");
table.style = "TableStyleLight1";
table.showBandedColumns = false;
matrix.getRange("A6:P6").format = { fill: camel, font: { bold: true, color: "#FFFFFF", size: 10 }, wrapText: true, verticalAlignment: "center", horizontalAlignment: "center" };
matrix.getRange("A7:P16").format = { fill: ivory, font: { color: ink, size: 9 }, wrapText: true, verticalAlignment: "top" };
for (const row of [8, 10, 12, 14, 16]) {
  matrix.getRange(`A${row}:P${row}`).format.fill = "#FFFFFF";
}
matrix.getRange("A7:A16").format.horizontalAlignment = "center";
matrix.getRange("D7:D16").format.horizontalAlignment = "center";
matrix.getRange("A6:P16").format.borders = { preset: "inside", style: "thin", color: "#D8E2F0" };
matrix.getRange("H7:H16").conditionalFormats.add("containsText", { text: "Open Access", format: { fill: "#DDF7EF", font: { color: "#087767", bold: true } } });
matrix.getRange("H7:H16").conditionalFormats.add("containsText", { text: "Institutional", format: { fill: "#FFF2D5", font: { color: "#8A5600", bold: true } } });
matrix.getRange("A:A").format.columnWidth = 8;
matrix.getRange("B:B").format.columnWidth = 38;
matrix.getRange("C:C").format.columnWidth = 33;
matrix.getRange("D:D").format.columnWidth = 9;
matrix.getRange("E:E").format.columnWidth = 37;
matrix.getRange("F:F").format.columnWidth = 28;
matrix.getRange("G:G").format.columnWidth = 34;
matrix.getRange("H:H").format.columnWidth = 25;
matrix.getRange("I:P").format.columnWidth = 37;
matrix.getRange("A6:P6").format.rowHeight = 46;
matrix.getRange("A7:P16").format.rowHeight = 112;
matrix.getRange("A1:P16").format.font.name = "Aptos";
matrix.freezePanes.freezeRows(6);
matrix.freezePanes.freezeColumns(2);

const coverageRows = [
  [1, "Summarization", "Transformer / domain evaluation", "IEEE", "T5", "ROUGE + repeated runs"],
  [2, "Summarization", "News summarization", "IEEE", "T5", "ROUGE precision/recall/F1"],
  [3, "Fake-news detection", "Explainability", "IEEE", "Co-attention", "Top-k sentence/comment XAI"],
  [4, "Integrated fact-checking", "Evidence + explainability", "IEEE", "QA + attention", "Gold-evidence limitation exposed"],
  [5, "Fake-news detection", "Hybrid DL + XAI", "IEEE", "FastText CNN-LSTM", "Multi-dataset + LIME"],
  [6, "Fake-news detection", "Generalisation", "IEEE", "Multichannel CNN", "Three real-world datasets"],
  [7, "Summarization", "Transformer foundation", "ACL", "BART", "Denoising encoder-decoder"],
  [8, "Fake-news detection", "Dataset bias/reasoning", "ACL", "Ablation study", "Evidence shortcut warning"],
  [9, "Summarization", "Dataset foundation", "ACL", "Topic-aware ConvS2S", "Introduced XSum"],
  [10, "Fake-news detection", "Dataset foundation", "ACL", "Hybrid CNN", "Introduced LIAR"],
];
scope.getRange("A1:F2").merge();
scope.getRange("A1").values = [["COVERAGE AND REQUIREMENT MAP"]];
scope.getRange("A1:F2").format = { fill: espresso, font: { bold: true, color: "#FFFFFF", size: 20 }, verticalAlignment: "center" };
scope.getRange("A4:F4").merge();
scope.getRange("A4").values = [["This sheet makes the literature-selection coverage auditable rather than relying on colour or narrative alone."]];
scope.getRange("A4:F4").format = { fill: sand, font: { italic: true, color: ink } };
scope.getRange("A6:F6").values = [["Sr. No.", "Primary area", "Required theme", "Venue family", "Core model", "Why selected"]];
scope.getRange("A7:F16").values = coverageRows;
scope.tables.add("A6:F16", true, "CoverageTable").style = "TableStyleLight1";
scope.getRange("A6:F6").format = { fill: sage, font: { bold: true, color: "#FFFFFF" }, wrapText: true };
scope.getRange("A7:F16").format = { fill: ivory, font: { color: ink, size: 10 }, wrapText: true, verticalAlignment: "top" };
for (const row of [8, 10, 12, 14, 16]) {
  scope.getRange(`A${row}:F${row}`).format.fill = "#FFFFFF";
}
scope.getRange("A:A").format.columnWidth = 10;
scope.getRange("B:B").format.columnWidth = 24;
scope.getRange("C:C").format.columnWidth = 28;
scope.getRange("D:D").format.columnWidth = 18;
scope.getRange("E:E").format.columnWidth = 25;
scope.getRange("F:F").format.columnWidth = 38;
scope.getRange("A7:F16").format.rowHeight = 48;
scope.getRange("A1:F16").format.font.name = "Aptos";
scope.freezePanes.freezeRows(6);

const errorScan = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" });
if (String(errorScan).includes("#REF!") || String(errorScan).includes("#DIV/0!")) {
  throw new Error(`Formula error detected: ${errorScan}`);
}

const preview = await workbook.render({ sheetName: "Overview", autoCrop: "all", scale: 1.2, format: "png" });
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
if (process.env.NEWSLENS_QA_DIR) {
  await fs.mkdir(process.env.NEWSLENS_QA_DIR, { recursive: true });
  for (const sheetName of ["Overview", "Literature Matrix", "Coverage Map"]) {
    const qaPreview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
    const qaName = sheetName.toLowerCase().replaceAll(" ", "_");
    await fs.writeFile(
      `${process.env.NEWSLENS_QA_DIR}/${qaName}.png`,
      new Uint8Array(await qaPreview.arrayBuffer()),
    );
  }
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
execFileSync(process.env.PYTHON || "python", [
  `${projectRoot}scripts/set_office_metadata.py`,
  outputPath,
  "--title", "NewsLens AI Research Paper Matrix",
  "--author", "Deven Sachin Gaikwad",
  "--rights", "© 2026 Deven Sachin Gaikwad. All Rights Reserved.",
  "--subject", "Sanitized NewsLens AI literature survey and research matrix",
], { stdio: "inherit" });
await fs.rm(`${outputPath}.inspect.ndjson`, { force: true });
console.log(`Wrote ${outputPath}`);
