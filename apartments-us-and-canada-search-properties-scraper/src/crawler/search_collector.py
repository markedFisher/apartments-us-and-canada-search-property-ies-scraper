import asyncio
import re
from typing import Iterable, List, Set

import httpx
from bs4 import BeautifulSoup

APARTMENTS_HOST = "apartments.com"

# Regex catches typical detail URLs like:
# https://www.apartments.com/904-pittsburg-ave-winston-salem-nc/ymg5lhs/
DETAIL_URL_RE = re.compile(r"https?://(?:www\.)?apartments\.com/[^\"'<>]+?/[a-z0-9]{3,8}/", re.IGNORECASE)

async def _fetch(client: httpx.AsyncClient, url: str) -> str:
    r = await client.get(url, follow_redirects=True)
    r.raise_for_status()
    return r.text

def _extract_detail_links(html: str) -> Set[str]:
    links: Set[str] = set()
    # Prefer fast regex, then validate via parsing
    for m in DETAIL_URL_RE.finditer(html):
        links.add(m.group(0))

    soup = BeautifulSoup(html, "lxml")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if APARTMENTS_HOST in href and DETAIL_URL_RE.search(href):
            links.add(href)
    return links

async def _collect_from_one(client: httpx.AsyncClient, url: str, sem: asyncio.Semaphore, attempt: int = 1, max_attempts: int = 3, backoff_ms: int = 400) -> Set[str]:
    async with sem:
        try:
            html = await _fetch(client, url)
            return _extract_detail_links(html)
        except Exception:
            if attempt >= max_attempts:
                return set()
            await asyncio.sleep((backoff_ms / 1000.0) * (2 ** (attempt - 1)))
            return await _collect_from_one(client, url, sem, attempt + 1, max_attempts, backoff_ms)

async def collect_search_results(
    client: httpx.AsyncClient,
    search_urls: Iterable[str],
    concurrency: int = 10,
    retry_attempts: int = 3,
    retry_backoff_base_ms: int = 400,
) -> Set[str]:
    sem = asyncio.Semaphore(concurrency)
    tasks = [
        asyncio.create_task(_collect_from_one(client, url, sem, 1, retry_attempts, retry_backoff_base_ms))
        for url in search_urls
    ]
    all_links: Set[str] = set()
    for coro in asyncio.as_completed(tasks):
        links = await coro
        all_links.update(links)
    return all_links