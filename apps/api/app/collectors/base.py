import aiohttp
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "TrustLayer/1.0 (Web3 Due Diligence Platform)",
    "Accept": "application/json",
}

async def safe_get(url: str, params: dict = None, headers: dict = None, timeout: int = 15) -> Optional[dict]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params=params,
                headers={**HEADERS, **(headers or {})},
                timeout=aiohttp.ClientTimeout(total=timeout),
                ssl=False,
            ) as resp:
                if resp.status == 200:
                    return await resp.json(content_type=None)
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
    return None
