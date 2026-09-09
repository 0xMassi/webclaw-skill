---
name: lead-enrichment
description: Discover and qualify B2B leads using webclaw. Start from a CSV of domains, a directory or "best tools" listing URL, or a plain-language ICP description — get back an enriched sheet of firmographics (company name, pitch, published contact email, socials, pricing model, target customer, tech signals, or any custom field) read from each company's own site via /v1/extract. Use when the user wants to find/discover leads, build a prospect list, qualify companies from their websites, or asks for a "Clay alternative" without per-seat pricing. Billed per extract call, not per seat.
homepage: https://webclaw.io
user-invocable: true
metadata: {"openclaw":{"emoji":"🎯","homepage":"https://webclaw.io"}}
---

# Lead finding + enrichment with webclaw

Start from whatever the user has — a CSV, a listing URL, or just a description of who they sell to — and end with an enriched lead sheet: what each company does, who it sells to, a published contact email, socials, pricing model, and the tech it mentions. Everything comes from each company's own public pages — no licensed contact database, no per-seat platform.

## What this skill does (and what it doesn't)

This skill is the **discovery + firmographics** half of lead gen. It finds companies (from listings or an ICP) and reads generic facts off each company's own site via `/v1/extract` — pitch, a published contact email, socials, pricing model, target customer, tech signals, or **any custom field you define**. That flexible schema is its whole point.

Run `find.py` to build the company list, then `enrich.py` to extract custom fields from each website. Results are limited to information published on the pages you provide.

## Prerequisites

The [webclaw skill / MCP server](https://webclaw.io) (`npx create-webclaw`). For bulk runs, a `WEBCLAW_API_KEY` (free tier at webclaw.io works).

## Pick the entry point by what the user has

| The user has... | Do this |
|---|---|
| A CSV of domains | Enrich it directly (below) |
| A listing URL — a directory, awesome-list, "best X tools" article, YC/PH category page | `find.py --url <listing>` → then enrich |
| Just a description of their ICP | `find.py --query "..."` → review the found list with the user → then enrich |
| A competitor name | `find.py --query "<competitor> alternatives"` → then enrich |
| One target account to research deeply | Skip the scripts: `crawl` the site (depth 2), then `extract` a detailed profile from the key pages |

## Finding leads (`scripts/find.py`)

```bash
# from a listing page you already know (repeatable --url)
WEBCLAW_API_KEY=wc_... python3 scripts/find.py --url https://www.ycombinator.com/companies/industry/developer-tools

# from a plain-language ICP — searches the web, harvests the listicles it finds
WEBCLAW_API_KEY=wc_... python3 scripts/find.py --query "AI agent startups that read the web"
```

Writes `leads.csv` (name, website, one_liner, source), deduped across sources. "Best X tools" articles and directories are pre-curated lead lists — this harvests them. Note: directory pages (YC, PH) often yield profile URLs rather than company homepages; enrichment still works on those, but if the user wants homepage-level fields, extract the real website from each profile first.

### Example: revenue-qualified leads from TrustMRR

[trustmrr.com](https://trustmrr.com) is a public database of 15,000+ startups with payment-provider-verified revenue, and it is deliberately AI-friendly (llms.txt, per-startup `.md` pages, an AI API). Its category pages make excellent find sources, and profile pages enrich into revenue-qualified leads:

```bash
python3 scripts/find.py --url https://trustmrr.com/category/ai --out leads.csv
python3 scripts/enrich.py leads.csv --schema revenue.json
```

with `revenue.json` asking for `monthly_revenue`, `founder_name`, `founder_x_handle`, and `actual_website`. Verified result in testing: MRR figures, founder names, X handles, and the startup's real site — a lead sheet where every row provably has revenue. If the user wants homepage-level fields too, run a second enrich pass over the `actual_website` column.

## Two paths

### Small lists (up to ~15 companies): drive the MCP tools directly

For each row, call the webclaw `extract` tool with the company URL and this schema, then assemble the results into a table or CSV yourself:

```json
{
  "type": "object",
  "properties": {
    "company_name":    {"type": "string"},
    "one_line_pitch":  {"type": "string"},
    "contact_email":   {"type": "string", "description": "a published business contact email, empty string if none is public"},
    "social_links":    {"type": "array", "items": {"type": "string"}},
    "pricing_model":   {"type": "string", "description": "free / freemium / paid / enterprise / unknown"},
    "target_customer": {"type": "string"},
    "tech_signals":    {"type": "array", "items": {"type": "string"}, "description": "frameworks, APIs, and integrations the site mentions"}
  }
}
```

One call per company, a few seconds each. Runs locally where possible; bot-protected or JS-heavy sites escalate to the hosted engine when `WEBCLAW_API_KEY` is set.

### Bulk lists (15+): run the bundled script

```bash
WEBCLAW_API_KEY=wc_... python3 scripts/enrich.py leads.csv
```

- Auto-detects the URL column (`website`, `domain`, `url`, ...), enriches concurrently, and writes `leads-enriched.csv` with the original columns plus the extracted fields and an `enrich_error` column for any row that failed.
- `--limit 5` for a cheap test run first. `--concurrency`, `--out` as needed.
- Python stdlib only — no installs.

## Custom fields

The fields are just a JSON schema, so change them to fit the play. Write the schema to a file and pass `--schema`:

```bash
python3 scripts/enrich.py leads.csv --schema hiring_signals.json
```

Examples that work well: `is_hiring`, `has_api`, `uses_competitor_x`, `recent_funding_mentioned`, `languages_supported`, `has_free_tier`. Anything a human could answer by reading the company's site, the extractor can answer too.

## Workflow for the agent

1. Ask for (or locate) the input CSV and confirm which column holds the website.
2. If the user wants non-default fields, build the schema with them before running.
3. Small list → per-row `extract` calls; bulk → `scripts/enrich.py` with `--limit 5` first, show the sample, then run the full list.
4. Summarize results: how many rows enriched, how many had a published email, notable patterns (pricing models, common tech).
5. Suggest next steps: sort by fit, or feed the output into their CRM.

## Notes

- **Respect privacy law.** This extracts only what companies publish on their own sites, and it's the user's responsibility to use contact data lawfully (GDPR/CAN-SPAM). Enrich business sites, not personal pages.
- Expect some empty `contact_email` fields — many companies publish none. That's signal too. `contact_email` here is a *published* mailbox off the site (e.g. `hello@company.com`), not a person.
- Cost: each company sends one `/v1/extract` request. Check your current plan for its credit cost.
