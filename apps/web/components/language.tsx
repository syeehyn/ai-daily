"use client";

import { ReactNode } from "react";
import { pick, useLang } from "@/lib/i18n";

export function LanguageToggle() {
  const { lang, setLang } = useLang();

  return (
    <div className="inline-flex items-center rounded-md border border-border p-1" role="group" aria-label="Language toggle">
      <button
        type="button"
        onClick={() => setLang("zh")}
        className={`rounded px-2 py-1 text-xs ${lang === "zh" ? "bg-fg text-bg" : "text-fgMuted"}`}
        aria-pressed={lang === "zh"}
      >
        中
      </button>
      <button
        type="button"
        onClick={() => setLang("en")}
        className={`rounded px-2 py-1 text-xs ${lang === "en" ? "bg-fg text-bg" : "text-fgMuted"}`}
        aria-pressed={lang === "en"}
      >
        EN
      </button>
    </div>
  );
}

export function T({ zh, en }: { zh: string; en: string }) {
  const { lang } = useLang();
  return <>{pick(zh, en, lang)}</>;
}

export function TNode({ zh, en }: { zh: ReactNode; en: ReactNode }) {
  const { lang } = useLang();
  return <>{lang === "zh" ? zh : en}</>;
}
