#!/usr/bin/env python3
"""Fetch paper preview images with robust fallback for each issue."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import mimetypes
import re
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
ISSUES_DIR = ROOT / "issues"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PAPER_ID_RE = re.compile(r"(\d{4}\.\d{4,5}(?:v\d+)?)")


def parse_front_matter(content: str) -> Tuple[Dict[str, str], str]:
  if not content.startswith("---\n"):
    return {}, content

  lines = content.splitlines()
  out: Dict[str, str] = {}
  end = None
  for idx in range(1, len(lines)):
    line = lines[idx]
    if line.strip() == "---":
      end = idx
      break
    if ":" not in line:
      continue
    key, value = line.split(":", 1)
    out[key.strip().lower()] = value.strip().strip('"').strip("'")

  if end is None:
    return {}, content
  return out, "\n".join(lines[end + 1 :])


def issue_dirs(selected_date: Optional[str]) -> List[Path]:
  if selected_date:
    if not DATE_RE.match(selected_date):
      raise ValueError("--date must be YYYY-MM-DD")
    issue = ISSUES_DIR / selected_date
    return [issue] if issue.exists() else []

  dirs: List[Path] = []
  for path in ISSUES_DIR.iterdir():
    if path.is_dir() and DATE_RE.match(path.name):
      dirs.append(path)
  return sorted(dirs, key=lambda p: p.name, reverse=True)


def detect_paper_id(path: Path, front: Dict[str, str], body: str) -> str:
  for source in [path.stem, front.get("url", ""), front.get("link", ""), body]:
    match = PAPER_ID_RE.search(source)
    if match:
      return match.group(1)
  return path.stem


def pick_hf_url(front: Dict[str, str], paper_id: str) -> str:
  url = (front.get("url") or front.get("link") or "").strip()
  if "huggingface.co/papers/" in url:
    return url
  if paper_id:
    return f"https://huggingface.co/papers/{paper_id}"
  return url


def extract_meta_image(page_html: str, base_url: str) -> Optional[str]:
  patterns = [
    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']'
  ]
  for pattern in patterns:
    match = re.search(pattern, page_html, re.IGNORECASE)
    if match:
      return urllib.parse.urljoin(base_url, match.group(1))
  return None


def request_text(url: str) -> str:
  req = urllib.request.Request(url, headers={"User-Agent": "ai-daily/2.0 image-fetcher"})
  with urllib.request.urlopen(req, timeout=20) as resp:
    charset = resp.headers.get_content_charset() or "utf-8"
    return resp.read().decode(charset, errors="replace")


def download_image(url: str, output_base: Path) -> Optional[Path]:
  req = urllib.request.Request(url, headers={"User-Agent": "ai-daily/2.0 image-fetcher"})
  with urllib.request.urlopen(req, timeout=25) as resp:
    content_type = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    if not content_type.startswith("image/"):
      return None
    raw = resp.read(8 * 1024 * 1024)
    ext = mimetypes.guess_extension(content_type) or Path(urllib.parse.urlparse(url).path).suffix or ".img"
    out = output_base.with_suffix(ext)
    out.write_bytes(raw)
    return out


def build_placeholder(title: str, output: Path) -> None:
  safe_title = html.escape(textwrap.shorten(title, width=70, placeholder="..."))
  svg = f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1200\" height=\"630\" viewBox=\"0 0 1200 630\">
  <defs>
    <linearGradient id=\"bg\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">
      <stop offset=\"0%\" stop-color=\"#1a1a18\"/>
      <stop offset=\"100%\" stop-color=\"#2b2b28\"/>
    </linearGradient>
  </defs>
  <rect width=\"1200\" height=\"630\" fill=\"url(#bg)\"/>
  <rect x=\"50\" y=\"50\" width=\"1100\" height=\"530\" rx=\"18\" fill=\"none\" stroke=\"#8f8f89\" stroke-width=\"2\"/>
  <text x=\"90\" y=\"150\" font-family=\"-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif\" font-size=\"30\" fill=\"#e8e8e2\">AI Daily Fallback Figure</text>
  <text x=\"90\" y=\"220\" font-family=\"-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif\" font-size=\"24\" fill=\"#d1d1cb\">{safe_title}</text>
  <text x=\"90\" y=\"560\" font-family=\"-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif\" font-size=\"18\" fill=\"#b0b0aa\">Generated placeholder when HF og:image metadata is unavailable.</text>
</svg>
"""
  output.write_text(svg, encoding="utf-8")


def process_issue(issue_dir: Path) -> Dict[str, Dict[str, str]]:
  papers_dir = issue_dir / "papers"
  figures_dir = issue_dir / "assets" / "figures"
  figures_dir.mkdir(parents=True, exist_ok=True)

  manifest: Dict[str, Dict[str, str]] = {}
  for paper_md in sorted(papers_dir.glob("*.md")):
    content = paper_md.read_text(encoding="utf-8")
    front, body = parse_front_matter(content)
    title = front.get("title") or paper_md.stem
    paper_id = detect_paper_id(paper_md, front, body)
    hf_url = pick_hf_url(front, paper_id)

    result_path: Optional[Path] = None
    source = "placeholder"
    image_url = ""

    try:
      if hf_url:
        page_html = request_text(hf_url)
        image_url = extract_meta_image(page_html, hf_url) or ""
        if image_url:
          result_path = download_image(image_url, figures_dir / paper_id)
          if result_path:
            source = "hf_og_image"
    except (urllib.error.URLError, TimeoutError, ValueError):
      result_path = None

    if result_path is None:
      placeholder = figures_dir / f"{paper_id}.svg"
      build_placeholder(title, placeholder)
      result_path = placeholder
      source = "generated_placeholder"

    manifest[paper_id] = {
      "paper_id": paper_id,
      "paper_file": paper_md.name,
      "source": source,
      "hf_page_url": hf_url,
      "image_url": image_url,
      "stored_path": str(result_path.relative_to(issue_dir)).replace("\\", "/")
    }

  (figures_dir / "manifest.json").write_text(
    json.dumps(
      {
        "issue_date": issue_dir.name,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "strategy": [
          "Try Hugging Face paper page og:image / metadata",
          "Fallback to generated placeholder thumb"
        ],
        "papers": manifest
      },
      ensure_ascii=False,
      indent=2,
    )
    + "\n",
    encoding="utf-8",
  )

  return manifest


def main() -> None:
  parser = argparse.ArgumentParser(description="Fetch HF paper preview images with fallback")
  parser.add_argument("--date", help="Issue date YYYY-MM-DD. If omitted, process all issues.")
  args = parser.parse_args()

  processed = 0
  for issue_dir in issue_dirs(args.date):
    manifest = process_issue(issue_dir)
    processed += 1
    print(f"[{issue_dir.name}] image assets ready for {len(manifest)} paper(s)")

  print(f"Done. Processed {processed} issue(s).")


if __name__ == "__main__":
  main()
