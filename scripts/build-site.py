#!/usr/bin/env python3
"""Build static pages for AI Daily without third-party dependencies."""

from __future__ import annotations

import datetime as dt
import html
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ISSUES_DIR = ROOT / "issues"
TEMPLATE_PATH = ROOT / "templates" / "daily-template.html"
ARCHIVE_INDEX_PATH = ROOT / "index.html"

ARCHIVE_START = "<!-- ARCHIVE_LIST_START -->"
ARCHIVE_END = "<!-- ARCHIVE_LIST_END -->"
ISSUE_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r'https?://[^\s)>"]+')

FOCUS_KEYWORDS = {
    "agent rl",
    "scaling rl",
    "rl",
    "rlvr",
    "grpo",
    "multi-agent",
    "tool-use",
    "reinforcement learning",
}


def escape(value: str) -> str:
    return html.escape(value or "", quote=True)


def is_issue_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    if not ISSUE_DATE_RE.match(path.name):
        return False
    try:
        dt.date.fromisoformat(path.name)
    except ValueError:
        return False
    return True


def parse_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    lines = text.splitlines()
    front = {}
    end_idx = None
    for idx in range(1, len(lines)):
        line = lines[idx].strip()
        if line == "---":
            end_idx = idx
            break
        if ":" in line:
            key, val = line.split(":", 1)
            front[key.strip().lower()] = val.strip()

    if end_idx is None:
        return {}, text

    body = "\n".join(lines[end_idx + 1 :])
    return front, body


def read_markdown(path: Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8")
    front, body = parse_front_matter(text)
    lines = body.splitlines()

    title = front.get("title", "").strip()
    if not title:
        for line in lines:
            if line.strip().startswith("#"):
                title = line.lstrip("# ").strip()
                break

    authors = front.get("authors", "").strip()
    tags_raw = front.get("tags", "").strip()
    link = (front.get("link") or front.get("url") or "").strip()
    summary = (
        front.get("summary")
        or front.get("brief")
        or front.get("comment")
        or front.get("one_sentence_summary")
        or ""
    ).strip()

    paragraphs: List[str] = []
    current = []
    for raw in lines:
        line = raw.strip()
        lower = line.lower()
        if not line:
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue

        if lower.startswith("authors:") and not authors:
            authors = line.split(":", 1)[1].strip()
            continue
        if lower.startswith("tags:") and not tags_raw:
            tags_raw = line.split(":", 1)[1].strip()
            continue
        if lower.startswith("link:") and not link:
            link = line.split(":", 1)[1].strip()
            continue

        if line.startswith("#"):
            continue

        if not summary and (lower.startswith("summary:") or lower.startswith("brief:")):
            summary = line.split(":", 1)[1].strip()
            continue

        current.append(line)

    if current:
        paragraphs.append(" ".join(current).strip())

    if not summary and paragraphs:
        summary = paragraphs[0]

    if not link:
        url_match = URL_RE.search(body)
        if url_match:
            link = url_match.group(0)

    if not title:
        title = path.stem.replace("-", " ").title()
    if not authors:
        authors = "Unknown authors"
    if not summary:
        summary = "No summary provided yet."

    tags = parse_tags(tags_raw)
    if not tags:
        tags = infer_tags_from_text(" ".join([title, summary, body]))

    return {
        "title": title,
        "authors": authors,
        "summary": summary,
        "tags": tags,
        "link": link,
        "path": path,
    }


def parse_tags(tags_raw: str) -> List[str]:
    tags_raw = tags_raw.strip()
    if not tags_raw:
        return []
    tags_raw = tags_raw.strip("[]")
    if "," in tags_raw:
        items = [t.strip() for t in tags_raw.split(",")]
    else:
        items = [t.strip() for t in tags_raw.split()]
    return [tag for tag in items if tag]


def infer_tags_from_text(text: str) -> List[str]:
    lower = text.lower()
    candidates = []
    mapping = {
        "agent": "Agent",
        "rl": "RL",
        "scaling": "Scaling",
        "llm": "LLM",
        "benchmark": "Benchmark",
        "multimodal": "Multimodal",
        "tool": "Tool-use",
        "reason": "Reasoning",
    }
    for key, label in mapping.items():
        if key in lower:
            candidates.append(label)
    return candidates[:4]


def safe_excerpt(text: str, max_len: int = 160) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def build_paper_card(paper: Dict[str, object], rank: int) -> str:
    tags = paper.get("tags", []) or []
    tags_html = "".join(f'<span class="tag">{escape(str(tag))}</span>' for tag in tags)
    link = str(paper.get("link") or "").strip()
    if link:
        link_html = f'<a href="{escape(link)}" target="_blank" rel="noopener">Read paper</a>'
    else:
        link_html = '<span class="paper-authors">Link pending</span>'

    return (
        '<article class="paper-card">'
        f'<div class="paper-rank">TOP {rank:02d}</div>'
        f'<h3 class="paper-title">{escape(str(paper["title"]))}</h3>'
        f'<p class="paper-authors">{escape(str(paper["authors"]))}</p>'
        f'<p class="paper-brief">{escape(safe_excerpt(str(paper["summary"]), 180))}</p>'
        f'<div class="tags">{tags_html}</div>'
        f"{link_html}"
        "</article>"
    )


def is_focus_paper(paper: Dict[str, object]) -> bool:
    text = " ".join(
        [
            str(paper.get("title", "")),
            str(paper.get("summary", "")),
            " ".join(str(tag) for tag in paper.get("tags", []) or []),
        ]
    ).lower()
    return any(keyword in text for keyword in FOCUS_KEYWORDS)


def build_focus_section(papers: List[Dict[str, object]]) -> str:
    focus_candidates = [p for p in papers if is_focus_paper(p)]
    if not focus_candidates:
        return (
            '<h3 class="focus-title">Agent RL / Scaling RL Radar</h3>'
            "<p>今天的 Top 10 中尚未出现强匹配焦点论文，建议继续关注 RLVR 与多智能体协同方向。</p>"
        )

    top = focus_candidates[:3]
    bullets = []
    for paper in top:
        bullets.append(
            "<li>"
            f"<strong>{escape(str(paper['title']))}</strong>: "
            f"{escape(safe_excerpt(str(paper['summary']), 120))}"
            "</li>"
        )

    return (
        '<h3 class="focus-title">Agent RL / Scaling RL Deep Dive</h3>'
        "<p>以下论文与 Agent RL / Scaling RL 相关，适合优先精读并跟踪可复现价值。</p>"
        f"<ul>{''.join(bullets)}</ul>"
    )


def build_takeaways(papers: List[Dict[str, object]]) -> str:
    if not papers:
        return "<p>暂无论文数据。</p>"

    tag_counter = Counter()
    for paper in papers:
        for tag in paper.get("tags", []) or []:
            tag_counter[str(tag)] += 1

    top_tags = [tag for tag, _ in tag_counter.most_common(3)]
    highlight = papers[0]

    items = [
        f"<li>今日共筛选 <strong>{len(papers)}</strong> 篇论文，建议先读 TOP 3 获取全局脉络。</li>",
        f"<li>高频主题：<strong>{escape(', '.join(top_tags) if top_tags else 'Agent / RL / LLM')}</strong>。</li>",
        f"<li>第一优先论文：<strong>{escape(str(highlight['title']))}</strong>。</li>",
    ]
    return "<ul>" + "".join(items) + "</ul>"


def replace_tokens(template: str, values: Dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def render_issue_page(issue_date: str, papers: List[Dict[str, object]], template: str) -> str:
    top_papers = papers[:10]
    cards = "".join(build_paper_card(paper, idx + 1) for idx, paper in enumerate(top_papers))
    if not cards:
        cards = '<div class="takeaway">No papers found for this date.</div>'

    values = {
        "PAGE_TITLE": f"AI Daily {issue_date}",
        "DATE": issue_date,
        "PAPER_COUNT": str(len(papers)),
        "TAGLINE": "Frontier AI Papers, Curated Like A Sci-Fi Journal",
        "TOP_PAPERS": cards,
        "FOCUS_AREA": build_focus_section(top_papers),
        "TAKEAWAYS": build_takeaways(top_papers),
    }
    return replace_tokens(template, values)


def build_archive_card(issue_date: str, papers: List[Dict[str, object]]) -> str:
    tags = Counter()
    for paper in papers:
        for tag in paper.get("tags", []) or []:
            tags[str(tag)] += 1
    topic = ", ".join(tag for tag, _ in tags.most_common(3)) or "Agent RL, Scaling RL"

    return (
        f'<a class="issue-card" href="issues/{issue_date}/index.html">'
        f'<div class="issue-date">{escape(issue_date)}</div>'
        f'<p class="issue-count">{len(papers)} papers</p>'
        f'<p class="issue-topic">Top topics: {escape(topic)}</p>'
        "</a>"
    )


def update_archive_index(issues_payload: List[Tuple[str, List[Dict[str, object]]]]) -> None:
    if not ARCHIVE_INDEX_PATH.exists():
        raise FileNotFoundError(f"Archive index not found: {ARCHIVE_INDEX_PATH}")

    original = ARCHIVE_INDEX_PATH.read_text(encoding="utf-8")
    if ARCHIVE_START not in original or ARCHIVE_END not in original:
        raise ValueError("Archive markers not found in index.html")

    if issues_payload:
        cards = "\n      ".join(build_archive_card(date, papers) for date, papers in issues_payload)
    else:
        cards = '<div class="empty">暂无已发布 issue，运行 <code>python3 scripts/build-site.py</code> 后会自动生成。</div>'

    before, rest = original.split(ARCHIVE_START, 1)
    _, after = rest.split(ARCHIVE_END, 1)
    updated = before + ARCHIVE_START + "\n      " + cards + "\n      " + ARCHIVE_END + after
    ARCHIVE_INDEX_PATH.write_text(updated, encoding="utf-8")


def main() -> None:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template missing: {TEMPLATE_PATH}")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    ISSUES_DIR.mkdir(parents=True, exist_ok=True)

    issue_dirs = sorted((p for p in ISSUES_DIR.iterdir() if is_issue_dir(p)), key=lambda p: p.name, reverse=True)
    issues_payload: List[Tuple[str, List[Dict[str, object]]]] = []

    for issue_dir in issue_dirs:
        papers_dir = issue_dir / "papers"
        md_files = sorted(papers_dir.glob("*.md")) if papers_dir.exists() else []
        papers = [read_markdown(md) for md in md_files]
        issue_html = render_issue_page(issue_dir.name, papers, template)
        (issue_dir / "index.html").write_text(issue_html, encoding="utf-8")
        issues_payload.append((issue_dir.name, papers))

    update_archive_index(issues_payload)
    print(f"Built {len(issues_payload)} issue page(s).")


if __name__ == "__main__":
    main()
