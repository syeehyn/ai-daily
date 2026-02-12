import Link from "next/link";
import { ReactNode } from "react";

function cx(...parts: Array<string | undefined | false>) {
  return parts.filter(Boolean).join(" ");
}

export function TopNav() {
  return (
    <header className="sticky top-0 z-20 border-b border-border/70 bg-bg/85 backdrop-blur">
      <nav className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4" aria-label="Main">
        <Link href="/" className="text-sm font-semibold tracking-tight hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
          AI Daily v2
        </Link>
        <div className="flex items-center gap-4 text-sm text-fgMuted">
          <a
            href="https://huggingface.co/papers"
            target="_blank"
            rel="noreferrer"
            className="hover:text-fg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            HF Papers
          </a>
        </div>
      </nav>
    </header>
  );
}

export function Button({
  children,
  href,
  variant = "primary"
}: {
  children: ReactNode;
  href?: string;
  variant?: "primary" | "secondary" | "ghost";
}) {
  const base = "inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors duration-base focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";
  const cls =
    variant === "primary"
      ? "border border-accent bg-accent text-inverse hover:bg-fg"
      : variant === "secondary"
        ? "border border-borderStrong bg-bgMuted text-fg hover:bg-accentSoft"
        : "border border-transparent text-fgMuted hover:border-border hover:text-fg";

  if (href) {
    return (
      <Link href={href} className={cx(base, cls)}>
        {children}
      </Link>
    );
  }

  return <button className={cx(base, cls)}>{children}</button>;
}

export function TextLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <Link
      href={href}
      className="underline decoration-borderStrong underline-offset-4 transition-colors duration-fast hover:decoration-fg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
    >
      {children}
    </Link>
  );
}

export function Chip({ children }: { children: ReactNode }) {
  return <span className="inline-flex rounded-full border border-border px-2.5 py-1 text-xs text-fgMuted">{children}</span>;
}

export function RecommendationCard({
  title,
  summary,
  href,
  date
}: {
  title: string;
  summary: string;
  href: string;
  date: string;
}) {
  return (
    <article className="group rounded-lg border border-border bg-bgMuted/50 p-5 transition-all duration-base hover:border-borderStrong hover:bg-bgMuted">
      <p className="mb-3 text-xs uppercase tracking-[0.12em] text-fgMuted">{date}</p>
      <h3 className="mb-2 text-base font-semibold leading-tight">{title}</h3>
      <p className="mb-4 line-clamp-3 text-sm text-fgMuted">{summary}</p>
      <TextLink href={href}>Read article</TextLink>
    </article>
  );
}

export function FooterColumns() {
  return (
    <footer className="mt-20 border-t border-border">
      <div className="mx-auto grid w-full max-w-6xl gap-8 px-6 py-10 text-sm sm:grid-cols-3">
        <div>
          <h2 className="mb-3 font-semibold">OpenClaw Data</h2>
          <ul className="space-y-2 text-fgMuted">
            <li>Paper ingestion</li>
            <li>X snapshot</li>
            <li>Image fallback pipeline</li>
          </ul>
        </div>
        <div>
          <h2 className="mb-3 font-semibold">Codex Design</h2>
          <ul className="space-y-2 text-fgMuted">
            <li>Next.js app router</li>
            <li>Editorial grayscale UI</li>
            <li>Accessible component system</li>
          </ul>
        </div>
        <div>
          <h2 className="mb-3 font-semibold">Project</h2>
          <ul className="space-y-2 text-fgMuted">
            <li><a className="hover:text-fg" href="https://github.com">Repository</a></li>
            <li><a className="hover:text-fg" href="/">Archive</a></li>
            <li><a className="hover:text-fg" href="https://huggingface.co/papers">Source feed</a></li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
