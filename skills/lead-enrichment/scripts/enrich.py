#!/usr/bin/env python3
"""Bulk lead enrichment via the webclaw API.

Reads a CSV with a website/domain column, enriches each company from its own
public site through POST /v1/extract, and writes <input>-enriched.csv with the
original columns plus the extracted fields. Stdlib only, no dependencies.

Usage:
  WEBCLAW_API_KEY=wc_... python3 enrich.py leads.csv
  python3 enrich.py leads.csv --out enriched.csv --concurrency 5 --limit 10
  python3 enrich.py leads.csv --schema my_schema.json
"""

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://api.webclaw.io/v1/extract"

# Fields worth having for every B2B lead; override with --schema.
DEFAULT_SCHEMA = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "one_line_pitch": {"type": "string"},
        "contact_email": {
            "type": "string",
            "description": "a published business contact email, empty string if none is public",
        },
        "social_links": {"type": "array", "items": {"type": "string"}},
        "pricing_model": {
            "type": "string",
            "description": "free / freemium / paid / enterprise / unknown",
        },
        "target_customer": {"type": "string"},
        "tech_signals": {
            "type": "array",
            "items": {"type": "string"},
            "description": "frameworks, APIs, and integrations the site mentions",
        },
    },
}

URL_COLUMNS = ("website", "domain", "url", "website_url", "company_url", "site")
CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def find_url_column(fieldnames):
    lowered = {name.lower().strip(): name for name in fieldnames}
    for candidate in URL_COLUMNS:
        if candidate in lowered:
            return lowered[candidate]
    return fieldnames[0]  # fall back to the first column


def normalize(raw):
    raw = raw.strip()
    if not raw:
        return ""
    return raw if raw.startswith(("http://", "https://")) else f"https://{raw}"


def enrich_one(api_key, url, schema):
    body = json.dumps({"url": url, "schema": schema}).encode()
    req = urllib.request.Request(
        API,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    for attempt in (1, 2):  # one retry on transient failures
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.load(resp).get("data") or {}, ""
        except urllib.error.HTTPError as e:
            if e.code >= 500 and attempt == 1:
                continue
            return {}, f"HTTP {e.code}"
        except Exception as e:
            if attempt == 1:
                continue
            return {}, str(e)[:80]
    return {}, "unreachable"


def flatten(value):
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    return "" if value is None else str(value)


def csv_safe(value):
    """Prevent spreadsheet formula execution when a CSV is opened interactively."""
    text = "" if value is None else str(value)
    return f"'{text}" if text.startswith(CSV_FORMULA_PREFIXES) else text


def main():
    parser = argparse.ArgumentParser(description="Enrich a CSV of company websites via webclaw")
    parser.add_argument("input", help="CSV with a website/domain/url column")
    parser.add_argument("--out", help="output path (default: <input>-enriched.csv)")
    parser.add_argument("--schema", help="path to a custom JSON schema for the fields to extract")
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--limit", type=int, help="only enrich the first N rows (handy for a test run)")
    args = parser.parse_args()

    api_key = os.environ.get("WEBCLAW_API_KEY", "")
    if not api_key:
        sys.exit("WEBCLAW_API_KEY is not set. Get a key at https://webclaw.io (free tier works).")

    schema = DEFAULT_SCHEMA
    if args.schema:
        with open(args.schema) as f:
            schema = json.load(f)

    with open(args.input, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    if not rows:
        sys.exit(f"{args.input} has no data rows.")
    if args.limit:
        rows = rows[: args.limit]

    url_col = find_url_column(fieldnames)
    enrich_cols = list(schema.get("properties", {}).keys())
    out_path = args.out or args.input.rsplit(".", 1)[0] + "-enriched.csv"

    print(f"enriching {len(rows)} rows from '{url_col}' column -> {out_path}")

    def work(row):
        url = normalize(row.get(url_col, ""))
        if not url:
            return row, {}, "empty url"
        data, err = enrich_one(api_key, url, schema)
        return row, data, err

    done = 0
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool, open(
        out_path, "w", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames + enrich_cols + ["enrich_error"])
        writer.writeheader()
        for row, data, err in pool.map(work, rows):
            for col in enrich_cols:
                row[col] = flatten(data.get(col))
            row["enrich_error"] = err
            writer.writerow({key: csv_safe(value) for key, value in row.items()})
            done += 1
            status = "ok" if not err else err
            print(f"  [{done}/{len(rows)}] {row.get(url_col, '')[:40]:40} {status}")

    print(f"done -> {out_path}")


if __name__ == "__main__":
    main()
