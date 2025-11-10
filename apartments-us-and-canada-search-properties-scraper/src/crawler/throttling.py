from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

import httpx

@asynccontextmanager
async def make_http_client(
    headers: Dict[str, str],
    timeout: float,
    max_connections: int,
    proxies: Optional[Dict[str, Optional[str]]] = None,
):
    limits = httpx.Limits(max_connections=max_connections, max_keepalive_connections=max_connections)
    proxy = None
    if proxies:
        # httpx expects a single proxy mapping or str; we pass mapping if provided
        proxy = {}
        if proxies.get("http"):
            proxy["http://"] = proxies["http"]
        if proxies.get("https"):
            proxy["https://"] = proxies["https"]
        if not proxy:
            proxy = None

    async with httpx.AsyncClient(
        headers=headers,
        timeout=timeout,
        limits=limits,
        proxies=proxy,
        http2=False,  # safer for some proxy setups
    ) as client:
        yield client