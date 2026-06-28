from .base import safe_get
from typing import Optional


async def collect_defillama_data(protocol_name: str) -> dict:
    protocols = await safe_get("https://api.llama.fi/protocols")
    if not protocols:
        return {"found": False, "protocol": protocol_name}

    name_lower = protocol_name.lower()
    match = None
    for p in protocols:
        if (
            name_lower in p.get("name", "").lower()
            or name_lower in p.get("slug", "").lower()
        ):
            match = p
            break

    if not match:
        return {"found": False, "protocol": protocol_name, "summary": f"{protocol_name} not found on DefiLlama"}

    slug = match.get("slug", "")
    detail = await safe_get(f"https://api.llama.fi/protocol/{slug}")

    return {
        "found": True,
        "name": match.get("name"),
        "slug": slug,
        "category": match.get("category"),
        "chains": match.get("chains", []),
        "tvl": match.get("tvl", 0),
        "tvl_change_24h": match.get("change_1d"),
        "tvl_change_7d": match.get("change_7d"),
        "mcap_tvl": match.get("mcap") / match.get("tvl", 1) if match.get("mcap") and match.get("tvl") else None,
        "audit_links": detail.get("audit_links", []) if detail else [],
        "audits": detail.get("audits") if detail else None,
        "oracles": detail.get("oracles", []) if detail else [],
        "description": detail.get("description") if detail else match.get("description"),
        "twitter": detail.get("twitter") if detail else None,
        "url": detail.get("url") if detail else None,
        "gecko_id": match.get("gecko_id"),
    }
