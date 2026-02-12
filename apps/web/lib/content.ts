import fs from "node:fs";
import path from "node:path";
import { Issue, Paper } from "@/lib/types";

const ROOT = path.resolve(process.cwd(), "../..");
const ISSUES_DIR = path.join(ROOT, "issues");

function parseFrontMatter(raw: string): { data: Record<string, string>; body: string } {
  if (!raw.startsWith("---\n")) return { data: {}, body: raw };
  const lines = raw.split("\n");
  const data: Record<string, string> = {};
  let end = -1;

  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (line.trim() === "---") {
      end = i;
      break;
    }
    const idx = line.indexOf(":");
    if (idx <= 0) continue;
    const key = line.slice(0, idx).trim().toLowerCase();
    const value = line.slice(idx + 1).trim().replace(/^"|"$/g, "");
    data[key] = value;
  }

  if (end === -1) return { data: {}, body: raw };
  return { data, body: lines.slice(end + 1).join("\n") };
}

function issueDates(): string[] {
  if (!fs.existsSync(ISSUES_DIR)) return [];
  return fs
    .readdirSync(ISSUES_DIR)
    .filter((entry) => /^\d{4}-\d{2}-\d{2}$/.test(entry) && fs.statSync(path.join(ISSUES_DIR, entry)).isDirectory())
    .sort((a, b) => (a < b ? 1 : -1));
}

function parsePaper(date: string, file: string): Paper {
  const id = file.replace(/\.md$/, "");
  const full = path.join(ISSUES_DIR, date, "papers", file);
  const raw = fs.readFileSync(full, "utf-8");
  const { data, body } = parseFrontMatter(raw);
  const title = data.title || body.match(/^#\s+(.+)$/m)?.[1] || id;
  const authors = data.authors || "Unknown authors";
  const summary = body
    .split("\n")
    .map((line) => line.trim())
    .find((line) => line && !line.startsWith("#") && !line.startsWith("-")) || "No summary.";
  const tagsRaw = data.tags || "";
  const tags = tagsRaw
    .replace(/\[|\]/g, "")
    .split(",")
    .map((tag) => tag.trim().replace(/^"|"$/g, ""))
    .filter(Boolean);

  const figuresDir = path.join(ISSUES_DIR, date, "assets", "figures");
  let image: string | undefined;
  if (fs.existsSync(figuresDir)) {
    const found = fs.readdirSync(figuresDir).find((name) => name.startsWith(`${id}.`));
    if (found) image = `/issues/${date}/assets/figures/${found}`;
  }

  return {
    id,
    title,
    authors,
    summary,
    tags,
    url: data.url || data.link || "",
    markdown: body.trim(),
    image
  };
}

function parseIssueFromFs(date: string): Issue {
  const digestPath = path.join(ISSUES_DIR, date, "digest.md");
  const digest = fs.existsSync(digestPath) ? fs.readFileSync(digestPath, "utf-8") : "";
  const papersDir = path.join(ISSUES_DIR, date, "papers");
  const paperFiles = fs.existsSync(papersDir)
    ? fs
        .readdirSync(papersDir)
        .filter((name) => name.endsWith(".md"))
        .sort()
    : [];
  const papers = paperFiles.map((file) => parsePaper(date, file));

  const title = digest.match(/^title:\s*"?(.+?)"?$/m)?.[1] || `AI Daily ${date}`;
  return { date, title, digest, papers };
}

function parseIssueFromAdapter(date: string, raw: string): Issue | null {
  try {
    const parsed = JSON.parse(raw) as Issue;
    if (!parsed.date || !Array.isArray(parsed.papers)) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function getIssues(): Issue[] {
  return issueDates().map((date) => {
    const adapterPath = path.join(ISSUES_DIR, date, "issue-data.json");
    if (fs.existsSync(adapterPath)) {
      const adapted = parseIssueFromAdapter(date, fs.readFileSync(adapterPath, "utf-8"));
      if (adapted) return adapted;
    }
    return parseIssueFromFs(date);
  });
}

export function getIssue(date: string): Issue | null {
  return getIssues().find((issue) => issue.date === date) ?? null;
}

export function getPaper(date: string, paperId: string): { issue: Issue; paper: Paper } | null {
  const issue = getIssue(date);
  if (!issue) return null;
  const paper = issue.papers.find((item) => item.id === paperId);
  if (!paper) return null;
  return { issue, paper };
}
