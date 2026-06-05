# Daily DTC Growth Brief

Static GitHub Pages site for a daily Chinese marketing brief focused on overseas ecommerce and DTC growth.

## What It Publishes

- Latest Europe and US ecommerce / DTC market signals
- 1-3 brand or campaign case studies
- Reusable growth plays for ads, content, influencers, CRM, CRO, pricing, retention, and community
- Audience insights and localization notes
- Domestic China growth tactics that may transfer overseas
- One practical experiment for the day
- Source links placed inline after each market signal and case, with facts separated from observations and inference

## Files

- `index.html` shows the latest brief.
- `archive/index.html` lists past briefs.
- `briefs/YYYY-MM-DD.html` stores each published issue.
- `content/briefs/YYYY-MM-DD.md` stores source Markdown for each issue.
- `scripts/publish_brief.py` turns a Markdown brief into static pages and can send a Feishu message.

## Local Publish

```bash
python3 scripts/publish_brief.py content/briefs/YYYY-MM-DD.md --site-url https://Via333.github.io/marketbrief/
```

To also send Feishu, set these in your local `.env` file:

```bash
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxxx
FEISHU_SECRET=optional-signing-secret
SITE_URL=https://Via333.github.io/marketbrief/
```

`.env` is ignored by git and must not be committed.

## GitHub Pages

Use a public repository if the page must be accessible from a company computer without GitHub login.

Current repository: `Via333/marketbrief`

First-time setup:

1. Open `https://github.com/Via333/marketbrief/settings/pages` with a GitHub account that has repository Settings access.
2. Under Build and deployment, set Source to GitHub Actions.
3. Re-run the latest `Deploy GitHub Pages` workflow if GitHub does not run it automatically.
4. The public URL is `https://Via333.github.io/marketbrief/`.
