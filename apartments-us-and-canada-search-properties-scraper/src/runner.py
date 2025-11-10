import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Set

import ujson as json_fast

from crawler.search_collector import collect_search_results
from crawler.details_collector import collect_listing_details
from crawler.throttling import make_http_client
from outputs.exporters import export_json, export_csv

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
        try:
            return json_fast.loads(text)
        except Exception:
            # fallback to stdlib for friendlier errors
            return json.loads(text)

def merge_settings(defaults: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(defaults or {})
    for k, v in (overrides or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge_settings(out[k], v)
        else:
            out[k] = v
    return out

async def main() -> None:
    parser = argparse.ArgumentParser(description="Apartments.com US & Canada Scraper")
    parser.add_argument(
        "--inputs",
        default=str(Path("data") / "inputs.sample.json"),
        help="Path to JSON file containing `searchUrls` and/or `listingUrls`.",
    )
    parser.add_argument(
        "--settings",
        default=str(Path("src") / "config" / "settings.example.json"),
        help="Path to settings JSON.",
    )
    parser.add_argument(
        "--proxies",
        default=str(Path("src") / "config" / "proxies.example.json"),
        help="Path to proxies JSON (optional).",
    )
    parser.add_argument(
        "--out",
        default=str(Path("data") / "output.json"),
        help="Output file path (json or csv by extension).",
    )
    args = parser.parse_args()

    settings = load_json(args.settings)
    inputs = load_json(args.inputs)

    if os.path.exists(args.proxies):
        proxies = load_json(args.proxies)
    else:
        proxies = {"http": None, "https": None}

    # Allow ENV overrides
    env_out = os.getenv("OUTPUT_PATH")
    if env_out:
        args.out = env_out

    # Merge CLI-style overrides (none for now) and environment
    cfg = merge_settings(
        {
            "http": {
                "timeout_secs": 25,
                "max_connections": 40,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36 BitbashScraper/1.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            },
            "crawler": {
                "concurrency": 12,
                "retry_attempts": 3,
                "retry_backoff_base_ms": 400,
                "follow_details": True,
                "respect_robots": False,
            },
        },
        settings,
    )

    async with make_http_client(
        headers=cfg["http"]["headers"],
        timeout=cfg["http"]["timeout_secs"],
        max_connections=cfg["http"]["max_connections"],
        proxies=proxies,
    ) as client:
        # 1) Gather listing URLs
        input_search_urls: List[str] = inputs.get("searchUrls", []) or []
        input_listing_urls: List[str] = inputs.get("listingUrls", []) or []

        listing_urls: Set[str] = set(input_listing_urls)
        if input_search_urls:
            found = await collect_search_results(
                client=client,
                search_urls=input_search_urls,
                concurrency=cfg["crawler"]["concurrency"],
                retry_attempts=cfg["crawler"]["retry_attempts"],
                retry_backoff_base_ms=cfg["crawler"]["retry_backoff_base_ms"],
            )
            listing_urls.update(found)

        listing_urls = {u for u in listing_urls if "apartments.com" in u}

        # 2) Fetch details
        results = []
        if cfg["crawler"]["follow_details"] and listing_urls:
            results = await collect_listing_details(
                client=client,
                listing_urls=sorted(list(listing_urls)),
                concurrency=cfg["crawler"]["concurrency"],
                retry_attempts=cfg["crawler"]["retry_attempts"],
                retry_backoff_base_ms=cfg["crawler"]["retry_backoff_base_ms"],
            )

    # 3) Export
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.suffix.lower() == ".csv":
        export_csv(results, str(out_path))
    else:
        export_json(results, str(out_path))

    print(f"Wrote {len(results)} records to {out_path}")

if __name__ == "__main__":
    asyncio.run(main())