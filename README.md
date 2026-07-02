# webclaw skill

Keyless-first web extraction for AI agents, powered by a local Rust engine.

Scrape, crawl, map, batch, extract, summarize, diff, search, and run 28
site-specific extractors — turning any URL into clean Markdown, text, or JSON.

## Install

```
npx create-webclaw
```

This installs the `webclaw-mcp` server and configures it for your agent
(Claude Code, Cursor, Windsurf, Codex, Antigravity, and more).

- **No API key needed.** Extraction runs locally for the common case —
  static sites, docs, blogs, server-rendered and product pages.
- **Optional `WEBCLAW_API_KEY`** ([webclaw.io](https://webclaw.io)) automatically
  handles the harder pages (bot-protected sites, JavaScript-rendered SPAs).

See [`skills/webclaw/SKILL.md`](skills/webclaw/SKILL.md) for the full tool reference.

## Add via the skills CLI

```
npx skills add 0xMassi/webclaw-skill
```

## Links

- Homepage: https://webclaw.io
- Docs: https://webclaw.io
