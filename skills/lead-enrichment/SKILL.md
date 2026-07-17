---
name: lead-enrichment
description: Turn a list of company domains into an enriched lead sheet using webclaw. Reads a CSV of websites and extracts company name, pitch, published contact email, socials, pricing model, target customer, and tech signals from each company's own site. Use when the user wants to enrich leads, build a prospect list, qualify companies from their websites, or asks for a "Clay alternative" without per-seat pricing. Costs about a dollar per 100 leads on the hosted API.
homepage: https://webclaw.io
user-invocable: true
metadata: {"openclaw":{"emoji":"🎯","homepage":"https://webclaw.io"}}
---

# Lead enrichment with webclaw

Point this skill at a CSV of company websites and get back the same CSV with the columns a lead list actually needs: what the company does, who it sells to, a published contact email, socials, pricing model, and the tech it mentions. Everything comes from each company's own public site — no licensed contact database, no per-seat platform.

## Prerequisites

The [webclaw skill / MCP server](https://webclaw.io) (`npx create-webclaw`). For bulk runs, a `WEBCLAW_API_KEY` (free tier at webclaw.io works).

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
- Expect some empty `contact_email` fields — many companies publish none. That's signal too.
- Rough cost on the hosted API: about a dollar per 100 leads.
