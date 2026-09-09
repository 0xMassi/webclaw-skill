# webclaw skill

<p align="center">
  <a href="https://github.com/0xMassi/webclaw-skill/stargazers"><img src="https://shieldcn.dev/github/stars/0xMassi/webclaw-skill.svg?variant=branded&logo=github" alt="Stars" /></a>
  <a href="https://www.npmjs.com/package/create-webclaw"><img src="https://shieldcn.dev/npm/dt/create-webclaw.svg?variant=branded" alt="installs" /></a>
  <a href="https://webclaw.io"><img src="https://shieldcn.dev/badge/Hosted-webclaw.io.svg?variant=branded&logo=safari" alt="Hosted webclaw" /></a>
</p>

Web extraction for AI agents, powered by a local Rust engine. Scrape, crawl,
map, batch, extract, summarize, diff, search, and run 28 site-specific
extractors that turn any URL into clean Markdown, text, or JSON.

## Install

```
npx create-webclaw
```

This installs the `webclaw-mcp` server and configures it for your agent
(Claude Code, Cursor, Windsurf, Codex, Antigravity, and more).

- **No API key needed.** Extraction runs locally for the common case: static
  sites, docs, blogs, server-rendered pages, and product pages.
- **Optional `WEBCLAW_API_KEY`** ([webclaw.io](https://webclaw.io)) handles the
  harder pages, like bot-protected sites and JavaScript-rendered SPAs.

See [`skills/webclaw/SKILL.md`](skills/webclaw/SKILL.md) for the full tool reference.

## Add via the skills CLI

```
npx skills add 0xMassi/webclaw-skill
```

## Cursor plugin

This repository also packages webclaw as a Cursor plugin. The plugin starts
`@webclaw/mcp@0.6.22`, loads the webclaw skill, and accepts an optional
`WEBCLAW_API_KEY` through Cursor's plugin settings.

Test a local checkout before marketplace submission:

```bash
ln -s /path/to/webclaw-skill ~/.cursor/plugins/local/webclaw
```

Reload Cursor, open **Customize**, and configure the plugin. Local extraction
works without a key. Add a key for hosted search, research, and protected pages.

## Skills in this repo

| Skill | What it does |
|---|---|
| [`webclaw`](skills/webclaw/SKILL.md) | The full toolset: scrape, crawl, map, batch, extract, summarize, diff, brand, search, research, and 28 site-specific extractors. |
| [`lead-enrichment`](skills/lead-enrichment/SKILL.md) | Discover companies (from a listing URL or an ICP) and enrich generic firmographics — pitch, contact email, socials, pricing model, tech signals, or any custom field — via `/v1/extract`. |

## Links

- Homepage: https://webclaw.io
