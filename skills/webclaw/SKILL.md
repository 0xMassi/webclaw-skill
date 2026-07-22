---
name: webclaw
description: Web extraction for AI agents. Scrape, crawl, map, batch, extract, summarize, diff, brand, search, and 28 site-specific extractors turn any URL into clean Markdown, text, or JSON. Runs locally with no key via the webclaw MCP server; set an optional WEBCLAW_API_KEY to handle bot-protected and JavaScript-rendered pages. Use when web_fetch returns blocked or empty content, or you need structured, LLM-ready extraction.
homepage: https://webclaw.io
user-invocable: true
metadata: {"openclaw":{"emoji":"🦀","homepage":"https://webclaw.io","install":[{"id":"npx","kind":"node","bins":["webclaw-mcp"],"label":"npx create-webclaw"}]}}
---

# webclaw

Web extraction for AI agents, powered by a local Rust engine. It turns any URL into clean Markdown, text, or JSON through the webclaw MCP server, and it works with no API key.

## Install

```
npx create-webclaw
```

This writes the `npx @webclaw/mcp` MCP config into your agent (Claude Code, Cursor, Windsurf, Codex, Antigravity, and more) — nothing to install; the server is fetched and cached on first launch. Restart the agent to load the tools below.

- **No key needed.** Extraction runs on your machine: free, private, and unlimited for the common case. Static sites, docs, blogs, server-rendered pages, and product pages all work locally.
- **Optional upgrade.** Set `WEBCLAW_API_KEY` (from https://webclaw.io) and webclaw escalates to the hosted engine for the pages local extraction can't finish: bot-protected sites and JavaScript-rendered SPAs. Without a key, those pages return a clear message that tells you how to unlock them.

## When to use this skill

- You need reliable web content with clean, structured output.
- `web_fetch` returns empty, truncated, or blocked content.
- You need structured data (pricing tables, product specs, contact info) as JSON.
- You need to crawl a whole site or discover every URL.
- You need LLM-optimized content, cleaner than raw markdown.
- You need a site-specific extractor (GitHub, Reddit, YouTube, npm, PyPI, Amazon).
- You need to summarize, diff, or search the web.
- You need to enrich a company URL — or a list of them — into outreach-ready leads: founders/leadership with their LinkedIn and X, plus summary, socials, pricing, tech, and on-site emails.

## Tools

All tools run locally with no key unless noted. Output formats: `markdown` (default), `text`, `llm` (adds a title and URL header with clean link references, best for feeding to a model), and `json` (full metadata).

### `scrape`: extract a single URL
`url` (required), `format`, `include_selectors`, `exclude_selectors`, `only_main_content`, `browser` (`chrome` | `firefox` | `random`), `cookies`.
YouTube `watch`, `shorts`, and `youtu.be` URLs also return a transcript and a video-metadata block alongside the content.

### `crawl`: scrape an entire site
`url`, `depth` (default 2), `max_pages` (default 50), `concurrency` (default 5), `use_sitemap`, `format`.

### `map`: discover URLs
`url`. Sitemap-first discovery, with a bounded same-origin crawl fallback when the sitemap is thin.

### `batch`: many URLs in parallel
`urls` (array), `format`, `concurrency` (default 5).

### `extract`: structured data via LLM
`url`, plus either `prompt` (natural language) or `schema` (a JSON schema). See **LLM setup** below.

### `summarize`: quick summary
`url`, `max_sentences` (default 3). See **LLM setup** below.

### `diff`: detect content changes
`url`, `previous_snapshot` (a prior extraction as JSON). Compares at the extracted-content level rather than raw HTML.

### `brand`: visual identity
`url`. Returns colors, fonts, logo, and favicon.

### `search`: web search
`query`, `num_results` (≤10), `country`, `lang`, `scrape` (also fetch and extract each result page). Uses **your own** `SERPER_API_KEY` (free at serper.dev) locally, and falls back to the hosted API when unset.

### `vertical_scrape`: typed JSON for a specific site
`name` (extractor name), `url`. Returns typed fields (title, price, author, rating) instead of generic markdown, or a clear "URL mismatch" error when the URL doesn't fit the extractor. Verticals for protected sites (Amazon, eBay, Etsy, Trustpilot) need `WEBCLAW_API_KEY`; without one they return a message asking you to set it.

### `list_extractors`: list all 28 site extractors
No params. Returns each extractor's name and URL shape:
`reddit`, `hackernews`, `github_repo`, `github_pr`, `github_issue`, `github_release`, `pypi`, `npm`, `crates_io`, `huggingface_model`, `huggingface_dataset`, `arxiv`, `docker_hub`, `dev_to`, `stackoverflow`, `substack_post`, `youtube_video`, `linkedin_post`, `instagram_post`, `instagram_profile`, `shopify_product`, `shopify_collection`, `ecommerce_product`, `woocommerce_product`, `amazon_product`, `ebay_listing`, `etsy_listing`, `trustpilot_reviews`.

### `research`: deep multi-source research *(requires `WEBCLAW_API_KEY`)*
`query`, `deep`, `topic`. Runs a search, read, and synthesize loop on the hosted engine and returns a cited report.

### `lead`: turn one company URL into an outreach-ready lead *(requires `WEBCLAW_API_KEY`)*
`url` (required), `no_cache` (default `false`). Enriches a single company. The response is `url`, `domain`, `people_source` (`web_search`), `cache` (`hit` | `miss`), and `credits` (100) at the top level, plus a nested **`lead`** object that holds everything about the company: `company_name`, `summary`, `socials` (`linkedin`, `x`, `github`), `tech`, `pricing` tiers (`plan`, `price`), on-site `emails` (`type`, `email`), and `people` — the founders/leadership as `name`, `role`, `linkedin`, `x`. The people come from open-web search + verification (anchored to the company's own domain, name-validated), not a licensed contact database. Does **not** return funding, HQ, phone, or guessed emails. Very new sites and solo founders may return fewer people, or none. Flat 100 credits per successful lead; a site that can't be reached and has no public people isn't charged.

### `lead_batch`: enrich many company URLs in one call *(requires `WEBCLAW_API_KEY`)*
`urls` (array, 1–25 companies), `no_cache` (default `false`). Runs `lead` across the whole list. The job is async on the server, but this tool **polls internally and blocks until it finishes**, then returns the final job: `id`, `status` (`completed`), `total`, `completed`, `succeeded`, `credits_charged`, and `results` — one entry per URL, either `{ url, status: "success", domain, lead, cache }` (same nested `lead` object as above) or `{ url, status: "error", error }`. Billed 100 credits per **successful** lead; URLs that can't be enriched (unreachable, nothing found) aren't charged. Up to 25 URLs per call. To discover the companies to feed it, pair with the **lead-enrichment** skill's `find.py`.

## Which tools need a key?

| Works with no key (runs locally) | Needs `WEBCLAW_API_KEY` (hosted) |
|---|---|
| `scrape`, `crawl`, `map`, `batch`, `extract`, `summarize`, `diff`, `brand`, `vertical_scrape`, `list_extractors` | `research`, `lead`, `lead_batch` |
| `search` (uses your own `SERPER_API_KEY`; hosted fallback if unset) | escalation for bot-protected and JavaScript-rendered pages |

## LLM setup (for `extract` and `summarize`)

These two tools use an LLM provider chain: local **Ollama** first (free and private; install from ollama.com), then your own `OPENAI_API_KEY`, `GEMINI_API_KEY`, or `ANTHROPIC_API_KEY` if set. No webclaw key needed.

## Tips

- For GitHub, Reddit, YouTube, npm, PyPI, or Amazon, use `vertical_scrape` (or plain `scrape`, which auto-detects most verticals) to get typed fields in one call.
- Set `only_main_content: true` to strip navigation, sidebars, and footers.
- Use the `llm` format when passing content to a model.
- Run `map` before `crawl` to scope a site, then crawl the section you need.
- If a page is bot-protected or JS-only, set `WEBCLAW_API_KEY` to escalate; without one you get a clear note that the page needs it.

## vs `web_fetch`

| | webclaw | `web_fetch` |
|---|---|---|
| Output quality | Multi-step extraction pipeline; clean markdown and `llm` format | Basic HTML parsing |
| Structured extraction | LLM- and schema-based, 28 typed extractors | None |
| Crawling and mapping | Whole-site crawl and URL discovery | Single page |
| Bot-protected and JS pages | Handled (local best-effort; automatic with a key) | Fails or readability-only |
| Cost | Free and local by default | Free |

Use `web_fetch` for a quick one-off lookup. Reach for webclaw when you need reliability, clean structure, structured data, or whole-site coverage.
