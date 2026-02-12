"use client";

import { useEffect, useState } from "react";

export type Lang = "zh" | "en";

export function detectLang(): Lang {
  if (typeof window === "undefined") return "zh";
  const saved = window.localStorage.getItem("ai-daily-lang");
  if (saved === "zh" || saved === "en") return saved;
  return (window.navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en";
}

export function useLang() {
  const [lang, setLang] = useState<Lang>("zh");

  useEffect(() => {
    const current = detectLang();
    setLang(current);
    document.documentElement.lang = current === "zh" ? "zh-CN" : "en";
    window.localStorage.setItem("ai-daily-lang", current);
  }, []);

  function changeLang(next: Lang) {
    setLang(next);
    if (typeof window !== "undefined") {
      window.localStorage.setItem("ai-daily-lang", next);
      document.documentElement.lang = next === "zh" ? "zh-CN" : "en";
    }
  }

  return { lang, setLang: changeLang };
}

export function pick(zh: string, en: string, lang: Lang) {
  return lang === "zh" ? zh : en;
}
