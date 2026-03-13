#!/usr/bin/env python3
"""webclaw CLI wrapper for OpenClaw agents.

Usage:
  python3 scripts/webclaw.py scrape <url> [--format markdown|text|llm|json] [--main] [--no-cache]
  python3 scripts/webclaw.py crawl <url> [--depth N] [--pages N] [--sitemap]
  python3 scripts/webclaw.py crawl-status <job_id>
  python3 scripts/webclaw.py map <url>
  python3 scripts/webclaw.py batch <url1> <url2> ... [--format markdown|text|llm]
  python3 scripts/webclaw.py extract <url> --prompt "..." | --schema '{"type":"object",...}'
  python3 scripts/webclaw.py summarize <url> [--sentences N]
  python3 scripts/webclaw.py diff <url> --previous <file.json>
  python3 scripts/webclaw.py brand <url>
"""

import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://api.webclaw.io/v1"


def get_api_key():
    key = os.environ.get("WEBCLAW_API_KEY", "")
    if not key:
        # Check workspace secrets (OpenClaw convention)
        for path in ["workspace/secrets/webclaw_api_key", "secrets/webclaw_api_key"]:
            if os.path.isfile(path):
                with open(path) as f:
                    key = f.read().strip()
                if key:
                    break
    if not key:
        print("Error: WEBCLAW_API_KEY not set. Get one at https://webclaw.io", file=sys.stderr)
        sys.exit(1)
    return key


def api(endpoint, body):
    key = get_api_key()
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{API_BASE}/{endpoint}",
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            err = json.loads(body)
            print(f"Error {e.code}: {err.get('error', body)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def api_get(endpoint):
    key = get_api_key()
    req = urllib.request.Request(
        f"{API_BASE}/{endpoint}",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def cmd_scrape(args):
    url = args[0]
    fmt = "markdown"
    main_only = False
    no_cache = False
    include = []
    exclude = []

    i = 1
    while i < len(args):
        if args[i] in ("--format", "-f") and i + 1 < len(args):
            fmt = args[i + 1]
            i += 2
        elif args[i] == "--main":
            main_only = True
            i += 1
        elif args[i] == "--no-cache":
            no_cache = True
            i += 1
        elif args[i] == "--include" and i + 1 < len(args):
            include = args[i + 1].split(",")
            i += 2
        elif args[i] == "--exclude" and i + 1 < len(args):
            exclude = args[i + 1].split(",")
            i += 2
        else:
            i += 1

    body = {"url": url, "formats": [fmt]}
    if main_only:
        body["only_main_content"] = True
    if no_cache:
        body["no_cache"] = True
    if include:
        body["include_selectors"] = include
    if exclude:
        body["exclude_selectors"] = exclude

    result = api("scrape", body)

    # Print the requested format's content
    content = result.get(fmt) or result.get("markdown") or ""
    if content:
        print(content)
    else:
        print(json.dumps(result, indent=2))


def cmd_crawl(args):
    url = args[0]
    depth = 3
    pages = 50
    sitemap = False

    i = 1
    while i < len(args):
        if args[i] == "--depth" and i + 1 < len(args):
            depth = int(args[i + 1])
            i += 2
        elif args[i] == "--pages" and i + 1 < len(args):
            pages = int(args[i + 1])
            i += 2
        elif args[i] == "--sitemap":
            sitemap = True
            i += 1
        else:
            i += 1

    body = {"url": url, "max_depth": depth, "max_pages": pages}
    if sitemap:
        body["use_sitemap"] = True

    result = api("crawl", body)
    job_id = result.get("job_id", "")
    print(f"Crawl started: {job_id}")
    print(f"Check status: python3 scripts/webclaw.py crawl-status {job_id}")


def cmd_crawl_status(args):
    job_id = args[0]
    result = api_get(f"crawl/{job_id}")
    print(json.dumps(result, indent=2))


def cmd_map(args):
    url = args[0]
    result = api("map", {"url": url})
    count = result.get("count", 0)
    print(f"Found {count} URLs:")
    for u in result.get("urls", []):
        print(f"  {u}")


def cmd_batch(args):
    urls = []
    fmt = "markdown"
    i = 0
    while i < len(args):
        if args[i] in ("--format", "-f") and i + 1 < len(args):
            fmt = args[i + 1]
            i += 2
        else:
            urls.append(args[i])
            i += 1

    result = api("batch", {"urls": urls, "formats": [fmt]})
    for item in result.get("results", []):
        url = item.get("url", "?")
        if item.get("error"):
            print(f"FAIL {url}: {item['error']}")
        else:
            content = item.get(fmt) or item.get("markdown") or ""
            print(f"--- {url} ({len(content)} chars) ---")
            print(content[:500])
            if len(content) > 500:
                print(f"  ... ({len(content) - 500} more chars)")
            print()


def cmd_extract(args):
    url = args[0]
    prompt = None
    schema = None

    i = 1
    while i < len(args):
        if args[i] == "--prompt" and i + 1 < len(args):
            prompt = args[i + 1]
            i += 2
        elif args[i] == "--schema" and i + 1 < len(args):
            schema = json.loads(args[i + 1])
            i += 2
        else:
            i += 1

    body = {"url": url}
    if schema:
        body["schema"] = schema
    elif prompt:
        body["prompt"] = prompt
    else:
        print("Error: --prompt or --schema required", file=sys.stderr)
        sys.exit(1)

    result = api("extract", body)
    print(json.dumps(result.get("data", result), indent=2))


def cmd_summarize(args):
    url = args[0]
    sentences = None

    i = 1
    while i < len(args):
        if args[i] == "--sentences" and i + 1 < len(args):
            sentences = int(args[i + 1])
            i += 2
        else:
            i += 1

    body = {"url": url}
    if sentences:
        body["max_sentences"] = sentences

    result = api("summarize", body)
    print(result.get("summary", json.dumps(result, indent=2)))


def cmd_diff(args):
    url = args[0]
    prev_file = None

    i = 1
    while i < len(args):
        if args[i] == "--previous" and i + 1 < len(args):
            prev_file = args[i + 1]
            i += 2
        else:
            i += 1

    if not prev_file:
        print("Error: --previous <file.json> required", file=sys.stderr)
        sys.exit(1)

    with open(prev_file) as f:
        previous = json.load(f)

    result = api("diff", {"url": url, "previous": previous})
    print(json.dumps(result, indent=2))


def cmd_brand(args):
    url = args[0]
    result = api("brand", {"url": url})
    print(json.dumps(result.get("brand", result), indent=2))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "scrape": cmd_scrape,
        "crawl": cmd_crawl,
        "crawl-status": cmd_crawl_status,
        "map": cmd_map,
        "batch": cmd_batch,
        "extract": cmd_extract,
        "summarize": cmd_summarize,
        "diff": cmd_diff,
        "brand": cmd_brand,
    }

    fn = commands.get(cmd)
    if not fn:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(commands.keys())}")
        sys.exit(1)

    fn(args)


if __name__ == "__main__":
    main()
