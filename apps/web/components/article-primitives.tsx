import { ReactNode } from "react";

export function ArticleHeading({ level = 2, children }: { level?: 2 | 3; children: ReactNode }) {
  if (level === 3) {
    return <h3 className="mt-8 text-xl font-semibold leading-tight">{children}</h3>;
  }
  return <h2 className="mt-10 text-2xl font-semibold leading-tight">{children}</h2>;
}

export function ArticleParagraph({ children }: { children: ReactNode }) {
  return <p className="mt-4 leading-7 text-fg">{children}</p>;
}

export function ArticleList({ items }: { items: string[] }) {
  return (
    <ul className="mt-4 list-disc space-y-2 pl-6 text-fg">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export function ArticleQuote({ children }: { children: ReactNode }) {
  return (
    <blockquote className="mt-6 border-l-2 border-borderStrong pl-4 italic text-fgMuted">
      {children}
    </blockquote>
  );
}

export function ArticleCallout({ children }: { children: ReactNode }) {
  return <aside className="mt-6 rounded-md border border-borderStrong bg-bgMuted px-4 py-3 text-sm">{children}</aside>;
}

export function ArticleCode({ children }: { children: ReactNode }) {
  return (
    <pre className="mt-6 overflow-x-auto rounded-md border border-border bg-[#0f0f10] p-4 text-sm text-[#e7e7e2]">
      <code>{children}</code>
    </pre>
  );
}

export function FigureCaption({ children }: { children: ReactNode }) {
  return <figcaption className="mt-2 text-xs uppercase tracking-[0.08em] text-fgMuted">{children}</figcaption>;
}
