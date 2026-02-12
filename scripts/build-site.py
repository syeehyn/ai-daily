#!/usr/bin/env python3
"""Build static pages for AI Daily without third-party dependencies."""

from __future__ import annotations

import datetime as dt
import html
import json
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
LOCAL_X_DIR = Path.home() / ".openclaw" / "local" / "ai-daily" / "x-snapshots"
URL_RE = re.compile(r'https?://[^\s)>"]+')
PAPER_ID_RE = re.compile(r"(\d{4}\.\d{4,5}(?:v\d+)?)")

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


def strip_wrapping_quotes(value: str) -> str:
    value = (value or "").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1].strip()
    return value


def clean_markdown_text(text: str) -> str:
    text = strip_wrapping_quotes(text)
    text = re.sub(r"\[(.*?)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def markdown_inline_to_html(text: str) -> str:
    escaped = escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"(https?://[^\s<]+)",
        lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener">{m.group(1)}</a>',
        escaped,
    )
    return escaped


def markdown_to_html(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    html_lines: List[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            close_list()
            continue
        if stripped.startswith("# "):
            continue
        if stripped.startswith("## "):
            close_list()
            html_lines.append(f"<h3>{markdown_inline_to_html(stripped[3:].strip())}</h3>")
            continue
        if stripped.startswith(("- ", "* ")):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{markdown_inline_to_html(stripped[2:].strip())}</li>")
            continue
        close_list()
        html_lines.append(f"<p>{markdown_inline_to_html(stripped)}</p>")

    close_list()
    return "".join(html_lines)


def extract_paper_id(*values: str) -> str:
    for value in values:
        match = PAPER_ID_RE.search(value or "")
        if match:
            return match.group(1)
    return ""


def build_hf_paper_link(path: Path, raw_link: str, body: str) -> str:
    cleaned = strip_wrapping_quotes(raw_link)
    paper_id = extract_paper_id(path.stem, cleaned, body)
    if paper_id:
        return f"https://huggingface.co/papers/{paper_id}"

    if cleaned and "huggingface.co/papers/" in cleaned:
        return cleaned
    if cleaned:
        return cleaned
    return ""


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
            front[key.strip().lower()] = strip_wrapping_quotes(val.strip())

    if end_idx is None:
        return {}, text

    body = "\n".join(lines[end_idx + 1 :])
    return front, body


def read_markdown(path: Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8")
    front, body = parse_front_matter(text)
    lines = body.splitlines()

    title = strip_wrapping_quotes(front.get("title", "").strip())
    if not title:
        for line in lines:
            if line.strip().startswith("#"):
                title = line.lstrip("# ").strip()
                break

    authors = strip_wrapping_quotes(front.get("authors", "").strip())
    tags_raw = front.get("tags", "").strip()
    link = (front.get("link") or front.get("url") or "").strip()
    summary = (
        front.get("summary")
        or front.get("brief")
        or front.get("comment")
        or front.get("one_sentence_summary")
        or ""
    ).strip()
    summary = strip_wrapping_quotes(summary)

    sections: Dict[str, List[str]] = {}
    current_section = ""

    paragraphs: List[str] = []
    current = []
    for raw in lines:
        line = raw.strip()
        lower = line.lower()
        if line.startswith("## "):
            current_section = clean_markdown_text(line[3:].strip()).lower()
            sections.setdefault(current_section, [])
            continue
        if current_section:
            sections[current_section].append(line)

        if not line:
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue

        if lower.startswith("authors:") and not authors:
            authors = strip_wrapping_quotes(line.split(":", 1)[1].strip())
            continue
        if lower.startswith("tags:") and not tags_raw:
            tags_raw = line.split(":", 1)[1].strip()
            continue
        if lower.startswith("link:") and not link:
            link = strip_wrapping_quotes(line.split(":", 1)[1].strip())
            continue

        if line.startswith("#"):
            continue

        if not summary and (lower.startswith("summary:") or lower.startswith("brief:")):
            summary = strip_wrapping_quotes(line.split(":", 1)[1].strip())
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
    link = build_hf_paper_link(path, link, body)

    if not title:
        title = path.stem.replace("-", " ").title()
    if not authors:
        authors = "Unknown authors"
    if not summary:
        summary = "No summary provided yet."

    tags = parse_tags(tags_raw)
    if not tags:
        tags = infer_tags_from_text(" ".join([title, summary, body]))

    insights = build_paper_insights(summary=summary, body=body, sections=sections, tags=tags)

    return {
        "title": title,
        "authors": authors,
        "summary": summary,
        "insights": insights,
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
    cleaned = [strip_wrapping_quotes(tag) for tag in items if tag]
    return [tag for tag in cleaned if tag]


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
    text = clean_markdown_text(text)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def section_content(sections: Dict[str, List[str]], keys: List[str]) -> List[str]:
    values: List[str] = []
    for heading, lines in sections.items():
        if any(key in heading for key in keys):
            values.extend(lines)
    return values


def extract_bullets(lines: List[str], max_items: int = 3) -> List[str]:
    items: List[str] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith(("- ", "* ")):
            item = clean_markdown_text(line[2:])
            if item:
                if item.endswith(("：", ":")):
                    continue
                items.append(item)
        elif re.match(r"^\d+\.\s+", line):
            item = clean_markdown_text(re.sub(r"^\d+\.\s+", "", line))
            if item:
                if item.endswith(("：", ":")):
                    continue
                items.append(item)
        if len(items) >= max_items:
            break
    return items


def extract_paragraph(lines: List[str]) -> str:
    text = " ".join(clean_markdown_text(line) for line in lines if line.strip() and not line.startswith(("-", "* ")))
    return safe_excerpt(text, 170)


def build_insight(label: str, text: str) -> str:
    return f"{label}：{safe_excerpt(text, 170)}"


def build_paper_insights(summary: str, body: str, sections: Dict[str, List[str]], tags: List[str]) -> List[str]:
    one_sentence_lines = section_content(sections, ["一句话", "one sentence"])
    innovation_lines = section_content(sections, ["关键创新", "innovation"])
    method_lines = section_content(sections, ["方法概述", "method"])
    result_lines = section_content(sections, ["主要结果", "result"])
    takeaway_lines = section_content(sections, ["要点总结", "takeaway"])

    one_sentence = clean_markdown_text(" ".join(one_sentence_lines)) or clean_markdown_text(summary)
    innovation_bullets = extract_bullets(innovation_lines, max_items=2)
    result_bullets = extract_bullets(result_lines, max_items=2)
    takeaway_bullets = extract_bullets(takeaway_lines, max_items=2)
    method_text = extract_paragraph(method_lines)

    insights: List[str] = []
    if one_sentence:
        insights.append(build_insight("问题", one_sentence))

    if innovation_bullets:
        insights.append(build_insight("方法", "；".join(innovation_bullets)))
    elif method_text:
        insights.append(build_insight("方法", method_text))

    if result_bullets:
        insights.append(build_insight("结果", "；".join(result_bullets)))
    else:
        fallback = extract_paragraph(result_lines)
        if fallback:
            insights.append(build_insight("结果", fallback))

    if takeaway_bullets:
        insights.append(build_insight("意义", "；".join(takeaway_bullets)))
    else:
        focus = "、".join(tags[:3]) if tags else "前沿 Agent / RL 研究"
        insights.append(build_insight("意义", f"该工作对 {focus} 方向具有直接参考价值。"))

    supplements = innovation_bullets + takeaway_bullets + result_bullets
    for item in supplements:
        if len(insights) >= 5:
            break
        clean = clean_markdown_text(item)
        if clean and all(clean not in existing for existing in insights):
            insights.append(build_insight("补充", clean))

    if len(insights) < 3:
        fallback = safe_excerpt(clean_markdown_text(body), 160)
        if fallback:
            insights.append(build_insight("补充", fallback))

    return insights[:5]


def build_paper_card(paper: Dict[str, object], rank: int) -> str:
    tags = paper.get("tags", []) or []
    tags_html = "".join(f'<span class="tag">{escape(str(tag))}</span>' for tag in tags)
    insights = paper.get("insights", []) or []
    insights_html = "".join(f"<li>{escape(str(item))}</li>" for item in insights[:5])
    link = str(paper.get("link") or "").strip()
    if link:
        link_html = (
            '<p class="paper-link">'
            f'<a href="{escape(link)}" target="_blank" rel="noopener">Open on Hugging Face Papers</a>'
            "</p>"
        )
    else:
        link_html = '<p class="paper-link"><span class="paper-authors">Link pending</span></p>'

    return (
        '<article class="paper-card" aria-label="paper-entry">'
        '<header class="paper-header">'
        f'<div class="paper-rank">Paper {rank:02d}</div>'
        f'<h3 class="paper-title">{escape(str(paper["title"]))}</h3>'
        "</header>"
        f'<p class="paper-authors">{escape(str(paper["authors"]))}</p>'
        f'<p class="paper-brief">{escape(safe_excerpt(str(paper["summary"]), 240))}</p>'
        f'<ul class="paper-insights">{insights_html}</ul>'
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


def render_x_snapshot(issue_dir: Path, issue_date: str) -> str:
    md_path = issue_dir / "x-snapshot.md"
    json_path = issue_dir / "x-snapshot.json"

    if not md_path.exists() and not json_path.exists():
        local_root = Path(__import__("os").environ.get("AI_DAILY_LOCAL_X_DIR", str(LOCAL_X_DIR))).expanduser()
        local_issue_dir = local_root / issue_date
        md_path = local_issue_dir / "x-snapshot.md"
        json_path = local_issue_dir / "x-snapshot.json"

    if not md_path.exists() and not json_path.exists():
        return ""

    if md_path.exists():
        body = markdown_to_html(md_path.read_text(encoding="utf-8"))
        return (
            '<section class="x-snapshot">'
            '<h2 class="section-title">X Daily Snapshot</h2>'
            f'<article class="x-snapshot-card">{body}</article>'
            "</section>"
        )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    sections = payload.get("sections", {}) if isinstance(payload, dict) else {}
    block = ['<section class="x-snapshot"><h2 class="section-title">X Daily Snapshot</h2><article class="x-snapshot-card">']
    for title in ["热门博主动态", "热门话题", "今日关键观点", "可跟进线索"]:
        items = sections.get(title, [])
        block.append(f"<h3>{escape(title)}</h3>")
        block.append("<ul>")
        if isinstance(items, list) and items:
            for item in items[:8]:
                if isinstance(item, str):
                    block.append(f"<li>{escape(item)}</li>")
                elif isinstance(item, dict):
                    text = item.get("text") or item.get("lead_text") or json.dumps(item, ensure_ascii=False)
                    handle = item.get("handle") or item.get("lead_handle") or ""
                    prefix = f"@{handle}: " if handle else ""
                    block.append(f"<li>{escape(prefix + str(text))}</li>")
                else:
                    block.append(f"<li>{escape(str(item))}</li>")
        else:
            block.append("<li>暂无数据</li>")
        block.append("</ul>")
    block.append("</article></section>")
    return "".join(block)


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
        "TAGLINE": "Frontier AI Papers, Curated as an Editorial Daily Brief",
        "TOP_PAPERS": cards,
        "X_DAILY_SNAPSHOT": render_x_snapshot(ISSUES_DIR / issue_date, issue_date),
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
