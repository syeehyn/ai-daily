import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--color-bg)",
        bgMuted: "var(--color-bg-muted)",
        fg: "var(--color-fg)",
        fgMuted: "var(--color-fg-muted)",
        border: "var(--color-border)",
        borderStrong: "var(--color-border-strong)",
        accent: "var(--color-accent)",
        accentSoft: "var(--color-accent-soft)",
        inverse: "var(--color-inverse)"
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)"
      },
      transitionDuration: {
        fast: "var(--duration-fast)",
        base: "var(--duration-base)"
      }
    }
  },
  plugins: []
};

export default config;
