"use client";

import Link from "next/link";
import { useRef } from "react";

import { repositoryUrl } from "./site-config";

export function MobileNavigation() {
  const menu = useRef<HTMLDetailsElement>(null);
  const close = () => menu.current?.removeAttribute("open");

  return (
    <details className="mobileMenu" ref={menu}>
      <summary aria-label="Open navigation menu">Menu</summary>
      <nav aria-label="Mobile navigation" onClick={close}>
        <Link href="/#methodology">Methodology</Link>
        <Link href="/#responsible-use">Responsible use</Link>
        <Link href="/#documentation">Documentation</Link>
        <a href={repositoryUrl}>GitHub</a>
        <Link className="navCta" href="/app">Open application</Link>
      </nav>
    </details>
  );
}
