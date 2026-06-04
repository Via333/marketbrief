# Daily DTC Growth Brief

Static GitHub Pages site for a daily Chinese marketing brief focused on overseas ecommerce and DTC growth.

## What It Publishes

- Latest Europe and US ecommerce / DTC market signals
- 1-3 brand or campaign case studies
- Reusable growth plays for ads, content, influencers, CRM, CRO, pricing, retention, and community
- Audience insights and localization notes
- Domestic China growth tactics that may transfer overseas
- One practical experiment for the day
- Source links, with facts separated from observations and inference

## Files

- `index.html` shows the latest brief.
- `archive/index.html` lists past briefs.
- `briefs/YYYY-MM-DD.html` stores each published issue.
- `content/briefs/YYYY-MM-DD.md` stores source Markdown for each issue.
- `scripts/publish_brief.py` turns a Markdown brief into static pages and can send a Feishu message.

## Local Publish

```bash
python3 scripts/publish_brief.py content/briefs/YYYY-MM-DD.md --site-url https://Via333.github.io/ChatGPTCodextest/
```

To also send Feishu, set `FEISHU_WEBHOOK` in your environment or in a local `.env` file:

```bash
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxxx
SITE_URL=https://Via333.github.io/ChatGPTCodextest/
```

`.env` is ignored by git and must not be committed.

## GitHub Pages

Use a public repository if the page must be accessible from a company computer without GitHub login.

Recommended setup:

1. Create or use a public repo, currently `Via333/ChatGPTCodextest`.
2. Push these files to the repo's `main` branch.
3. The included GitHub Actions workflow deploys the root folder to Pages.
4. If GitHub asks for a Pages source the first time, choose GitHub Actions.
5. The public URL is `https://Via333.github.io/ChatGPTCodextest/`.
