import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import "./styles.css";
import { MobileNavigation } from "./MobileNavigation";
import { repositoryUrl } from "./site-config";

export const metadata: Metadata = {
  title: {
    default: "NewsLens AI — Editorial intelligence with accountable AI",
    template: "%s | NewsLens AI",
  },
  description:
    "Summarise news articles, estimate linguistic credibility risk, and inspect transparent model evidence.",
  authors: [{ name: "Deven Sachin Gaikwad" }],
  creator: "Deven Sachin Gaikwad",
  publisher: "Deven Sachin Gaikwad",
  other: {
    copyright: "© 2026 Deven Sachin Gaikwad. All Rights Reserved.",
  },
};

function Navigation() {
  const links = (
    <>
      <Link href="/#methodology">Methodology</Link>
      <Link href="/#responsible-use">Responsible use</Link>
      <Link href="/#documentation">Documentation</Link>
      <a href={repositoryUrl}>GitHub</a>
      <Link className="navCta" href="/app">Open application</Link>
    </>
  );

  return (
    <header className="siteHeader">
      <div className="headerInner">
        <Link className="brand" href="/" aria-label="NewsLens AI home">
          <img src="/logo.svg" alt="" width="42" height="42" />
          <span>NewsLens AI</span>
        </Link>
        <nav className="desktopNav" aria-label="Primary navigation">{links}</nav>
        <MobileNavigation />
      </div>
    </header>
  );
}

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <a className="skipLink" href="#main-content">Skip to content</a>
        <Navigation />
        {children}
        <footer className="siteFooter">
          <div>
            <strong>NewsLens AI</strong>
            <span>NewsLens AI · Designed and developed by Deven Sachin Gaikwad</span>
            <span>© 2026 Deven Sachin Gaikwad. All Rights Reserved.</span>
          </div>
          <p>Research software — not a replacement for professional fact-checking.</p>
        </footer>
      </body>
    </html>
  );
}
