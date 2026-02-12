import type { Issue } from "@/lib/types";

type DigestSections = {
  highlights: string[];
  trends: string[];
  focus: Array<{ title: string; text: string }>;
};

function clean(line: string): string {
  return line
    .replace(/^[-*]\s*/, "")
    .replace(/^\d+\.\s*/, "")
    .replace(/^>\s*/, "")
    .trim();
}

export function parseDigest(issue: Issue): DigestSections {
  const raw = issue.digest || "";
  const lines = raw.split(/\r?\n/);

  const highlights: string[] = [];
  const trends: string[] = [];
  const focus: Array<{ title: string; text: string }> = [];

  let mode: "none" | "highlight" | "trend" | "focus" = "none";
  let currentFocus: { title: string; text: string } | null = null;

  for (const line0 of lines) {
    const line = line0.trim();
    if (!line) continue;

    if (line.includes("今日亮点")) {
      mode = "highlight";
      continue;
    }
    if (line.includes("趋势观察")) {
      if (currentFocus) focus.push(currentFocus);
      currentFocus = null;
      mode = "trend";
      continue;
    }
    if (line.includes("重点关注")) {
      if (currentFocus) focus.push(currentFocus);
      currentFocus = null;
      mode = "focus";
      continue;
    }
    if (line.startsWith("---") || line.startsWith("|")) continue;

    if (mode === "highlight") {
      if (line.startsWith("##")) continue;
      const text = clean(line);
      if (text) highlights.push(text);
      continue;
    }

    if (mode === "trend") {
      if (/^\d+\./.test(line) || /^[-*]\s/.test(line)) {
        const text = clean(line);
        if (text) trends.push(text);
      }
      continue;
    }

    if (mode === "focus") {
      if (line.startsWith("###")) {
        if (currentFocus) focus.push(currentFocus);
        currentFocus = { title: line.replace(/^###\s*/, "").trim(), text: "" };
        continue;
      }
      if (line.startsWith("→")) continue;
      if (!currentFocus) continue;
      const text = clean(line);
      if (text) currentFocus.text = currentFocus.text ? `${currentFocus.text} ${text}` : text;
    }
  }

  if (currentFocus) focus.push(currentFocus);

  if (!highlights.length) {
    highlights.push("今日核心更新已生成，但摘要段还未结构化。可直接查看下方 topic 速读。");
  }

  return { highlights, trends, focus };
}
