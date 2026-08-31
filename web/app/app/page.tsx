import type { Metadata } from "next";

import { EmbedFrame } from "./EmbedFrame";
import { streamlitUrl } from "../site-config";

export const metadata: Metadata = {
  title: "Application",
  description: "Use the NewsLens AI Streamlit analysis workspace.",
};

function embeddedUrl(source: string): string {
  const url = new URL(source);
  url.searchParams.set("embed", "true");
  return url.toString();
}

export default function ApplicationPage() {
  const source = streamlitUrl();
  return (
    <main id="main-content" className="appPage">
      <section className="appIntro sectionShell">
        <div>
          <p className="eyebrow">Live analysis workspace</p>
          <h1>NewsLens AI</h1>
        </div>
        <div className="appFallback">
          <p>The functional Python/ML product runs below. If embedding is restricted or interrupted:</p>
          <a className="button secondary sameTabFallback" href={source}>
            Open Streamlit in this tab
          </a>
        </div>
      </section>
      <EmbedFrame source={embeddedUrl(source)} fallback={source} />
    </main>
  );
}
