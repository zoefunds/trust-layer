import asyncio
from .github import collect_github_data
from .defillama import collect_defillama_data
from .coingecko import collect_coingecko_data


async def collect_all_evidence(protocol_name: str) -> dict:
    github, defillama, coingecko = await asyncio.gather(
        collect_github_data(protocol_name),
        collect_defillama_data(protocol_name),
        collect_coingecko_data(protocol_name),
        return_exceptions=True,
    )

    return {
        "protocol": protocol_name,
        "github": github if not isinstance(github, Exception) else {"found": False, "error": str(github)},
        "defillama": defillama if not isinstance(defillama, Exception) else {"found": False, "error": str(defillama)},
        "coingecko": coingecko if not isinstance(coingecko, Exception) else {"found": False, "error": str(coingecko)},
    }
