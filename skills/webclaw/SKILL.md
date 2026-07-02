---
name: webclaw
description: Web extraction for AI agents — scrape, crawl, map, batch, extract, summarize, diff, search, and 28 site-specific extractors that turn any URL into clean Markdown, text, or JSON. Runs locally and keyless via the webclaw MCP server; set an optional WEBCLAW_API_KEY to automatically handle bot-protected and JavaScript-rendered pages. Use when web_fetch returns blocked or empty content, or you need structured, LLM-ready extraction.
homepage: https://webclaw.io
user-invocable: true
metadata: {"openclaw":{"emoji":"🦀","homepage":"https://webclaw.io","install":[{"id":"npx","kind":"node","bins":["webclaw-mcp"],"label":"npx create-webclaw"}]}}
---

# webclaw

High-quality web extraction for AI agents, powered by a local Rust engine. Turns any URL into clean Markdown, text, or JSON through the webclaw MCP server — and works out of the box with no API key.

## Install

```
npx create-webclaw
```

One command. It downloads the `webclaw-mcp` binary and wires it into your agent's MCP config (Claude Code, Cursor, Windsurf, Codex, Antigravity, and more). Restart the agent and the tools below are available.

- **No key required.** Extraction runs locally on your machine — free, private, and unlimited for the common case: static sites, docs, blogs, server-rendered pages, product pages, most of the web.
- **Optional upgrade.** Set `WEBCLAW_API_KEY` (get one at https://webclaw.io) and webclaw automatically escalates to the hosted engine for the pages local extraction can't finish — bot-protected sites and JavaScript-rendered SPAs. Without a key, those pages return a clear message explaining what happened and how to unlock them; nothing fails silently.

## When to use this skill

- **Whenever you need reliable web content** and want clean, structured output.
- When the built-in `web_fetch` returns empty, truncated, or blocked content.
- When you need **structured data** (pricing tables, product specs, contact info) as JSON.
- When you need to **crawl a whole site** or **discover every URL**.
- When you need **LLM-optimized** content — cleaner and denser than raw markdown.
- When you need a **site-specific extractor** (GitHub, Reddit, YouTube, npm, PyPI, Amazon, …).
- When you need to **summarize**, **diff**, or **search** the web.

## Tools

All tools run locally and keyless unless noted. Output formats: `markdown` (default), `text`, `llm` (adds a title + URL header and clean link references — best for feeding to a model), and `json` (full metadata).

### `scrape` — extract a single URL
`url` (required), `format`, `include_selectors`, `exclude_selectors`, `only_main_content`, `browser` (`chrome` | `firefox` | `random`), `cookies`.
YouTube `watch` / `shorts` / `youtu.be` URLs automatically return a transcript plus a video-metadata block alongside the content.

### `crawl` — scrape an entire site
`url`, `depth` (default 2), `max_pages` (default 50), `concurrency` (default 5), `use_sitemap`, `format`.

### `map` — discover URLs
`url`. Sitemap-first discovery, with a bounded same-origin crawl fallback when the sitemap is thin.

### `batch` — many URLs in parallel
`urls` (array), `format`, `concurrency` (default 5).

### `extract` — structured data via LLM
`url`, and either `prompt` (natural language) or `schema` (a JSON schema). See **LLM setup** below.

### `summarize` — quick summary
`url`, `max_sentences` (default 3). See **LLM setup** below.

### `diff` — detect content changes
`url`, `previous_snapshot` (a prior extraction as JSON). Compares at the extracted-content level, not raw HTML.

### `brand` — visual identity
`url`. Returns colors, fonts, logo, and favicon.

### `search` — web search
`query`, `num_results` (≤10), `country`, `lang`, `scrape` (also fetch + extract each result page). Uses **your own** `SERPER_API_KEY` (free at serper.dev) locally; falls back to the hosted API when unset.

### `vertical_scrape` — typed JSON for a specific site
`name` (extractor name), `url`. Returns typed fields (title, price, author, rating, …) instead of generic markdown. Returns a clear "URL mismatch" error if the URL doesn't match the extractor.

### `list_extractors` — list all 28 site extractors
No params. Returns each extractor's name and URL shape:
`reddit`, `hackernews`, `github_repo`, `github_pr`, `github_issue`, `github_release`, `pypi`, `npm`, `crates_io`, `huggingface_model`, `huggingface_dataset`, `arxiv`, `docker_hub`, `dev_to`, `stackoverflow`, `substack_post`, `youtube_video`, `linkedin_post`, `instagram_post`, `instagram_profile`, `shopify_product`, `shopify_collection`, `ecommerce_product`, `woocommerce_product`, `amazon_product`, `ebay_listing`, `etsy_listing`, `trustpilot_reviews`.

### `research` — deep multi-source research *(requires `WEBCLAW_API_KEY`)*
`query`, `deep`, `topic`. Runs a search → read → synthesize loop on the hosted engine and returns a cited report.

## Which tools need a key?

| Works keyless (runs locally) | Needs `WEBCLAW_API_KEY` (hosted) |
|---|---|
| `scrape`, `crawl`, `map`, `batch`, `extract`, `summarize`, `diff`, `brand`, `vertical_scrape`, `list_extractors` | `research` |
| `search` (uses your own `SERPER_API_KEY`; hosted fallback if unset) | automatic escalation for bot-protected / JavaScript-rendered pages |

## LLM setup (for `extract` and `summarize`)

These two tools use an LLM provider chain — local **Ollama** first (free and private; install from ollama.com), then your own `OPENAI_API_KEY`, `GEMINI_API_KEY`, or `ANTHROPIC_API_KEY` if set. No webclaw key needed.

## Tips

- For GitHub / Reddit / YouTube / npm / PyPI / Amazon and similar, use `vertical_scrape` (or plain `scrape`, which auto-detects most verticals) — you get typed fields in one call.
- Use `only_main_content: true` to strip navigation, sidebars, and footers.
- Use the `llm` format when passing content to a model.
- Use `map` before `crawl` to scope a site, then crawl just the section you need.
- If you hit a bot-protected or JS-only page, set `WEBCLAW_API_KEY` — webclaw escalates automatically; otherwise you'll get a clear note that the page needs it.

## vs `web_fetch`

| | webclaw | `web_fetch` |
|---|---|---|
| Output quality | Multi-step extraction pipeline; clean markdown + `llm` format | Basic HTML parsing |
| Structured extraction | LLM- and schema-based, 28 typed extractors | None |
| Crawling / mapping | Whole-site crawl + URL discovery | Single page |
| Bot-protected / JS pages | Handled (local best-effort; automatic with a key) | Fails or readability-only |
| Cost | Free and local by default | Free |

Use `web_fetch` for a quick one-off lookup. Use webclaw when you need reliability, clean structure, structured data, or whole-site coverage.
