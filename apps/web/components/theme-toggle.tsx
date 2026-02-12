"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const current = document.documentElement.classList.contains("dark") ? "dark" : "light";
    setTheme(current);
  }, []);

  function toggle() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.classList.toggle("dark", next === "dark");
    localStorage.setItem("ai-daily-theme", next);
  }

  return (
    <button
      type="button"
      onClick={toggle}
      className="rounded-md border border-border px-3 py-2 text-xs font-medium transition-colors duration-base hover:border-borderStrong focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      aria-label="Toggle color theme"
    >
      {theme === "dark" ? "Light" : "Dark"}
    </button>
  );
}
