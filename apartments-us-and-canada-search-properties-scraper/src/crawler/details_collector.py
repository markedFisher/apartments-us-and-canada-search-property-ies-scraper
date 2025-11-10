import asyncio
from typing import Dict, Iterable, List

import httpx

from extractors.listing_parser import parse_listing_page

async def _fetch_detail(
    client: httpx.AsyncClient,
    url: str,
    sem: asyncio.Semaphore,
    attempt: int,
    max_attempts: int,
    backoff_ms: int,
) -> Dict:
    async with sem:
        try:
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
            html = r.text
            return parse_listing_page(url, html)
        except Exception as e:
            if attempt >= max_attempts:
                return {"url": url, "_error": str(e)}
            await asyncio.sleep((backoff_ms / 1000.0) * (2 ** (attempt - 1)))
            return await _fetch_detail(client, url, sem, attempt + 1, max_attempts, backoff_ms)

async def collect_listing_details(
    client: httpx.AsyncClient,
    listing_urls: Iterable[str],
    concurrency: int = 10,
    retry_attempts: int = 3,
    retry_backoff_base_ms: int = 400,
) -> List[Dict]:
    sem = asyncio.Semaphore(concurrency)
    tasks = [
        asyncio.create_task(_fetch_detail(client, url, sem, 1, retry_attempts, retry_backoff_base_ms))
        for url in listing_urls
    ]
    results: List[Dict] = []
    for t in asyncio.as_completed(tasks):
        result = await t
        results.append(result)
    return results