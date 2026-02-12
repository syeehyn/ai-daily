import type { Paper } from "@/lib/types";

const CJK_RE = /[\u3400-\u9FFF]/;

export function hasCJK(text: string): boolean {
  return CJK_RE.test(text || "");
}

export function enSummary(paper: Paper): string {
  const s = (paper.summary || "").trim();
  if (s && !hasCJK(s)) return s;
  const tags = (paper.tags || []).slice(0, 3).join(", ");
  const tagPart = tags ? ` Focus: ${tags}.` : "";
  return `${paper.title}.${tagPart} See full note for methods, results, and takeaways.`;
}

export function enIssueTitle(date: string, zhTitle?: string): string {
  if (!zhTitle) return `AI Daily Digest - ${date}`;
  return hasCJK(zhTitle) ? `AI Daily Digest - ${date}` : zhTitle;
}

export function enTrend(line: string): string {
  if (!hasCJK(line)) return line;
  return "Trend insight from today’s digest (English detail is being expanded in pipeline).";
}
