import type { Metadata } from "next";
import Script from "next/script";
import { ThemeToggle } from "@/components/theme-toggle";
import { TopNav } from "@/components/ui";
import { LanguageToggle } from "@/components/language";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Daily",
  description: "Daily AI briefing"
};

const initTheme = `
(() => {
  const storedTheme = localStorage.getItem('ai-daily-theme');
  const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const shouldDark = storedTheme ? storedTheme === 'dark' : dark;
  document.documentElement.classList.toggle('dark', shouldDark);

  const storedLang = localStorage.getItem('ai-daily-lang');
  const lang = storedLang ? storedLang : ((navigator.language || '').toLowerCase().startsWith('zh') ? 'zh' : 'en');
  localStorage.setItem('ai-daily-lang', lang);
  document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
})();
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Script id="theme-init" strategy="beforeInteractive">{initTheme}</Script>
        <TopNav />
        <div className="mx-auto flex w-full max-w-6xl justify-end gap-2 px-6 pt-4">
          <LanguageToggle />
          <ThemeToggle />
        </div>
        {children}
      </body>
    </html>
  );
}
