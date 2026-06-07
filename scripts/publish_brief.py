#!/usr/bin/env python3
"""Publish one Markdown DTC brief into a static GitHub Pages site."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEED_PATH = ROOT / "feed.json"
BRIEF_DIR = ROOT / "briefs"
ARCHIVE_PATH = ROOT / "archive" / "index.html"
INDEX_PATH = ROOT / "index.html"


@dataclass
class Brief:
    source: Path
    slug: str
    title: str
    summary: str
    published_at: str
    body_markdown: str
    body_html: str


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def slug_from_path(path: Path) -> str:
    match = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
    if match:
        return match.group(1)
    return date.today().isoformat()


def extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return f"DTC 增长营销每日简报 - {fallback}"


def extract_summary(markdown: str) -> str:
    plain_lines: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        stripped = re.sub(r"^[-*]\s+", "", stripped)
        stripped = re.sub(r"[*_`>]", "", stripped).strip()
        if stripped:
            plain_lines.append(stripped)
        if len(" ".join(plain_lines)) > 130:
            break
    summary = " ".join(plain_lines)
    return summary[:170] + ("..." if len(summary) > 170 else "")


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        escaped,
    )
    return escaped


def markdown_to_html(markdown: str) -> str:
    blocks: list[str] = []
    list_items: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            blocks.append("<ul>" + "".join(list_items) + "</ul>")
            list_items = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_list()
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            flush_list()
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h2>{inline_markdown(stripped[3:].strip())}</h2>")
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h3>{inline_markdown(stripped[4:].strip())}</h3>")
            continue
        if stripped.startswith("> "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<blockquote>{inline_markdown(stripped[2:].strip())}</blockquote>")
            continue
        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        if bullet:
            flush_paragraph()
            list_items.append(f"<li>{inline_markdown(bullet.group(1))}</li>")
            continue
        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def read_brief(path: Path, site_url: str | None = None) -> Brief:
    markdown = path.read_text(encoding="utf-8").strip()
    slug = slug_from_path(path)
    title = extract_title(markdown, slug)
    summary = extract_summary(markdown)
    return Brief(
        source=path,
        slug=slug,
        title=title,
        summary=summary,
        published_at=slug,
        body_markdown=markdown,
        body_html=markdown_to_html(markdown),
    )


def page_shell(title: str, description: str, body: str, asset_prefix: str = "") -> str:
    stylesheet = f"{asset_prefix}assets/style.css"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="stylesheet" href="{stylesheet}">
</head>
<body>
  <header class="site-header">
    <div class="shell nav">
      <a class="brand" href="{asset_prefix}"><span class="mark">DTC</span><span>增长营销每日简报</span></a>
      <nav class="nav-links" aria-label="主要导航">
        <a href="{asset_prefix}archive/">往期归档</a>
        <a href="{asset_prefix}feed.json">数据源</a>
      </nav>
    </div>
  </header>
  {body}
  <footer class="site-footer">
    <div class="shell">Generated for internal growth learning and discussion.</div>
  </footer>
</body>
</html>
"""


def render_brief_page(brief: Brief) -> str:
    body = f"""<main>
    <section class="shell hero">
      <p class="eyebrow">Published {html.escape(brief.published_at)}</p>
      <h1>{html.escape(brief.title)}</h1>
      <p class="lede">{html.escape(brief.summary)}</p>
      <div class="meta-row">
        <span class="chip">欧美市场优先</span>
        <span class="chip">案例拆解</span>
        <span class="chip">飞书同步</span>
      </div>
    </section>
    <section class="shell layout">
      <article class="brief">
{brief.body_html}
      </article>
      <aside class="side" aria-label="简报信息">
        <section class="side-panel">
          <h2>发布日期</h2>
          <p>{html.escape(brief.published_at)}</p>
        </section>
        <section class="side-panel">
          <h2>阅读重点</h2>
          <p>市场信号、案例玩法、受众洞察、可执行实验。</p>
        </section>
      </aside>
    </section>
  </main>"""
    return page_shell(brief.title, brief.summary, body, "../")


def render_index(brief: Brief) -> str:
    body = f"""<main>
    <section class="shell hero">
      <p class="eyebrow">最新简报 · {html.escape(brief.published_at)}</p>
      <h1>{html.escape(brief.title)}</h1>
      <p class="lede">{html.escape(brief.summary)}</p>
      <div class="meta-row">
        <span class="chip">欧美市场优先</span>
        <span class="chip">案例拆解</span>
        <span class="chip">飞书同步</span>
      </div>
    </section>
    <section class="shell layout">
      <article class="brief">
{brief.body_html}
      </article>
      <aside class="side" aria-label="简报说明">
        <section class="side-panel">
          <h2>往期归档</h2>
          <p><a href="archive/">查看全部历史简报</a></p>
        </section>
        <section class="side-panel">
          <h2>固定结构</h2>
          <p>趋势、案例、玩法、受众、框架、今日实验、来源链接。</p>
        </section>
      </aside>
    </section>
  </main>"""
    return page_shell("DTC 增长营销每日简报", brief.summary, body)


def load_feed() -> list[dict[str, str]]:
    if not FEED_PATH.exists():
        return []
    try:
        data = json.loads(FEED_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_feed(feed: list[dict[str, str]]) -> None:
    FEED_PATH.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_archive(feed: list[dict[str, str]]) -> str:
    if feed:
        items = "\n".join(
            f"""      <li class="archive-item"><a href="../{html.escape(item['url'])}">{html.escape(item['title'])}</a><time>{html.escape(item['date'])}</time><p>{html.escape(item.get('summary', ''))}</p></li>"""
            for item in feed
        )
    else:
        items = '      <li class="empty-state">暂无已发布简报。</li>'
    body = f"""<main class="shell">
    <section class="hero">
      <p class="eyebrow">Archive</p>
      <h1>往期归档</h1>
      <p class="lede">按发布日期倒序排列。</p>
    </section>
    <ul class="archive-list">
{items}
    </ul>
  </main>"""
    return page_shell("往期归档 - DTC 增长营销每日简报", "DTC 增长营销每日简报往期归档。", body, "../")


def publish(brief: Brief) -> str:
    BRIEF_DIR.mkdir(exist_ok=True)
    (ROOT / "archive").mkdir(exist_ok=True)
    output_path = BRIEF_DIR / f"{brief.slug}.html"
    output_path.write_text(render_brief_page(brief), encoding="utf-8")
    INDEX_PATH.write_text(render_index(brief), encoding="utf-8")

    feed = [item for item in load_feed() if item.get("date") != brief.published_at]
    feed.insert(
        0,
        {
            "date": brief.published_at,
            "title": brief.title,
            "summary": brief.summary,
            "url": f"briefs/{brief.slug}.html",
        },
    )
    feed.sort(key=lambda item: item["date"], reverse=True)
    save_feed(feed)
    ARCHIVE_PATH.write_text(render_archive(feed), encoding="utf-8")
    return f"briefs/{brief.slug}.html"


def feishu_signature(secret: str, timestamp: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
    digest = hmac.new(string_to_sign, b"", digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def send_feishu(webhook: str, title: str, summary: str, url: str, secret: str = "") -> None:
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "template": "green",
                "title": {"tag": "plain_text", "content": title},
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": summary}},
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "查看完整简报"},
                            "url": url,
                            "type": "primary",
                        }
                    ],
                },
            ],
        },
    }
    if secret:
        timestamp = str(int(time.time()))
        payload["timestamp"] = timestamp
        payload["sign"] = feishu_signature(secret, timestamp)
    request = urllib.request.Request(
        webhook,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            response.read()
    except Exception as exc:
        print(f"Feishu webhook error: {exc}", file=sys.stderr)


def git_commit_and_push(message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=ROOT, check=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if diff.returncode == 0:
        return
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    subprocess.run(["git", "push"], cwd=ROOT, check=True)


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path, help="Path to Markdown brief")
    parser.add_argument("--site-url", default=os.environ.get("SITE_URL", "").strip(), help="Public GitHub Pages base URL")
    parser.add_argument("--send-feishu", action="store_true", help="Send Feishu card after publishing")
    parser.add_argument("--push", action="store_true", help="Commit and push changes with git")
    args = parser.parse_args()

    brief_path = args.brief if args.brief.is_absolute() else ROOT / args.brief
    if not brief_path.exists():
        print(f"Brief not found: {brief_path}", file=sys.stderr)
        return 1

    brief = read_brief(brief_path, args.site_url)
    relative_url = publish(brief)
    public_url = (args.site_url.rstrip("/") + "/" + relative_url) if args.site_url else relative_url

    if args.push:
        git_commit_and_push(f"Publish DTC brief {brief.published_at}")

    if args.send_feishu:
        webhook = os.environ.get("FEISHU_WEBHOOK", "").strip()
        if not webhook:
            print("FEISHU_WEBHOOK is missing; skip Feishu send.", file=sys.stderr)
            return 2
        secret = os.environ.get("FEISHU_SECRET", "").strip()
        send_feishu(webhook, brief.title, brief.summary, public_url, secret)

    print(public_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
