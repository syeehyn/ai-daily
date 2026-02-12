#!/usr/bin/env python3
"""Fetch X daily snapshot from live API or mock data and output markdown + JSON."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "x-config.json"
MOCK_PATH = ROOT / "config" / "x-mock-snapshot.json"
ISSUES_DIR = ROOT / "issues"
LOCAL_X_DIR = Path.home() / ".openclaw" / "local" / "ai-daily" / "x-snapshots"
X_API_BASE = "https://api.x.com/2"


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_dir(base_dir: Path, issue_date: str) -> Path:
    issue_dir = base_dir / issue_date
    issue_dir.mkdir(parents=True, exist_ok=True)
    return issue_dir


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_iso(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def truncate(text: str, limit: int = 180) -> str:
    compact = " ".join((text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def x_get(endpoint: str, bearer_token: str, params: Dict[str, Any]) -> Dict[str, Any]:
    query = urllib.parse.urlencode(params)
    url = f"{X_API_BASE}{endpoint}?{query}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer_token}"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def engagement_score(metrics: Dict[str, Any]) -> float:
    likes = float(metrics.get("like_count", 0) or 0)
    retweets = float(metrics.get("retweet_count", 0) or 0)
    replies = float(metrics.get("reply_count", 0) or 0)
    quotes = float(metrics.get("quote_count", 0) or 0)
    bookmarks = float(metrics.get("bookmark_count", 0) or 0)
    impressions = float(metrics.get("impression_count", 0) or 0)
    return likes + 2.0 * retweets + 1.5 * replies + 1.2 * quotes + 0.8 * bookmarks + impressions / 1000.0


def recency_score(created_at: str, now: dt.datetime) -> float:
    age_hours = max((now - parse_iso(created_at)).total_seconds() / 3600.0, 0.0)
    return math.exp(-age_hours / 24.0)


def weighted_score(post: Dict[str, Any], weights: Dict[str, Any], now: dt.datetime) -> float:
    engagement = engagement_score(post.get("public_metrics", {}))
    recency = recency_score(post.get("created_at", now.isoformat()), now)
    return float(weights.get("engagement", 0.7)) * engagement + float(weights.get("recency", 0.3)) * recency


def normalize_live_tweet(tweet: Dict[str, Any], handle: str | None, query: str | None) -> Dict[str, Any]:
    tid = str(tweet.get("id", ""))
    author = handle or "unknown"
    if not author and tweet.get("author_id"):
        author = str(tweet["author_id"])
    return {
        "id": tid,
        "handle": author,
        "query": query,
        "text": tweet.get("text", ""),
        "created_at": tweet.get("created_at", utc_now().isoformat()),
        "public_metrics": tweet.get("public_metrics", {}),
        "url": f"https://x.com/{author}/status/{tid}" if tid and author else "",
    }


def fetch_live(config: Dict[str, Any], token: str) -> Dict[str, List[Dict[str, Any]]]:
    output_cfg = config.get("output", {})
    timeline_max = int(output_cfg.get("timeline_tweets_per_user", 5))
    search_max = int(output_cfg.get("search_results_per_query", 10))

    timeline_posts: List[Dict[str, Any]] = []
    for handle in config.get("influencer_handles", []):
        user_resp = x_get(
            f"/users/by/username/{urllib.parse.quote(str(handle))}",
            token,
            {"user.fields": "id,username,name"},
        )
        user_id = ((user_resp.get("data") or {}).get("id"))
        if not user_id:
            continue

        tweets_resp = x_get(
            f"/users/{user_id}/tweets",
            token,
            {
                "max_results": min(max(timeline_max, 5), 100),
                "exclude": "retweets,replies",
                "tweet.fields": "created_at,public_metrics,lang",
            },
        )
        for tweet in tweets_resp.get("data", []) or []:
            timeline_posts.append(normalize_live_tweet(tweet, str(handle), None))

    topic_posts: List[Dict[str, Any]] = []
    for query in config.get("topic_queries", []):
        tweets_resp = x_get(
            "/tweets/search/recent",
            token,
            {
                "query": query,
                "max_results": min(max(search_max, 10), 100),
                "tweet.fields": "created_at,public_metrics,lang",
                "expansions": "author_id",
                "user.fields": "username",
            },
        )

        user_map: Dict[str, str] = {}
        includes = tweets_resp.get("includes", {}) or {}
        for user in includes.get("users", []) or []:
            uid = str(user.get("id", ""))
            uname = str(user.get("username", ""))
            if uid and uname:
                user_map[uid] = uname

        for tweet in tweets_resp.get("data", []) or []:
            author_id = str(tweet.get("author_id", ""))
            handle = user_map.get(author_id, "unknown")
            topic_posts.append(normalize_live_tweet(tweet, handle, str(query)))

    return {"timeline_posts": timeline_posts, "topic_posts": topic_posts}


def fetch_mock(mock_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    payload = read_json(mock_path)
    return {
        "timeline_posts": payload.get("timeline_posts", []),
        "topic_posts": payload.get("topic_posts", []),
    }


def dedupe(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    cleaned: List[Dict[str, Any]] = []
    for post in posts:
        key = str(post.get("id") or "") + "::" + str(post.get("handle") or "")
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(post)
    return cleaned


def summarize_topics(topic_posts: List[Dict[str, Any]], top_n: int, now: dt.datetime, weights: Dict[str, Any]) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for post in topic_posts:
        query = str(post.get("query") or "Other")
        buckets.setdefault(query, []).append(post)

    summary: List[Dict[str, Any]] = []
    for query, posts in buckets.items():
        ranked = sorted(posts, key=lambda x: weighted_score(x, weights, now), reverse=True)
        lead = ranked[0] if ranked else {}
        summary.append(
            {
                "query": query,
                "count": len(posts),
                "lead_text": truncate(str(lead.get("text", ""))),
                "lead_url": lead.get("url", ""),
                "lead_handle": lead.get("handle", ""),
                "score": round(sum(weighted_score(p, weights, now) for p in posts), 2),
            }
        )

    return sorted(summary, key=lambda x: float(x.get("score", 0)), reverse=True)[:top_n]


def build_viewpoints(posts: List[Dict[str, Any]], top_n: int) -> List[str]:
    viewpoints: List[str] = []
    for post in posts[:top_n * 2]:
        text = truncate(str(post.get("text", "")), 140)
        if not text:
            continue
        sentence = f"@{post.get('handle', 'unknown')}: {text}"
        if all(text not in existing for existing in viewpoints):
            viewpoints.append(sentence)
        if len(viewpoints) >= top_n:
            break
    return viewpoints


def build_followup_leads(posts: List[Dict[str, Any]], top_n: int) -> List[str]:
    leads: List[str] = []
    keywords = ("release", "benchmark", "open", "paper", "eval", "agent", "roadmap", "next week")
    for post in posts:
        text = str(post.get("text", ""))
        lower = text.lower()
        if not any(k in lower for k in keywords):
            continue
        url = str(post.get("url", "")).strip()
        lead = f"跟进 @{post.get('handle', 'unknown')}：{truncate(text, 120)}"
        if url:
            lead += f" ({url})"
        leads.append(lead)
        if len(leads) >= top_n:
            break
    if not leads:
        leads = ["暂未识别到高优先级线索，建议查看热门话题中的首条帖子。"]
    return leads


def build_markdown(
    issue_date: str,
    top_influencers: List[Dict[str, Any]],
    topic_summary: List[Dict[str, Any]],
    viewpoints: List[str],
    followups: List[str],
) -> str:
    lines: List[str] = []
    lines.append(f"# X Daily Snapshot ({issue_date})")
    lines.append("")
    lines.append("## 热门博主动态")
    for post in top_influencers:
        score = post.get("score", 0)
        lines.append(
            f"- @{post.get('handle', 'unknown')} | {truncate(str(post.get('text', '')), 160)} "
            f"(score={score}, {post.get('url', '')})"
        )
    if not top_influencers:
        lines.append("- 暂无数据")

    lines.append("")
    lines.append("## 热门话题")
    for topic in topic_summary:
        lines.append(
            f"- {topic.get('query', 'N/A')} (热度={topic.get('score', 0)}): "
            f"{topic.get('lead_text', '')}"
        )
    if not topic_summary:
        lines.append("- 暂无数据")

    lines.append("")
    lines.append("## 今日关键观点")
    for item in viewpoints:
        lines.append(f"- {item}")
    if not viewpoints:
        lines.append("- 暂无观点")

    lines.append("")
    lines.append("## 可跟进线索")
    for item in followups:
        lines.append(f"- {item}")
    if not followups:
        lines.append("- 暂无线索")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch X daily snapshot")
    parser.add_argument("--mode", choices=["live", "mock"], default="mock")
    parser.add_argument("--date", help="Issue date in YYYY-MM-DD. Default: today UTC")
    parser.add_argument("--config", default=str(CONFIG_PATH), help="Path to x-config.json")
    parser.add_argument("--mock-data", default=str(MOCK_PATH), help="Path to mock JSON data")
    parser.add_argument("--local-dir", default=str(LOCAL_X_DIR), help="Local output root (default: ~/.openclaw/local/ai-daily/x-snapshots)")
    parser.add_argument("--sync-to-issues", action="store_true", help="Also write x-snapshot files into repo issues/YYYY-MM-DD for publishing")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    mock_path = Path(args.mock_data)

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    config = read_json(config_path)
    now = utc_now()

    issue_date = args.date or now.date().isoformat()
    local_root = Path(args.local_dir).expanduser()
    local_issue_dir = ensure_dir(local_root, issue_date)

    if args.mode == "live":
        token = os.getenv("X_BEARER_TOKEN", "").strip()
        if not token:
            raise RuntimeError("X_BEARER_TOKEN is required for --mode live")
        fetched = fetch_live(config, token)
        source = "live"
    else:
        if not mock_path.exists():
            raise FileNotFoundError(f"Mock data not found: {mock_path}")
        fetched = fetch_mock(mock_path)
        source = "mock"

    weights = config.get("ranking_weights", {})
    output_cfg = config.get("output", {})

    timeline_posts = dedupe(fetched.get("timeline_posts", []))
    topic_posts = dedupe(fetched.get("topic_posts", []))

    ranked_influencers = sorted(timeline_posts, key=lambda x: weighted_score(x, weights, now), reverse=True)
    for post in ranked_influencers:
        post["score"] = round(weighted_score(post, weights, now), 2)

    ranked_topics_posts = sorted(topic_posts, key=lambda x: weighted_score(x, weights, now), reverse=True)
    for post in ranked_topics_posts:
        post["score"] = round(weighted_score(post, weights, now), 2)

    top_influencers_n = int(output_cfg.get("top_influencer_posts", 8))
    top_topics_n = int(output_cfg.get("top_topics", 6))
    viewpoints_n = int(output_cfg.get("key_viewpoints", 5))
    followup_n = int(output_cfg.get("followup_leads", 5))

    top_influencers = ranked_influencers[:top_influencers_n]
    topic_summary = summarize_topics(ranked_topics_posts, top_topics_n, now, weights)
    viewpoints = build_viewpoints(ranked_influencers + ranked_topics_posts, viewpoints_n)
    followups = build_followup_leads(ranked_influencers + ranked_topics_posts, followup_n)

    markdown = build_markdown(issue_date, top_influencers, topic_summary, viewpoints, followups)

    payload = {
        "date": issue_date,
        "source": source,
        "generated_at": now.isoformat(),
        "config": {
            "influencer_handles": config.get("influencer_handles", []),
            "topic_queries": config.get("topic_queries", []),
            "ranking_weights": weights,
            "output": output_cfg,
        },
        "sections": {
            "热门博主动态": top_influencers,
            "热门话题": topic_summary,
            "今日关键观点": viewpoints,
            "可跟进线索": followups,
        },
        "raw": {
            "timeline_posts": ranked_influencers,
            "topic_posts": ranked_topics_posts,
        },
    }

    md_path = local_issue_dir / "x-snapshot.md"
    json_path = local_issue_dir / "x-snapshot.json"
    md_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")

    if args.sync_to_issues:
        repo_issue_dir = ensure_dir(ISSUES_DIR, issue_date)
        (repo_issue_dir / "x-snapshot.md").write_text(markdown, encoding="utf-8")
        (repo_issue_dir / "x-snapshot.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Synced to {repo_issue_dir / 'x-snapshot.md'}")
        print(f"Synced to {repo_issue_dir / 'x-snapshot.json'}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - CLI failure path
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
