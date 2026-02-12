#!/usr/bin/env python3
"""Build issue-data.json adapter from existing markdown/json outputs."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ISSUES_DIR = ROOT / "issues"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_front_matter(raw: str) -> Tuple[Dict[str, str], str]:
  if not raw.startswith("---\n"):
    return {}, raw
  lines = raw.splitlines()
  meta: Dict[str, str] = {}
  end = None
  for idx in range(1, len(lines)):
    line = lines[idx]
    if line.strip() == "---":
      end = idx
      break
    if ":" not in line:
      continue
    k, v = line.split(":", 1)
    meta[k.strip().lower()] = v.strip().strip('"').strip("'")
  if end is None:
    return {}, raw
  return meta, "\n".join(lines[end + 1 :])


def parse_tags(raw: str) -> List[str]:
  text = (raw or "").strip().strip("[]")
  if not text:
    return []
  return [item.strip().strip('"').strip("'") for item in text.split(",") if item.strip()]


def parse_summary(body: str) -> str:
  for line in body.splitlines():
    s = line.strip()
    if not s or s.startswith("#") or s.startswith("-"):
      continue
    return s
  return "No summary available."


def load_figures_manifest(issue_dir: Path) -> Dict[str, str]:
  manifest_path = issue_dir / "assets" / "figures" / "manifest.json"
  if not manifest_path.exists():
    return {}
  payload = json.loads(manifest_path.read_text(encoding="utf-8"))
  papers = payload.get("papers", {})
  out: Dict[str, str] = {}
  if isinstance(papers, dict):
    for paper_id, item in papers.items():
      if isinstance(item, dict) and item.get("stored_path"):
        out[str(paper_id)] = f"/api/assets/{issue_dir.name}/figures/{Path(str(item['stored_path'])).name}"
  return out


def build_issue_data(issue_dir: Path) -> Dict[str, object]:
  digest_path = issue_dir / "digest.md"
  digest_raw = digest_path.read_text(encoding="utf-8") if digest_path.exists() else ""

  digest_meta, _ = parse_front_matter(digest_raw)
  issue_title = digest_meta.get("title") or f"AI Daily {issue_dir.name}"

  figure_map = load_figures_manifest(issue_dir)

  papers: List[Dict[str, object]] = []
  for md in sorted((issue_dir / "papers").glob("*.md")):
    raw = md.read_text(encoding="utf-8")
    front, body = parse_front_matter(raw)
    pid = md.stem
    papers.append(
      {
        "id": pid,
        "title": front.get("title") or pid,
        "authors": front.get("authors") or "Unknown authors",
        "summary": parse_summary(body),
        "tags": parse_tags(front.get("tags", "")),
        "url": front.get("url") or front.get("link") or "",
        "markdown": body.strip(),
        "image": figure_map.get(pid),
      }
    )

  snapshot_json = issue_dir / "x-snapshot.json"
  x_snapshot = None
  if snapshot_json.exists():
    x_snapshot = json.loads(snapshot_json.read_text(encoding="utf-8"))

  return {
    "date": issue_dir.name,
    "title": issue_title,
    "digest": digest_raw,
    "papers": papers,
    "x_snapshot": x_snapshot,
    "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "schema_version": "2.0",
  }


def iter_issue_dirs(selected_date: str | None) -> List[Path]:
  if selected_date:
    issue_dir = ISSUES_DIR / selected_date
    return [issue_dir] if issue_dir.exists() else []
  return sorted([d for d in ISSUES_DIR.iterdir() if d.is_dir() and DATE_RE.match(d.name)], key=lambda p: p.name, reverse=True)


def main() -> None:
  parser = argparse.ArgumentParser(description="Build issue-data.json files")
  parser.add_argument("--date", help="Issue date YYYY-MM-DD")
  args = parser.parse_args()

  count = 0
  for issue_dir in iter_issue_dirs(args.date):
    payload = build_issue_data(issue_dir)
    out = issue_dir / "issue-data.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    count += 1
    print(f"Wrote {out}")

  print(f"Done. Built {count} adapter file(s).")


if __name__ == "__main__":
  main()
