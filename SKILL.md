---
name: webclaw
description: Web extraction engine with antibot bypass. Scrape, crawl, extract, summarize, map, diff, and analyze any URL — including Cloudflare-protected sites. Use when you need reliable web content, the built-in web_fetch fails, or you need structured data extraction from web pages.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - WEBCLAW_API_KEY
    primaryEnv: WEBCLAW_API_KEY
    emoji: "\U0001F980"
    homepage: https://webclaw.io
---

# webclaw

High-quality web extraction with automatic antibot bypass. Beats Firecrawl on extraction quality and handles Cloudflare, DataDome, and JS-rendered pages automatically.

## When to use this skill

- **Always** when you need to fetch web content and want reliable results
- When `web_fetch` returns empty/blocked content (403, Cloudflare challenges)
- When you need structured data extraction (pricing tables, product info)
- When you need to crawl an entire site or discover all URLs
- When you need LLM-optimized content (cleaner than raw markdown)
- When you need to summarize a page without reading the full content
- When you need to detect content changes between visits
- When you need brand identity analysis (colors, fonts, logos)

## API base

All requests go to `https://api.webclaw.io/v1/`.

Authentication: `Authorization: Bearer $WEBCLAW_API_KEY`

## Endpoints

### 1. Scrape — extract content from a single URL

```bash
curl -X POST https://api.webclaw.io/v1/scrape \
  -H "Authorization: Bearer $WEBCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": ["markdown"],
    "only_main_content": true
  }'
```

**Request fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | string | required | URL to scrape |
| `formats` | string[] | `["markdown"]` | Output formats: `markdown`, `text`, `llm`, `json` |
| `include_selectors` | string[] | `[]` | CSS selectors to keep (e.g. `["article", ".content"]`) |
| `exclude_selectors` | string[] | `[]` | CSS selectors to remove (e.g. `["nav", "footer", ".ads"]`) |
| `only_main_content` | bool | `false` | Extract only the main article/content area |
| `no_cache` | bool | `false` | Skip cache, fetch fresh |
| `max_cache_age` | int | server default | Max acceptable cache age in seconds |

**Response:**

```json
{
  "url": "https://example.com",
  "metadata": {
    "title": "Example",
    "description": "...",
    "language": "en",
    "word_count": 1234
  },
  "markdown": "# Page Title\n\nContent here...",
  "cache": { "status": "miss" }
}
```

**Format options:**
- `markdown` — clean markdown, best for general use
- `text` — plain text without formatting
- `llm` — optimized for LLM consumption: includes page title, URL, and cleaned content with link references. Best for feeding to AI models.
- `json` — full extraction result with all metadata

**When antibot bypass activates** (automatic, no extra config):
```json
{
  "antibot": {
    "solver": "cloudflare",
    "challenge": "turnstile",
    "elapsed_ms": 3200
  }
}
```

### 2. Crawl — scrape an entire website

Starts an async job. Poll for results.

**Start crawl:**
```bash
curl -X POST https://api.webclaw.io/v1/crawl \
  -H "Authorization: Bearer $WEBCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.example.com",
    "max_depth": 3,
    "max_pages": 50,
    "use_sitemap": true
  }'
```

Response: `{ "job_id": "abc-123", "status": "running" }`

**Poll status:**
```bash
curl https://api.webclaw.io/v1/crawl/abc-123 \
  -H "Authorization: Bearer $WEBCLAW_API_KEY"
```

Response when complete:
```json
{
  "job_id": "abc-123",
  "status": "completed",
  "total": 47,
  "completed": 45,
  "errors": 2,
  "pages": [
    {
      "url": "https://docs.example.com/intro",
      "markdown": "# Introduction\n...",
      "metadata": { "title": "Intro", "word_count": 500 }
    }
  ]
}
```

**Request fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | string | required | Starting URL |
| `max_depth` | int | `3` | How many links deep to follow |
| `max_pages` | int | `100` | Maximum pages to crawl |
| `use_sitemap` | bool | `false` | Seed URLs from sitemap.xml |
| `formats` | string[] | `["markdown"]` | Output formats per page |
| `include_selectors` | string[] | `[]` | CSS selectors to keep |
| `exclude_selectors` | string[] | `[]` | CSS selectors to remove |
| `only_main_content` | bool | `false` | Main content only |

### 3. Map — discover all URLs on a site

Fast URL discovery without full content extraction.

```bash
curl -X POST https://api.webclaw.io/v1/map \
  -H "Authorization: Bearer $WEBCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Response:
```json
{
  "url": "https://example.com",
  "count": 142,
  "urls": [
    "https://example.com/about",
    "https://example.com/pricing",
    "https://example.com/docs/intro"
  ]
}
```

### 4. Batch — scrape multiple URLs in parallel

```bash
curl -X POST https://api.webclaw.io/v1/batch \
  -H "Authorization: Bearer $WEBCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://a.com",
      "https://b.com",
      "https://c.com"
    ],
    "formats": ["markdown"],
    "concurrency": 5
  }'
```

Response:
```json
{
  "total": 3,
  "completed": 3,
  "errors": 0,
  "results": [
    { "url": "https://a.com", "markdown": "...", "metadata": {} },
    { "url": "https://b.com", "markdown": "...", "metadata": {} },
    { "url": "https://c.com", "error": "timeout" }
  ]
}
```

### 5. Extract — LLM-powered structured extraction

Pull structured data from any page using a JSON schema or plain-text prompt.

**With JSON schema:**
```bash
curl -X POST https://api.webclaw.io/v1/extract \
  -H "Authorization: Bearer $WEBCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/pricing",
    "schema": {
      "type": "object",
      "properties": {
        "plans": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "price": { "type": "string" },
              "features": { "type": "array", "items": { "type": "string" } }
            }
          }
        }
      }
    }
  }'
```

**With prompt:**
```bash
curl -X POST https://api.webclaw.io/v1/extract \
  -H "Authorization: Bearer $WEBCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/pricing",
    "prompt": "Extract all pricing tiers with names, monthly prices, and key features"
  }'
```

Response:
```json
{
  "url": "https://example.com/pricing",
  "data": {
    "plans": [
      { "name": "Starter", "price": "$49/mo", "features": ["10k pages", "Email support"] },
      { "name": "Pro", "price": "$99/mo", "features": ["100k pages", "Priority support", "API access"] }
    ]
  }
}
```

### 6. Summarize — get a quick summary of any page

```bash
curl -X POST https://api.webclaw.io/v1/summarize \
  -H "Authorization: Bearer $WEBCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/long-article",
    "max_sentences": 3
  }'
```

Response:
```json
{
  "url": "https://example.com/long-article",
  "summary": "The article discusses... Key findings include... The author concludes that..."
}
```

### 7. Diff — detect content changes

Compare current page content against a previous snapshot.

```bash
curl -X POST https://api.webclaw.io/v1/diff \
  -H "Authorization: Bearer $WEBCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "previous": {
      "markdown": "# Old content...",
      "metadata": { "title": "Old Title" }
    }
  }'
```

Response:
```json
{
  "url": "https://example.com",
  "status": "changed",
  "diff": "--- previous\n+++ current\n@@ -1 +1 @@\n-# Old content\n+# New content",
  "metadata_changes": [
    { "field": "title", "old": "Old Title", "new": "New Title" }
  ]
}
```

### 8. Brand — extract brand identity

Analyze a website's visual identity: colors, fonts, logo.

```bash
curl -X POST https://api.webclaw.io/v1/brand \
  -H "Authorization: Bearer $WEBCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Response:
```json
{
  "url": "https://example.com",
  "brand": {
    "colors": [
      { "hex": "#FF6B35", "usage": "primary" },
      { "hex": "#1A1A2E", "usage": "background" }
    ],
    "fonts": ["Inter", "JetBrains Mono"],
    "logo_url": "https://example.com/logo.svg",
    "favicon_url": "https://example.com/favicon.ico"
  }
}
```

## Choosing the right format

| Goal | Format | Why |
|------|--------|-----|
| Read and understand a page | `markdown` | Clean structure, headings, links preserved |
| Feed content to an AI model | `llm` | Optimized: includes title + URL header, clean link refs |
| Search or index content | `text` | Plain text, no formatting noise |
| Programmatic analysis | `json` | Full metadata, structured data, DOM statistics |

## Tips

- **Use `llm` format** when passing content to yourself or another AI — it's specifically optimized for LLM consumption with better context framing.
- **Use `only_main_content: true`** to skip navigation, sidebars, and footers. Reduces noise significantly.
- **Use `include_selectors`/`exclude_selectors`** for fine-grained control when `only_main_content` isn't enough.
- **Batch over individual scrapes** when fetching multiple URLs — it's faster and more efficient.
- **Use `map` before `crawl`** to discover the site structure first, then crawl specific sections.
- **Use `extract` with a JSON schema** for reliable structured output (e.g., pricing tables, product specs, contact info).
- **Antibot bypass is automatic** — no extra configuration needed. Works on Cloudflare, DataDome, AWS WAF, and JS-rendered SPAs.

## vs web_fetch

| | webclaw | web_fetch |
|---|---------|-----------|
| Cloudflare bypass | Automatic | Fails (403) |
| JS-rendered pages | Automatic fallback | Readability only |
| Output quality | 20-step optimization pipeline | Basic HTML parsing |
| Structured extraction | LLM-powered, schema-based | None |
| Crawling | Full site crawl with sitemap | Single page only |
| Caching | Built-in, configurable TTL | Per-session |
| Rate limiting | Managed server-side | Client responsibility |

Use `web_fetch` for simple, fast lookups. Use webclaw when you need reliability, quality, or advanced features.
