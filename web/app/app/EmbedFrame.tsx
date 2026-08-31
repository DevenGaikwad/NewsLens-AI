"use client";

import { useState } from "react";

export function EmbedFrame({ source, fallback }: { source: string; fallback: string }) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="embedFrame">
      {!loaded && <div className="embedLoading" role="status">Opening the NewsLens AI workspace…</div>}
      <iframe
        src={source}
        title="NewsLens AI Streamlit application"
        loading="eager"
        onLoad={() => setLoaded(true)}
        allow="clipboard-write"
        referrerPolicy="strict-origin-when-cross-origin"
        sandbox="allow-downloads allow-forms allow-popups allow-same-origin allow-scripts"
      />
      <noscript>
        <p><a href={fallback}>Open NewsLens AI in this tab</a>.</p>
      </noscript>
    </div>
  );
}
