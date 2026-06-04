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
- Local automation in the Codex workspace generates the static pages and sends Feishu messages.

## GitHub Pages

Use a public repository if the page must be accessible from a company computer without GitHub login.

Current repository: `Via333/ChatGPTCodextest`

First-time setup:

1. Open `https://github.com/Via333/ChatGPTCodextest/settings/pages` with a GitHub account that has repository Settings access.
2. Under Build and deployment, set Source to GitHub Actions.
3. Re-run the latest `Deploy GitHub Pages` workflow if GitHub does not run it automatically.
4. The public URL is `https://Via333.github.io/ChatGPTCodextest/`.
