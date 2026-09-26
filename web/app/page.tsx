import Link from "next/link";

import { documentationLinks, repositoryPath, repositoryUrl } from "./site-config";

const features = [
  ["Summarise", "Generate a deterministic extractive reading view while keeping the classifier independent from the summary."],
  ["Compare ledgers", "Evaluate the visible Reference note and Article account with a synthetic-trained linear pipeline."],
  ["Calibrate", "Convert the score with model-bound Platt calibration and abstain outside the supported format."],
  ["Explain", "Review calibrated confidence and signed feature contributions instead of receiving an unexplained label."],
  ["Review", "Record evidence, notes, source URLs and a human editorial assessment in a private session workflow."],
  ["Monitor", "Inspect privacy-safe newsroom analytics and lightweight drift indicators without automatic retraining."],
] as const;

export default function Home() {
  return (
    <main id="main-content">
      <section className="hero sectionShell" aria-labelledby="hero-title">
        <div className="heroCopy">
          <p className="eyebrow">The synthetic news intelligence desk</p>
          <h1 id="hero-title">Compare transparently.<br />Keep the scope visible.</h1>
          <p className="dek">
            NewsLens AI combines article extraction, focused summarisation and an explainable
            synthetic ledger-consistency signal in one editorial workspace.
          </p>
          <div className="buttonRow">
            <Link className="button primary" href="/app">Open NewsLens AI</Link>
            <a className="button secondary" href={repositoryUrl}>View source on GitHub</a>
          </div>
          <p className="technicalLine">STREAMLIT · SYNTHETIC DATA · LOGISTIC REGRESSION · SHAPED FOR REVIEW</p>
        </div>
        <div className="heroArtwork" aria-label="Abstract editorial illustration">
          <div className="paperCard">
            <span>THE NEWS INTELLIGENCE DESK</span>
            <h2>Signal, context and uncertainty.</h2>
            <div className="paperRules" aria-hidden="true"><i /><i /><i /><i /></div>
          </div>
          <div className="lens" aria-hidden="true"><span>✓</span></div>
        </div>
      </section>

      <section className="metrics" aria-label="Measured project facts">
        <div><strong>6</strong><span>product areas</span></div>
        <div><strong>24,000</strong><span>synthetic articles</span></div>
        <div><strong>1,200</strong><span>locked final-test rows</span></div>
        <div><strong>1.000</strong><span>final-test macro-F1</span></div>
      </section>

      <section className="sectionShell sectionBlock" aria-labelledby="features-title">
        <div className="sectionHeading">
          <div><p className="eyebrow">Inside the desk</p><h2 id="features-title">A review workflow, not a truth machine.</h2></div>
          <p>Every output is framed as a bounded synthetic comparison that a reader can inspect and verify independently.</p>
        </div>
        <div className="featureGrid">
          {features.map(([title, body], index) => (
            <article key={title}>
              <span>0{index + 1}</span>
              <h3>{title}</h3>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="methodology" className="method sectionShell sectionBlock" aria-labelledby="method-title">
        <div>
          <p className="eyebrow">Methodology</p>
          <h2 id="method-title">Two independent analysis branches.</h2>
          <p>The cleaned source article flows to summarisation and synthetic ledger comparison separately. The classifier never consumes the generated summary.</p>
        </div>
        <ol className="methodSteps">
          <li><strong>Ingest</strong><span>Text, public URL, TXT or text-based PDF.</span></li>
          <li><strong>Prepare</strong><span>Validate, extract, clean and calculate article statistics.</span></li>
          <li><strong>Analyse</strong><span>Summarise; compare visible fields; calibrate; calculate local contributions.</span></li>
          <li><strong>Review</strong><span>Apply abstention, record human evidence and inspect session-local analytics and drift.</span></li>
        </ol>
      </section>

      <section id="responsible-use" className="responsibility sectionShell sectionBlock" aria-labelledby="responsibility-title">
        <p className="eyebrow">Responsible use</p>
        <h2 id="responsibility-title">A synthetic consistency signal is not a verified fact-check.</h2>
        <p>NewsLens AI recognizes patterns in an independently authored fictional benchmark. It does not retrieve evidence, establish objective truth, or replace journalists, researchers or professional fact-checkers.</p>
        <ul>
          <li>Calibrated confidence measures reliability against synthetic labels, not the probability that a real claim is true.</li>
          <li>Ordinary articles without both visible ledger blocks are outside automatic-classification scope.</li>
          <li>Public hosting uses a temporary, session-isolated archive; durable cloud history is not promised.</li>
        </ul>
      </section>

      <section id="documentation" className="sectionShell sectionBlock" aria-labelledby="docs-title">
        <div className="sectionHeading">
          <div><p className="eyebrow">Publication record</p><h2 id="docs-title">Documentation and research.</h2></div>
          <p>Code, the original synthetic benchmark, the public model, bound calibration, methodology and testing evidence are available through the canonical repository. Streamlit is the required deployment target; Vercel is not required.</p>
        </div>
        <div className="documentGrid">
          {documentationLinks.map(([label, path]) => (
            <a key={path} href={repositoryPath(path)}><span>{label}</span><b aria-hidden="true">↗</b></a>
          ))}
        </div>
      </section>
    </main>
  );
}
