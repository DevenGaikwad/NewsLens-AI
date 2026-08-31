import Link from "next/link";

import { documentationLinks, repositoryPath, repositoryUrl } from "./site-config";

const features = [
  ["Summarise", "Generate a focused extractive summary while keeping the classifier independent from the summary."],
  ["Assess language", "Estimate linguistic credibility risk with the packaged TF-IDF and Logistic Regression pipeline."],
  ["Calibrate", "Convert the model score with held-out Platt calibration and abstain below a validation-selected threshold."],
  ["Explain", "Review calibrated confidence and signed feature contributions instead of receiving an unexplained label."],
  ["Review", "Record evidence, notes, source URLs and a human editorial assessment in a private session workflow."],
  ["Monitor", "Inspect privacy-safe newsroom analytics and lightweight drift indicators without automatic retraining."],
] as const;

export default function Home() {
  return (
    <main id="main-content">
      <section className="hero sectionShell" aria-labelledby="hero-title">
        <div className="heroCopy">
          <p className="eyebrow">The news intelligence desk</p>
          <h1 id="hero-title">Investigate language.<br />Keep the uncertainty.</h1>
          <p className="dek">
            NewsLens AI combines article extraction, focused summarisation and an explainable
            linguistic credibility-risk estimate in one editorial workspace.
          </p>
          <div className="buttonRow">
            <Link className="button primary" href="/app">Open NewsLens AI</Link>
            <a className="button secondary" href={repositoryUrl}>View source on GitHub</a>
          </div>
          <p className="technicalLine">STREAMLIT · TF-IDF · LOGISTIC REGRESSION · SHAPED FOR REVIEW</p>
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
        <div><strong>56</strong><span>packaged checks</span></div>
        <div><strong>2,399</strong><span>untouched final-test rows</span></div>
        <div><strong>0.9921</strong><span>final-test macro-F1</span></div>
      </section>

      <section className="sectionShell sectionBlock" aria-labelledby="features-title">
        <div className="sectionHeading">
          <div><p className="eyebrow">Inside the desk</p><h2 id="features-title">A review workflow, not a truth machine.</h2></div>
          <p>Every output is framed as model evidence that a reader can inspect, question and verify independently.</p>
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
          <p>The cleaned source article flows to summarisation and classification separately. The classifier never consumes the generated summary, avoiding an unnecessary source of information loss.</p>
        </div>
        <ol className="methodSteps">
          <li><strong>Ingest</strong><span>Text, public URL, TXT or text-based PDF.</span></li>
          <li><strong>Prepare</strong><span>Validate, extract, clean and calculate article statistics.</span></li>
          <li><strong>Analyse</strong><span>Summarise; classify; calibrate confidence; calculate local contributions.</span></li>
          <li><strong>Review</strong><span>Apply abstention, record human evidence and inspect session-local analytics and drift.</span></li>
        </ol>
      </section>

      <section id="responsible-use" className="responsibility sectionShell sectionBlock" aria-labelledby="responsibility-title">
        <p className="eyebrow">Responsible use</p>
        <h2 id="responsibility-title">A linguistic risk estimate is not a verified fact-check.</h2>
        <p>NewsLens AI detects patterns correlated with its training data. It does not retrieve evidence, establish objective truth, or replace journalists, researchers or professional fact-checkers. Confirm important claims through independent primary sources.</p>
        <ul>
          <li>Calibrated confidence measures reliability against benchmark labels, not the probability that a claim is factually true.</li>
          <li>Satire, opinion, emerging events, multilingual text and unfamiliar domains can be misclassified.</li>
          <li>Public hosting uses a temporary, session-isolated archive; durable cloud history is not promised.</li>
        </ul>
      </section>

      <section id="documentation" className="sectionShell sectionBlock" aria-labelledby="docs-title">
        <div className="sectionHeading">
          <div><p className="eyebrow">Publication record</p><h2 id="docs-title">Documentation and research.</h2></div>
          <p>Code, methodology, testing evidence, issues, releases and deployment history are staged for the canonical public repository after the remaining release gates are cleared.</p>
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
