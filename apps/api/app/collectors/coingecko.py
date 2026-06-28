from .base import safe_get


async def collect_coingecko_data(protocol_name: str) -> dict:
    slug = protocol_name.lower().replace(" ", "-")
    search = await safe_get(
        "https://api.coingecko.com/api/v3/search",
        params={"query": protocol_name},
    )

    coin_id = None
    if search and search.get("coins"):
        coin_id = search["coins"][0].get("id")

    if not coin_id:
        coin_id = slug

    data = await safe_get(
        f"https://api.coingecko.com/api/v3/coins/{coin_id}",
        params={"localization": "false", "tickers": "false", "community_data": "true"},
    )

    if not data or "error" in data:
        return {"found": False, "protocol": protocol_name}

    market = data.get("market_data", {})
    community = data.get("community_data", {})
    developer = data.get("developer_data", {})

    return {
        "found": True,
        "id": data.get("id"),
        "name": data.get("name"),
        "symbol": data.get("symbol"),
        "market_cap_rank": data.get("market_cap_rank"),
        "price_usd": market.get("current_price", {}).get("usd"),
        "market_cap": market.get("market_cap", {}).get("usd"),
        "total_volume_24h": market.get("total_volume", {}).get("usd"),
        "price_change_24h": market.get("price_change_percentage_24h"),
        "price_change_30d": market.get("price_change_percentage_30d"),
        "all_time_high": market.get("ath", {}).get("usd"),
        "all_time_low": market.get("atl", {}).get("usd"),
        "circulating_supply": market.get("circulating_supply"),
        "total_supply": market.get("total_supply"),
        "max_supply": market.get("max_supply"),
        "twitter_followers": community.get("twitter_followers", 0),
        "reddit_subscribers": community.get("reddit_subscribers", 0),
        "telegram_channel_user_count": community.get("telegram_channel_user_count", 0),
        "github_stars": developer.get("stars", 0),
        "github_forks": developer.get("forks", 0),
        "github_total_issues": developer.get("total_issues", 0),
        "genesis_date": data.get("genesis_date"),
        "categories": data.get("categories", []),
        "description": data.get("description", {}).get("en", "")[:500],
        "homepage": (data.get("links", {}).get("homepage", [None]) or [None])[0],
        "whitepaper": data.get("links", {}).get("whitepaper"),
    }
