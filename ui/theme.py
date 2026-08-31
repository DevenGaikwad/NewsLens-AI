"""Warm editorial design tokens and resilient Streamlit CSS."""

from __future__ import annotations

import streamlit as st


GLOBAL_CSS = """
<style>
:root {
  --paper-primary: #F3F0E8;
  --paper-secondary: #EAE4D8;
  --paper-highlight: #FAF8F2;
  --warm-beige: #D8CCBA;
  --muted-taupe: #A89984;
  --editorial-brown: #6D5947;
  --deep-brown: #40352C;
  --charcoal: #1A1917;
  --ink-black: #090909;
  --soft-grey: #77736C;
  --border-light: #D4CEC2;
  --border-dark: #393631;
  --success-muted: #496454;
  --success-paper: #E7ECE6;
  --warning-muted: #8A693D;
  --warning-paper: #F1E9DA;
  --danger-muted: #813F39;
  --danger-paper: #F1E2DF;
  --serif: Georgia, "Times New Roman", serif;
  --sans: Inter, Arial, Helvetica, sans-serif;
  --mono: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
}

html, body, [class*="css"] {
  font-family: var(--sans);
}

html {
  scroll-behavior: smooth;
}

body {
  background: var(--paper-primary);
}

.stApp {
  color: var(--charcoal);
  background-color: var(--paper-primary);
  background-image:
    radial-gradient(rgba(64, 53, 44, .035) .7px, transparent .7px),
    linear-gradient(180deg, rgba(255,255,255,.22), rgba(216,204,186,.08));
  background-size: 5px 5px, 100% 100%;
}

[data-testid="stAppViewContainer"] {
  background: transparent;
}

[data-testid="stHeader"] {
  background: rgba(243, 240, 232, .92);
  border-bottom: 1px solid rgba(212, 206, 194, .65);
  backdrop-filter: blur(8px);
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
  color: var(--deep-brown);
}

[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
  display: none;
}

.block-container {
  max-width: 1280px;
  /* Reserve the fixed native Streamlit router height so the product
     masthead is never cropped beneath it. */
  padding: 4.85rem 2.2rem 4.5rem;
}

h1, h2, h3, h4, h5, h6 {
  color: var(--ink-black);
  font-family: var(--serif) !important;
  font-weight: 600;
  letter-spacing: -.025em;
}

h1 { font-size: clamp(2.3rem, 5vw, 4.9rem); line-height: .98; }
h2 { font-size: clamp(1.65rem, 3vw, 2.55rem); line-height: 1.08; }
h3 { font-size: clamp(1.2rem, 2vw, 1.6rem); line-height: 1.15; }

p, li, label, [data-testid="stMarkdownContainer"] {
  color: var(--charcoal);
  line-height: 1.68;
}

a {
  color: var(--deep-brown);
  text-decoration-color: var(--muted-taupe);
  text-underline-offset: 3px;
}

a:hover {
  color: var(--ink-black);
}

hr {
  border-color: var(--border-light) !important;
}

code, pre {
  font-family: var(--mono) !important;
}

pre {
  background: var(--paper-secondary) !important;
  border: 1px solid var(--border-light);
  border-radius: 2px !important;
}

/* Product masthead and top navigation */
.nl-masthead {
  align-items: center;
  border-bottom: 1px solid var(--border-dark);
  display: flex;
  justify-content: space-between;
  padding: .35rem 0 .8rem;
}

.nl-brand {
  align-items: center;
  color: var(--ink-black) !important;
  display: inline-flex;
  font-family: var(--serif);
  font-size: 1.35rem;
  font-weight: 700;
  gap: .62rem;
  letter-spacing: -.02em;
  text-decoration: none !important;
}

.nl-brand img {
  height: 30px;
  width: 30px;
}

.nl-descriptor {
  color: var(--soft-grey);
  font-family: var(--mono);
  font-size: .68rem;
  font-weight: 700;
  letter-spacing: .11em;
  text-transform: uppercase;
}

.nl-nav {
  align-items: center;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  gap: .18rem;
  justify-content: flex-end;
  margin-bottom: 1.5rem;
  padding: .58rem 0;
}

.nl-nav a {
  border-bottom: 2px solid transparent;
  color: var(--deep-brown);
  font-size: .78rem;
  font-weight: 650;
  letter-spacing: .015em;
  padding: .5rem .67rem .42rem;
  text-decoration: none;
  white-space: nowrap;
}

.nl-nav a:hover,
.nl-nav a[aria-current="page"] {
  border-bottom-color: var(--ink-black);
  color: var(--ink-black);
}

.nl-nav a.nl-nav-cta {
  background: var(--ink-black);
  border: 1px solid var(--ink-black);
  color: var(--paper-highlight);
  margin-left: .35rem;
  padding: .52rem .82rem;
}

.nl-nav a.nl-nav-cta:hover,
.nl-nav a.nl-nav-cta[aria-current="page"] {
  background: var(--deep-brown);
  border-color: var(--deep-brown);
  color: #fff;
}

/* Native Streamlit navigation owns routing and browser history. */
[data-testid="stTopNavLinkContainer"] {
  background: rgba(250, 248, 242, .96);
  border-bottom: 1px solid var(--border-dark);
  box-shadow: none;
  font-family: var(--sans);
  min-height: 48px;
}

[data-testid="stTopNavLink"],
[data-testid="stTopNavLink"] a {
  align-items: center;
  color: var(--deep-brown) !important;
  display: inline-flex;
  font-size: .76rem;
  font-weight: 750;
  letter-spacing: .018em;
  min-height: 44px;
  text-decoration: none !important;
}

[data-testid="stTopNavLink"]:hover,
[data-testid="stTopNavLink"]:hover a,
[data-testid="stTopNavLink"][aria-current="page"],
[data-testid="stTopNavLink"][aria-current="page"] a,
[data-testid="stTopNavLink"] a[aria-current="page"] {
  background: var(--paper-secondary);
  color: var(--ink-black) !important;
}

[data-testid="stTopNavLink"]:focus-visible,
[data-testid="stTopNavLink"] a:focus-visible,
[data-testid="stPageLink-NavLink"]:focus-visible,
[data-testid="stPageLink-NavLink"] a:focus-visible,
a:focus-visible,
button:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible {
  outline: 3px solid var(--editorial-brown) !important;
  outline-offset: 3px;
}

/* Hero and editorial sections */
.editorial-hero {
  align-items: stretch;
  background: var(--paper-highlight);
  border-bottom: 1px solid var(--border-dark);
  border-top: 1px solid var(--border-dark);
  display: grid;
  grid-template-columns: minmax(0, 1.18fr) minmax(280px, .82fr);
  margin: .25rem 0 1rem;
  min-height: 430px;
}

.editorial-hero > * {
  min-width: 0;
}

.editorial-hero-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: clamp(2rem, 5vw, 4.5rem);
}

.editorial-hero-art {
  align-items: stretch;
  background: var(--paper-secondary);
  border-left: 1px solid var(--border-dark);
  display: flex;
  min-height: 330px;
  min-width: 0;
  overflow: hidden;
}

.editorial-hero-art img {
  display: block;
  height: 100%;
  max-width: 100%;
  object-fit: cover;
  width: 100%;
}

.eyebrow,
.section-kicker,
.technical-label {
  color: var(--editorial-brown);
  font-family: var(--mono);
  font-size: .68rem;
  font-weight: 800;
  letter-spacing: .14em;
  text-transform: uppercase;
}

.editorial-hero h1 {
  font-size: clamp(3.1rem, 5.8vw, 5.2rem);
  line-height: .89;
  margin: .72rem 0 1.15rem;
  max-width: 780px;
}

.editorial-hero p {
  color: var(--deep-brown);
  font-size: 1.04rem;
  line-height: 1.72;
  margin: 0;
  max-width: 680px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: .65rem;
  margin-top: 1.55rem;
}

.editorial-button {
  align-items: center;
  border: 1px solid var(--ink-black);
  border-radius: 2px;
  display: inline-flex;
  font-size: .8rem;
  font-weight: 750;
  justify-content: center;
  letter-spacing: .025em;
  min-height: 44px;
  padding: .68rem 1rem;
  text-decoration: none !important;
}

.editorial-button.primary {
  background: var(--ink-black);
  color: var(--paper-highlight);
}

.editorial-button.secondary {
  background: transparent;
  color: var(--ink-black);
}

.editorial-button:hover {
  background: var(--deep-brown);
  border-color: var(--deep-brown);
  color: white;
}

/* Hero calls-to-action remain native page links, styled as editorial buttons. */
.st-key-nl_hero_actions {
  margin-top: 1.3rem;
}

.st-key-nl_hero_actions [data-testid="stPageLink-NavLink"],
.st-key-nl_hero_actions [data-testid="stPageLink-NavLink"] a {
  align-items: center;
  border: 1px solid var(--ink-black);
  border-radius: 2px;
  box-shadow: none;
  display: inline-flex;
  font-size: .8rem;
  font-weight: 750;
  justify-content: center;
  letter-spacing: .025em;
  min-height: 44px;
  padding: .63rem .95rem;
  text-decoration: none !important;
  width: 100%;
}

.st-key-nl_hero_actions > [data-testid="stElementContainer"]:first-child [data-testid="stPageLink-NavLink"],
.st-key-nl_hero_actions > [data-testid="stElementContainer"]:first-child [data-testid="stPageLink-NavLink"] a {
  background: var(--ink-black);
  color: var(--paper-highlight) !important;
}

.st-key-nl_hero_actions > [data-testid="stElementContainer"]:first-child [data-testid="stMarkdownContainer"] p {
  color: var(--paper-highlight) !important;
}

.st-key-nl_hero_actions > [data-testid="stElementContainer"]:last-child [data-testid="stPageLink-NavLink"],
.st-key-nl_hero_actions > [data-testid="stElementContainer"]:last-child [data-testid="stPageLink-NavLink"] a {
  background: transparent;
  color: var(--ink-black) !important;
}

.st-key-nl_hero_actions > [data-testid="stElementContainer"]:last-child [data-testid="stMarkdownContainer"] p {
  color: var(--ink-black) !important;
}

.st-key-nl_hero_actions [data-testid="stPageLink-NavLink"]:hover,
.st-key-nl_hero_actions [data-testid="stPageLink-NavLink"]:hover a {
  background: var(--deep-brown);
  border-color: var(--deep-brown);
  color: #fff !important;
}

.st-key-nl_hero_actions [data-testid="stPageLink-NavLink"]:hover [data-testid="stMarkdownContainer"] p {
  color: #fff !important;
}

.technical-tags {
  color: var(--soft-grey);
  font-family: var(--mono);
  font-size: .65rem;
  letter-spacing: .04em;
  line-height: 1.7;
  margin-top: 1.25rem;
  text-transform: uppercase;
}

.page-hero {
  border-bottom: 1px solid var(--border-dark);
  display: grid;
  gap: 1.2rem;
  grid-template-columns: minmax(0, 1.25fr) minmax(240px, .75fr);
  margin-bottom: 1.7rem;
  padding: 1.6rem 0 1.75rem;
}

.page-hero h1 {
  font-size: clamp(2.5rem, 5vw, 4.8rem);
  line-height: .94;
  margin: .65rem 0 0;
}

.page-hero p {
  align-self: end;
  color: var(--deep-brown);
  font-size: .98rem;
  margin: 0;
}

.editorial-strip {
  background: var(--ink-black);
  color: var(--paper-highlight);
  font-family: var(--mono);
  font-size: .65rem;
  font-weight: 700;
  letter-spacing: .095em;
  line-height: 1.65;
  margin: 1rem 0 2.6rem;
  overflow: hidden;
  padding: .74rem 1rem;
  text-align: center;
  text-transform: uppercase;
}

.section-heading {
  border-top: 1px solid var(--border-dark);
  display: grid;
  gap: 1.25rem;
  grid-template-columns: minmax(0, 1.2fr) minmax(240px, .8fr);
  margin: 2.8rem 0 1.35rem;
  padding-top: 1rem;
}

.section-heading h2 {
  margin: .32rem 0 0;
}

.section-heading p {
  align-self: end;
  color: var(--soft-grey);
  margin: 0;
}

.editorial-card,
.reading-panel,
.metadata-panel {
  background: var(--paper-highlight);
  border: 1px solid var(--border-light);
  border-left: 3px solid var(--editorial-brown);
  border-radius: 0 5px 5px 0;
  box-shadow: none;
  height: 100%;
  padding: 1.15rem 1.2rem;
}

.editorial-card h3,
.reading-panel h3 {
  font-size: 1.18rem;
  margin: .28rem 0 .55rem;
}

.editorial-card p {
  color: var(--soft-grey);
  font-size: .9rem;
  margin: 0;
}

.workflow-list {
  border-top: 1px solid var(--border-dark);
  counter-reset: workflow;
  margin: 0;
}

.workflow-item {
  border-bottom: 1px solid var(--border-light);
  display: grid;
  gap: 1rem;
  grid-template-columns: 46px 1fr;
  padding: .9rem 0;
}

.workflow-item::before {
  color: var(--editorial-brown);
  content: counter(workflow, decimal-leading-zero);
  counter-increment: workflow;
  font-family: var(--mono);
  font-size: .72rem;
  font-weight: 800;
  padding-top: .16rem;
}

.workflow-item strong {
  color: var(--ink-black);
  display: block;
  font-family: var(--serif);
  font-size: 1.05rem;
  margin-bottom: .18rem;
}

.workflow-item span {
  color: var(--soft-grey);
  display: block;
  font-size: .82rem;
  line-height: 1.5;
}

/* Metrics, verdicts and content panels */
.metric-strip {
  border-bottom: 1px solid var(--border-dark);
  border-top: 1px solid var(--border-dark);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  margin: 1.4rem 0;
}

.metric-item {
  border-right: 1px solid var(--border-light);
  min-width: 0;
  padding: 1rem 1.05rem;
}

.metric-item:last-child {
  border-right: none;
}

.metric-label {
  color: var(--soft-grey);
  font-family: var(--mono);
  font-size: .61rem;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.metric-value {
  color: var(--ink-black);
  font-family: var(--serif);
  font-size: clamp(1.4rem, 3vw, 2.1rem);
  font-weight: 600;
  line-height: 1.1;
  margin-top: .36rem;
  overflow-wrap: anywhere;
}

.metric-note {
  color: var(--soft-grey);
  font-size: .69rem;
  line-height: 1.35;
  margin-top: .32rem;
}

.verdict-panel {
  background: var(--paper-highlight);
  border: 1px solid var(--border-light);
  border-top: 4px solid var(--warning-muted);
  min-height: 100%;
  padding: 1.25rem 1.35rem;
}

.verdict-panel.reliable { border-top-color: var(--success-muted); }
.verdict-panel.misleading { border-top-color: var(--danger-muted); }
.verdict-panel.uncertain { border-top-color: var(--warning-muted); }

.verdict-label {
  color: var(--soft-grey);
  font-family: var(--mono);
  font-size: .66rem;
  font-weight: 800;
  letter-spacing: .11em;
  text-transform: uppercase;
}

.verdict-title {
  color: var(--ink-black);
  font-family: var(--serif);
  font-size: clamp(1.8rem, 3.5vw, 3rem);
  line-height: 1;
  margin: .65rem 0 .55rem;
}

.verdict-panel p {
  color: var(--deep-brown);
  font-size: .88rem;
  margin: 0;
}

.verdict-probability {
  align-items: baseline;
  border-top: 1px solid var(--border-light);
  display: flex;
  gap: .55rem;
  margin-top: 1rem;
  padding-top: .8rem;
}

.verdict-probability strong {
  color: var(--ink-black);
  font-family: var(--serif);
  font-size: 1.7rem;
}

.verdict-probability span {
  color: var(--soft-grey);
  font-family: var(--mono);
  font-size: .64rem;
  text-transform: uppercase;
}

.reading-panel {
  border-left-color: var(--ink-black);
}

.reading-panel p {
  color: var(--charcoal);
  font-family: var(--serif);
  font-size: 1.08rem;
  line-height: 1.82;
  margin: .6rem 0 0;
  overflow-wrap: anywhere;
}

.reading-meta {
  border-top: 1px solid var(--border-light);
  color: var(--soft-grey);
  font-family: var(--mono);
  font-size: .64rem;
  letter-spacing: .03em;
  margin-top: 1rem;
  padding-top: .7rem;
  text-transform: uppercase;
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.metadata-item {
  border-bottom: 1px solid var(--border-light);
  min-width: 0;
  padding: .82rem .9rem;
}

.metadata-item .label {
  color: var(--soft-grey);
  display: block;
  font-family: var(--mono);
  font-size: .59rem;
  font-weight: 800;
  letter-spacing: .08em;
  margin-bottom: .28rem;
  text-transform: uppercase;
}

.metadata-item .value {
  color: var(--charcoal);
  display: block;
  font-size: .82rem;
  overflow-wrap: anywhere;
}

.evidence-group {
  border-top: 1px solid var(--border-light);
  margin-top: .55rem;
  padding-top: .7rem;
}

.evidence-chip {
  background: var(--paper-secondary);
  border: 1px solid var(--border-light);
  border-radius: 2px;
  color: var(--deep-brown);
  display: inline-block;
  font-family: var(--mono);
  font-size: .67rem;
  margin: .18rem .18rem .18rem 0;
  padding: .33rem .46rem;
}

.evidence-chip.reliable { border-bottom: 2px solid var(--success-muted); }
.evidence-chip.misleading { border-bottom: 2px solid var(--danger-muted); }

.callout {
  background: var(--paper-secondary);
  border-left: 3px solid var(--editorial-brown);
  color: var(--deep-brown);
  font-size: .84rem;
  line-height: 1.58;
  margin: 1rem 0;
  padding: .8rem 1rem;
}

.callout strong {
  color: var(--ink-black);
}

.callout.warning {
  background: var(--warning-paper);
  border-left-color: var(--warning-muted);
}

.callout.danger {
  background: var(--danger-paper);
  border-left-color: var(--danger-muted);
}

.callout.success {
  background: var(--success-paper);
  border-left-color: var(--success-muted);
}

.empty-state {
  background: var(--paper-highlight);
  border: 1px dashed var(--muted-taupe);
  padding: 2.2rem;
  text-align: center;
}

.empty-state h3 {
  margin: 0 0 .45rem;
}

.empty-state p {
  color: var(--soft-grey);
  margin: 0;
}

.archive-row {
  background: var(--paper-highlight);
  border-bottom: 1px solid var(--border-dark);
  padding: 1rem .2rem;
}

.archive-row h3 {
  font-size: 1.15rem;
  margin: .28rem 0;
  overflow-wrap: anywhere;
}

.archive-meta {
  color: var(--soft-grey);
  font-family: var(--mono);
  font-size: .62rem;
  letter-spacing: .04em;
  text-transform: uppercase;
}

.archive-preview {
  color: var(--deep-brown);
  display: -webkit-box;
  font-family: var(--serif);
  font-size: .88rem;
  line-height: 1.55;
  margin-top: .4rem;
  overflow: hidden;
  overflow-wrap: anywhere;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

/* Native Streamlit widget restyling */
[data-testid="stMetric"] {
  background: transparent;
  border-bottom: 1px solid var(--border-light);
  border-radius: 0;
  box-shadow: none;
  padding: .75rem .15rem;
}

[data-testid="stMetricLabel"] {
  color: var(--soft-grey);
  font-family: var(--mono);
  font-size: .67rem;
  letter-spacing: .06em;
  text-transform: uppercase;
}

[data-testid="stMetricValue"] {
  color: var(--ink-black);
  font-family: var(--serif);
}

.stButton > button,
.stDownloadButton > button {
  background: transparent;
  border: 1px solid var(--ink-black);
  border-radius: 2px;
  box-shadow: none;
  color: var(--ink-black);
  font-size: .8rem;
  font-weight: 750;
  min-height: 44px;
  transition: background .18s ease, color .18s ease, border-color .18s ease;
}

.stButton > button[kind="primary"] {
  background: var(--ink-black);
  color: var(--paper-highlight);
}

.stButton > button p,
.stDownloadButton > button p {
  color: inherit !important;
}

button[kind="primary"] [data-testid="stMarkdownContainer"],
button[kind="primary"] [data-testid="stMarkdownContainer"] p {
  color: var(--paper-highlight) !important;
}

[data-testid="stFormSubmitButton"] button {
  background: var(--ink-black) !important;
  border-color: var(--ink-black) !important;
  color: var(--paper-highlight) !important;
}

[data-testid="stFormSubmitButton"] [data-testid="stMarkdownContainer"],
[data-testid="stFormSubmitButton"] [data-testid="stMarkdownContainer"] p {
  color: var(--paper-highlight) !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
  background: var(--deep-brown);
  border-color: var(--deep-brown);
  color: white;
}

.stButton > button:hover [data-testid="stMarkdownContainer"],
.stButton > button:hover [data-testid="stMarkdownContainer"] p,
.stDownloadButton > button:hover [data-testid="stMarkdownContainer"],
.stDownloadButton > button:hover [data-testid="stMarkdownContainer"] p {
  color: white !important;
}

.stButton > button:focus-visible,
.stDownloadButton > button:focus-visible,
input:focus-visible,
textarea:focus-visible,
[role="combobox"]:focus-visible,
a:focus-visible {
  outline: 3px solid rgba(138, 105, 61, .35) !important;
  outline-offset: 2px;
}

input, textarea,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div,
[data-baseweb="select"] > div {
  background: var(--paper-highlight) !important;
  border-color: var(--border-light) !important;
  border-radius: 2px !important;
  color: var(--charcoal) !important;
}

textarea {
  line-height: 1.55 !important;
}

[data-baseweb="tab-list"] {
  border-bottom: 1px solid var(--border-dark);
  gap: 0;
}

[data-baseweb="tab"] {
  background: transparent;
  border-radius: 0;
  color: var(--deep-brown);
  font-family: var(--mono);
  font-size: .67rem;
  letter-spacing: .06em;
  padding: .65rem 1rem;
  text-transform: uppercase;
}

[data-baseweb="tab"][aria-selected="true"] {
  background: var(--ink-black);
  color: var(--paper-highlight);
}

[data-testid="stFileUploaderDropzone"] {
  background: var(--paper-highlight);
  border: 1px dashed var(--muted-taupe);
  border-radius: 2px;
}

[data-testid="stDataFrame"] {
  border: 1px solid var(--border-light);
}

div[data-testid="stExpander"] {
  background: var(--paper-highlight);
  border: 1px solid var(--border-light);
  border-radius: 2px;
  box-shadow: none;
}

div[data-testid="stAlert"] {
  border-radius: 2px;
  box-shadow: none;
}

[data-testid="stImage"] {
  background: var(--paper-highlight);
  border: 1px solid var(--border-light);
  padding: .35rem;
}

[data-testid="stImage"] img {
  filter: saturate(.78) sepia(.06);
}

.js-plotly-plot,
[data-testid="stPlotlyChart"] {
  background: var(--paper-highlight);
}

.nl-footer {
  border-top: 1px solid var(--border-dark);
  color: var(--soft-grey);
  display: grid;
  font-family: var(--mono);
  font-size: .62rem;
  gap: .7rem;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.35fr);
  letter-spacing: .045em;
  margin-top: 3.5rem;
  padding-top: 1rem;
  text-transform: uppercase;
}

.nl-footer-context,
.nl-footer-owner {
  display: grid;
  gap: .3rem;
}

.nl-footer-context span:last-child,
.nl-footer-owner span:last-child {
  color: var(--editorial-brown);
}

.nl-footer-owner {
  text-align: right;
}

@media (max-width: 900px) {
  .block-container {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .nl-masthead,
  .page-hero,
  .section-heading {
    grid-template-columns: 1fr;
  }

  .nl-masthead {
    align-items: flex-start;
    gap: .5rem;
  }

  .nl-nav {
    justify-content: flex-start;
    gap: .05rem;
    overflow: visible;
    flex-wrap: wrap;
  }

  .nl-nav a {
    font-size: .69rem;
    padding: .42rem .48rem .36rem;
  }

  .nl-nav a.nl-nav-cta {
    margin-left: 0;
  }

  [data-testid="stTopNavLinkContainer"] {
    overflow-x: auto;
    overscroll-behavior-inline: contain;
    scrollbar-width: thin;
  }

  .editorial-hero {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .editorial-hero-art {
    border-left: none;
    border-top: 1px solid var(--border-dark);
    max-height: 310px;
    min-height: 230px;
  }

  .editorial-hero-copy {
    padding: 2rem 1.35rem;
  }

  .editorial-hero h1 {
    font-size: clamp(2.35rem, 11.5vw, 4rem);
  }

  .metric-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .metric-item:nth-child(2n) {
    border-right: none;
  }

  .metric-item {
    border-bottom: 1px solid var(--border-light);
  }

  .nl-footer {
    grid-template-columns: 1fr;
    gap: .35rem;
  }

  .nl-footer-owner {
    margin-top: .35rem;
    text-align: left;
  }
}

@media (max-width: 560px) {
  .nl-descriptor {
    max-width: 160px;
    text-align: right;
  }

  .editorial-hero-copy {
    padding: 1.35rem;
  }

  .page-hero h1 {
    font-size: 2.75rem;
  }

  .metric-strip,
  .metadata-grid {
    grid-template-columns: 1fr;
  }

  .metric-item,
  .metric-item:nth-child(2n) {
    border-right: none;
  }

  .editorial-strip {
    text-align: left;
  }

  .editorial-strip + .section-heading {
    margin-top: 6.8rem;
  }

  .hero-actions {
    flex-direction: column;
    gap: .45rem;
    margin-top: 1rem;
  }

  .editorial-button {
    width: 100%;
  }

  .st-key-nl_hero_actions {
    width: 100%;
  }

  .st-key-nl_hero_actions [data-testid="stPageLink-NavLink"] {
    flex: 1 1 100%;
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  * { transition: none !important; animation: none !important; }
}
</style>
"""


def apply_theme() -> None:
    """Apply the shared design system once for the current page render."""

    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
