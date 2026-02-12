import type { Metadata } from "next";
import Script from "next/script";
import { ThemeToggle } from "@/components/theme-toggle";
import { TopNav } from "@/components/ui";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Daily v2",
  description: "Editorial daily AI paper briefing"
};

const initTheme = `
(() => {
  const stored = localStorage.getItem('ai-daily-theme');
  const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const shouldDark = stored ? stored === 'dark' : dark;
  document.documentElement.classList.toggle('dark', shouldDark);
})();
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Script id="theme-init" strategy="beforeInteractive">{initTheme}</Script>
        <TopNav />
        <div className="mx-auto flex w-full max-w-6xl justify-end px-6 pt-4">
          <ThemeToggle />
        </div>
        {children}
      </body>
    </html>
  );
}
