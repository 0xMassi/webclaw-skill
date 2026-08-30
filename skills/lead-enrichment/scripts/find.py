#!/usr/bin/env python3
"""Lead finding via the webclaw API — the discovery half of the pipeline.

Two ways in, one CSV out (ready for enrich.py):

  1. From a listing page you already know (a directory, an awesome-list,
     a "best X tools" article, a YC/PH category page):
       python3 find.py --url https://www.ycombinator.com/companies/industry/developer-tools

  2. From a plain-language ICP description (searches the web, then harvests
     the listicles and directories it finds):
       python3 find.py --query "AI agent startups that read the web"

Output: leads.csv (name, website, one_liner, source). Stdlib only.
"""

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

API = "https://api.webclaw.io/v1"

# Discussion platforms, not listing pages — skipped in --query mode.
SKIP_HOSTS = ("reddit.com", "youtube.com", "x.com", "twitter.com", "linkedin.com", "news.ycombinator.com")
CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

LISTING_SCHEMA = {
    "type": "object",
    "properties": {
        "companies": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "website_or_profile_url": {
                        "type": "string",
                        "description": "the hyperlink TARGET (https://... or a domain), never the link's visible text; empty string if the page shows no link",
                    },
                    "one_liner": {"type": "string"},
                },
            },
            "description": "actual companies/products listed on the page; skip navigation, ads, and the page's own brand",
        }
    },
}


def call(api_key, path, body):
    req = urllib.request.Request(
        f"{API}/{path}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.load(resp), ""
        except urllib.error.HTTPError as e:
            if e.code >= 500 and attempt == 1:
                continue
            return {}, f"HTTP {e.code}"
        except Exception as e:
            if attempt == 1:
                continue
            return {}, str(e)[:80]
    return {}, "unreachable"


def looks_like_url(value):
    """Accept https://... or bare domains; reject link text like 'VIEW PROFILE'."""
    value = value.strip()
    if not value or " " in value or "." not in value:
        return False
    return True


def host_matches(host, suffix):
    """Match a hostname itself or a real subdomain, never a lookalike suffix."""
    return host == suffix or host.endswith(f".{suffix}")


def csv_safe(value):
    """Prevent spreadsheet formula execution when a CSV is opened interactively."""
    text = "" if value is None else str(value)
    return f"'{text}" if text.startswith(CSV_FORMULA_PREFIXES) else text


def companies_from_listing(api_key, url):
    data, err = call(api_key, "extract", {"url": url, "schema": LISTING_SCHEMA})
    if err:
        print(f"  {url[:60]:60} {err}")
        return []
    found = (data.get("data") or {}).get("companies") or []
    print(f"  {url[:60]:60} {len(found)} companies")
    rows = []
    for c in found:
        if not c.get("name"):
            continue
        website = (c.get("website_or_profile_url") or "").strip()
        rows.append(
            {
                "name": c["name"].strip(),
                "website": website if looks_like_url(website) else "",
                "one_liner": (c.get("one_liner") or "").strip()[:160],
                "source": url,
            }
        )
    return rows


def listing_urls_from_query(api_key, query, max_sources):
    data, err = call(api_key, "search", {"query": query, "num_results": 10})
    if err:
        sys.exit(f"search failed: {err}")
    urls = []
    for r in data.get("results", []):
        url = r.get("url") or ""
        host = urlparse(url).netloc.lower()
        if any(host_matches(host, suffix) for suffix in SKIP_HOSTS):
            continue
        urls.append(url)
        if len(urls) >= max_sources:
            break
    return urls


def main():
    parser = argparse.ArgumentParser(description="Find leads from listing pages or an ICP query")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", action="append", help="listing page URL (repeatable)")
    src.add_argument("--query", help="plain-language ICP description to search for")
    parser.add_argument("--out", default="leads.csv")
    parser.add_argument("--sources", type=int, default=4, help="max listing pages to harvest in --query mode")
    args = parser.parse_args()

    api_key = os.environ.get("WEBCLAW_API_KEY", "")
    if not api_key:
        sys.exit("WEBCLAW_API_KEY is not set. Get a key at https://webclaw.io (free tier works).")

    if args.query:
        print(f"searching listing pages for: {args.query}")
        urls = listing_urls_from_query(api_key, args.query, args.sources)
        if not urls:
            sys.exit("search returned no usable listing pages; try rephrasing the query")
    else:
        urls = args.url

    print(f"harvesting {len(urls)} listing page(s):")
    seen, rows = set(), []
    for url in urls:
        for c in companies_from_listing(api_key, url):
            key = c["name"].lower() or urlparse(c["website"]).netloc.lower()
            if key in seen:
                continue
            seen.add(key)
            rows.append(c)

    if not rows:
        sys.exit("no companies found on the given page(s)")

    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "website", "one_liner", "source"])
        writer.writeheader()
        writer.writerows(
            {key: csv_safe(value) for key, value in row.items()} for row in rows
        )

    missing = sum(1 for r in rows if not r["website"])
    print(f"done -> {args.out} ({len(rows)} unique companies, {missing} without a usable website URL)")
    if missing:
        print("tip: fill missing websites with a web search per name, or drop those rows before enriching")
    print(f"next: WEBCLAW_API_KEY=... python3 enrich.py {args.out}")


if __name__ == "__main__":
    main()
