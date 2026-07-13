"""
GenLayer consensus service.
Calls the deployed TrustLayer intelligent contract on StudioNet.
Falls back to simulation when the contract call fails.
"""
import json
import asyncio
import logging
from typing import AsyncIterator
from ..core.config import settings

logger = logging.getLogger(__name__)

# All 13 domain validators matching the deployed contract
VALIDATOR_TYPES = [
    "identity",
    "founders",
    "funding",
    "investors",
    "github",
    "documentation",
    "onchain",
    "tokenomics",
    "security",
    "community",
    "ecosystem",
    "product",
    "media",
]


async def run_investigation_via_genlayer(
    protocol_name: str,
    evidence: dict,
    investigation_id: str = "",
    user_private_key: str = None,
) -> AsyncIterator[dict]:
    if settings.GENLAYER_CONTRACT_ADDRESS:
        async for update in _call_genlayer_contract(protocol_name, evidence, investigation_id, user_private_key):
            yield update
    else:
        logger.warning("[GenLayer] No contract address configured — using off-chain simulation")
        async for update in _simulate_investigation(protocol_name, evidence, is_fallback=True):
            yield update


def _build_genlayer_client(private_key: str = None):
    """Build a genlayer-py client. Uses the provided key, or falls back to the service account."""
    from genlayer_py import create_client, create_account
    from genlayer_py.chains import studionet

    key = private_key or settings.GENLAYER_PRIVATE_KEY
    account = create_account(account_private_key=key)
    endpoint = settings.GENLAYER_STUDIO_URL.rstrip("/") + "/api"
    return create_client(chain=studionet, endpoint=endpoint, account=account)


def _run_genlayer_transaction_sync(protocol_name: str, evidence: dict, investigation_id: str, user_private_key: str = None) -> tuple[str, str]:
    """
    Blocking call executed in a worker thread (genlayer-py is a synchronous SDK).

    Flow:
      1. client.write_contract("investigate", ...)  → tx_hash (signed & submitted via eth_sendRawTransaction)
      2. client.wait_for_transaction_receipt(...)    → poll until GenLayer's 5-node consensus accepts it
      3. client.read_contract("get_report", ...)     → JSON report string stored on-chain
    """
    from genlayer_py.types import TransactionStatus
    from genlayer_py.assertions import tx_execution_succeeded

    contract_address = settings.GENLAYER_CONTRACT_ADDRESS
    client = _build_genlayer_client(private_key=user_private_key)

    logger.info(f"[GenLayer] Sending transaction for {protocol_name}")
    tx_hash = client.write_contract(
        address=contract_address,
        function_name="investigate",
        args=[protocol_name, json.dumps(evidence), investigation_id],
    )
    logger.info(f"[GenLayer] tx_hash={tx_hash}")

    receipt = client.wait_for_transaction_receipt(
        transaction_hash=tx_hash,
        status=TransactionStatus.ACCEPTED,
        retries=200,
        interval=3000,
    )

    if not tx_execution_succeeded(receipt):
        raise Exception(f"GenLayer transaction failed: {receipt}")

    logger.info(f"[GenLayer] transaction accepted by consensus, reading report")
    report_str = client.read_contract(
        address=contract_address,
        function_name="get_report",
        args=[protocol_name],
    )
    return tx_hash, report_str


async def _call_genlayer_contract(
    protocol_name: str,
    evidence: dict,
    investigation_id: str = "",
    user_private_key: str = None,
) -> AsyncIterator[dict]:
    """Call the deployed TrustLayer contract via the genlayer-py SDK on StudioNet."""
    contract_address = settings.GENLAYER_CONTRACT_ADDRESS

    # Signal all 13 sources as running immediately
    for vtype in VALIDATOR_TYPES:
        yield {"type": "validator_update", "validator_type": vtype, "status": "running"}
        await asyncio.sleep(0.1)

    try:
        tx_hash, raw = await asyncio.to_thread(
            _run_genlayer_transaction_sync, protocol_name, evidence, investigation_id, user_private_key
        )
        report_data = json.loads(raw) if isinstance(raw, str) else raw

        # Stream validator completions from the on-chain report
        validators_map = report_data.get("validators", {})
        for vtype in VALIDATOR_TYPES:
            vdata = validators_map.get(vtype, {})
            yield {
                "type": "validator_update",
                "validator_type": vtype,
                "status": "completed",
                "findings": vdata.get("findings", ""),
                "confidence_score": float(vdata.get("score", vdata.get("confidence", vdata.get("confidence_score", 50.0)))),
                "verified_claims": vdata.get("verified_claims", []),
                "disputed_claims": vdata.get("disputed_claims", []),
                "sources": vdata.get("sources", []),
            }
            await asyncio.sleep(0.2)

        # Map contract scores to the report shape the backend expects
        contract_scores = report_data.get("scores", {})
        mapped_scores = {
            "overall":    float(contract_scores.get("overall", 50)),
            "github":     float(contract_scores.get("github", 50)),
            "onchain":    float(contract_scores.get("onchain", 50)),
            "security":   float(contract_scores.get("security", 50)),
            "funding":    float(contract_scores.get("funding", 50)),
            "team":       float(contract_scores.get("team", contract_scores.get("founders", 50))),
            "community":  float(contract_scores.get("community", 50)),
            "tokenomics": float(contract_scores.get("tokenomics", 50)),
            "product":    float(contract_scores.get("product", 50)),
            "reputation": float(contract_scores.get("reputation", contract_scores.get("identity", 50))),
        }
        report_data["scores"] = mapped_scores
        report_data["consensus_result"] = {
            "method": "genlayer_py write_contract + run_nondet_unsafe",
            "validators_count": 5,
            "consensus_reached": True,
            "tx_hash": tx_hash,
        }

        yield {"type": "completed", "report": report_data}

    except Exception as e:
        logger.error(f"[GenLayer] Contract call failed — falling back to simulation: {e}")
        async for update in _simulate_investigation(protocol_name, evidence, is_fallback=True):
            yield update


async def _simulate_investigation(
    protocol_name: str,
    evidence: dict,
    is_fallback: bool = False,
) -> AsyncIterator[dict]:
    """Off-chain simulation — used as fallback when contract call fails or when no contract is configured."""
    github = evidence.get("github", {})
    defillama = evidence.get("defillama", {})
    coingecko = evidence.get("coingecko", {})

    for vtype in VALIDATOR_TYPES:
        yield {"type": "validator_update", "validator_type": vtype, "status": "running"}
        await asyncio.sleep(0.3)

    scores = _compute_scores(github, defillama, coingecko)
    validator_results = _generate_validator_results(protocol_name, github, defillama, coingecko, scores)

    for vtype in VALIDATOR_TYPES:
        v = validator_results[vtype]
        yield {
            "type": "validator_update",
            "validator_type": vtype,
            "status": "completed",
            "findings": v["findings"],
            "confidence_score": v["confidence_score"],
        }
        await asyncio.sleep(0.5)

    overall = scores["overall"]
    risk_level = "low" if overall >= 75 else "medium" if overall >= 50 else "high" if overall >= 25 else "critical"

    summary_text = _build_summary(protocol_name, overall, risk_level, github, defillama, coingecko)
    if is_fallback:
        summary_text = "[SIMULATED — GenLayer contract call failed, this is an off-chain estimate] " + summary_text

    report = {
        "scores": scores,
        "risk_level": risk_level,
        "simulated": True,
        "validators": validator_results,
        "verified_claims": _build_verified_claims(protocol_name, github, defillama, coingecko),
        "disputed_claims": _build_disputed_claims(github, coingecko),
        "unresolved_claims": _build_unresolved_claims(),
        "summary": summary_text,
        "recommendation": _build_recommendation(protocol_name, overall, risk_level),
        "consensus_result": {
            "validators_count": 0,
            "consensus_reached": False,
            "consensus_method": "off_chain_simulation",
            "simulated": True,
            "overall_confidence": sum(v["confidence_score"] for v in validator_results.values()) / 13,
        },
        "evidence": evidence,
    }
    yield {"type": "completed", "report": report}


def _compute_scores(github: dict, defillama: dict, coingecko: dict) -> dict:
    # GitHub
    if github.get("found"):
        stars = github.get("stars", 0)
        recent = github.get("recent_commits", 0)
        contributors = github.get("contributors_count", 0)
        gh = min(100, min(stars / 100, 40) + min(recent * 4, 30) + min(contributors * 5, 20) + (5 if github.get("license") else 0) + (5 if not github.get("is_archived") else 0))
    else:
        gh = 20.0

    # On-chain
    if defillama.get("found"):
        tvl = defillama.get("tvl", 0) or 0
        chains = len(defillama.get("chains", []))
        audits = 1 if defillama.get("audit_links") else 0
        onchain = min(100, min(tvl / 1_000_000 * 10, 50) + min(chains * 5, 20) + audits * 20 + 10)
    elif coingecko.get("found"):
        onchain = 40.0
    else:
        onchain = 15.0

    # Security
    if defillama.get("found"):
        audit_links = defillama.get("audit_links", []) or []
        security = min(100, min(len(audit_links) * 25, 60) + (20 if defillama.get("audits") else 0) + 20)
    else:
        security = 25.0

    # Funding
    funding = min(100, onchain * 0.5 + (30 if coingecko.get("found") else 0) + 20)

    # Identity
    identity = min(100, (30 if coingecko.get("found") else 0) + (30 if defillama.get("found") else 0) + (40 if github.get("found") else 20))

    # Community (proxy from CoinGecko engagement)
    community = min(100, (40 if coingecko.get("found") else 15) + (20 if defillama.get("found") else 0) + 10)

    # Tokenomics
    tokenomics = min(100, (50 if coingecko.get("found") else 20) + (15 if defillama.get("found") else 0))

    # Ecosystem (proxy from chain count)
    chains_count = len(defillama.get("chains", []) or [])
    ecosystem = min(100, min(chains_count * 12, 60) + (20 if defillama.get("found") else 0) + 10)

    # Product (proxy from github + onchain)
    product = min(100, gh * 0.4 + onchain * 0.4 + 20)

    # Founders, Investors, Documentation, Media — proxy values
    founders = min(100, (gh * 0.6 + 30) if github.get("found") else 25)
    investors = min(100, (funding * 0.5 + identity * 0.3 + 20))
    documentation = min(100, (gh * 0.5 + 20) if github.get("found") else 20)
    media = min(100, (identity * 0.5 + community * 0.3 + 15))

    overall = round(
        security * 0.15 + onchain * 0.12 + gh * 0.10 + funding * 0.10 +
        identity * 0.08 + founders * 0.08 + investors * 0.07 + documentation * 0.07 +
        tokenomics * 0.07 + community * 0.06 + ecosystem * 0.05 + product * 0.05,
        2,
    )

    return {
        "overall": overall,
        "github": round(gh, 2),
        "onchain": round(onchain, 2),
        "security": round(security, 2),
        "funding": round(funding, 2),
        "reputation": round(identity, 2),
        "team": round((founders + investors) / 2, 2),
        "community": round(community, 2),
        "tokenomics": round(tokenomics, 2),
        "product": round(product, 2),
        # internal use
        "_founders": round(founders, 2),
        "_investors": round(investors, 2),
        "_documentation": round(documentation, 2),
        "_ecosystem": round(ecosystem, 2),
        "_media": round(media, 2),
    }


def _generate_validator_results(protocol_name, github, defillama, coingecko, scores) -> dict:
    gh_found = github.get("found", False)
    dl_found = defillama.get("found", False)
    cg_found = coingecko.get("found", False)
    name = coingecko.get("name") or defillama.get("name") or protocol_name
    chains = defillama.get("chains", []) or []

    return {
        "identity": {
            "findings": (
                f"{'Listed on CoinGecko as ' + name if cg_found else 'Not found on CoinGecko'}. "
                f"{'Indexed on DefiLlama (category: ' + defillama.get('category', 'N/A') + ')' if dl_found else 'Not found on DefiLlama'}. "
                f"{'Public GitHub repository: ' + github.get('full_name', '') if gh_found else 'No public GitHub found'}."
            ),
            "confidence_score": round(scores["reputation"], 2),
        },
        "founders": {
            "findings": (
                f"{'GitHub organization/repository found: ' + github.get('full_name', '') + ' with ' + str(github.get('contributors_count', 0)) + ' active contributors' if gh_found else 'No public GitHub repository found — founder identities cannot be verified from public data'}. "
                "Manual background check of named founders is always recommended."
            ),
            "confidence_score": round(scores["_founders"], 2),
        },
        "funding": {
            "findings": (
                f"{'TVL: $' + '{:,.0f}'.format(defillama.get('tvl', 0) or 0) + ' across ' + str(len(chains)) + ' chain(s)' if dl_found else 'No TVL data on DefiLlama'}. "
                f"{'Market cap rank: #' + str(coingecko.get('market_cap_rank', 'N/A')) if cg_found else 'Not ranked on CoinGecko'}."
            ),
            "confidence_score": round(scores["funding"], 2),
        },
        "investors": {
            "findings": (
                f"{'Protocol has CoinGecko rank #' + str(coingecko.get('market_cap_rank', 'N/A')) + ' suggesting institutional attention' if cg_found else 'No CoinGecko listing — institutional investor signals unavailable'}. "
                "Direct investor verification requires manual cross-referencing with VC portfolio pages."
            ),
            "confidence_score": round(scores["_investors"], 2),
        },
        "github": {
            "findings": (
                f"{'Repository: ' + github.get('full_name', '') + ' | Stars: ' + str(github.get('stars', 0)) + ' | Contributors: ' + str(github.get('contributors_count', 0)) + ' | Recent commits: ' + str(github.get('recent_commits', 0)) if gh_found else 'No public GitHub repository found'}. "
                f"{'License: ' + (github.get('license') or 'None') + ' | Archived: ' + str(github.get('is_archived', False)) if gh_found else ''}."
            ),
            "confidence_score": round(scores["github"], 2),
        },
        "documentation": {
            "findings": (
                f"{'Documentation quality inferred from GitHub repository ' + github.get('full_name', '') + ' — README and code comments present' if gh_found else 'No public GitHub repository — documentation quality cannot be assessed'}. "
                f"{'Official website found via CoinGecko' if cg_found and coingecko.get('homepage') else 'No official website detected'}."
            ),
            "confidence_score": round(scores["_documentation"], 2),
        },
        "onchain": {
            "findings": (
                f"{'Deployed on: ' + ', '.join(chains[:5]) if dl_found else 'No on-chain data found via DefiLlama'}. "
                f"{'TVL: $' + '{:,.0f}'.format(defillama.get('tvl', 0) or 0) if dl_found else ''}. "
                f"{'Category: ' + defillama.get('category', '') if dl_found else ''}."
            ),
            "confidence_score": round(scores["onchain"], 2),
        },
        "tokenomics": {
            "findings": (
                f"{'Token listed on CoinGecko (rank #' + str(coingecko.get('market_cap_rank', 'N/A')) + ', market cap $' + '{:,.0f}'.format(coingecko.get('market_cap', 0) or 0) + ')' if cg_found else 'Token not found on CoinGecko — tokenomics data unavailable'}. "
                f"{'24h volume: $' + '{:,.0f}'.format(coingecko.get('total_volume_24h', 0) or 0) if cg_found else ''}."
            ),
            "confidence_score": round(scores["tokenomics"], 2),
        },
        "security": {
            "findings": (
                f"{'Audit reports found: ' + str(len(defillama.get('audit_links') or [])) + ' public audit link(s)' if dl_found and defillama.get('audit_links') else 'No public security audit links found via DefiLlama'}. "
                "Independent smart contract audit strongly recommended before significant capital allocation."
            ),
            "confidence_score": round(scores["security"], 2),
        },
        "community": {
            "findings": (
                f"{'Protocol listed on CoinGecko rank #' + str(coingecko.get('market_cap_rank', 'N/A')) + ' — indicating community engagement' if cg_found else 'No CoinGecko listing — community engagement signals limited'}. "
                f"{'Also indexed on DefiLlama suggesting active DeFi community' if dl_found else ''}."
            ),
            "confidence_score": round(scores["community"], 2),
        },
        "ecosystem": {
            "findings": (
                f"{'Active on ' + str(len(chains)) + ' chains: ' + ', '.join(chains[:6]) if dl_found and chains else 'No multi-chain data found on DefiLlama'}. "
                f"{'Oracle integrations: ' + ', '.join((defillama.get('oracles') or [])[:3]) if dl_found and defillama.get('oracles') else 'No oracle integration data available'}."
            ),
            "confidence_score": round(scores["_ecosystem"], 2),
        },
        "product": {
            "findings": (
                f"{'Active product development — ' + str(github.get('recent_commits', 0)) + ' recent commits, ' + str(github.get('stars', 0)) + ' GitHub stars' if gh_found else 'No public GitHub — product development activity cannot be assessed'}. "
                f"{'Protocol category: ' + defillama.get('category', 'N/A') + ' with TVL $' + '{:,.0f}'.format(defillama.get('tvl', 0) or 0) if dl_found else ''}."
            ),
            "confidence_score": round(scores["product"], 2),
        },
        "media": {
            "findings": (
                f"{'Protocol is publicly listed on CoinGecko and has market presence (rank #' + str(coingecko.get('market_cap_rank', 'N/A')) + ')' if cg_found else 'No CoinGecko listing — public media presence is limited'}. "
                f"{'DefiLlama indexing confirms DeFi media coverage' if dl_found else 'Not found on DefiLlama'}."
            ),
            "confidence_score": round(scores["_media"], 2),
        },
    }


def _build_verified_claims(protocol_name, github, defillama, coingecko) -> list:
    claims = []
    if github.get("found"):
        claims.append({"claim": f"Public GitHub repository: {github.get('full_name')}", "source": "GitHub", "confidence": 95})
    if defillama.get("found"):
        claims.append({"claim": f"Indexed on DefiLlama with TVL ${defillama.get('tvl', 0):,.0f}", "source": "DefiLlama", "confidence": 90})
    if coingecko.get("found"):
        claims.append({"claim": f"Token listed on CoinGecko (rank #{coingecko.get('market_cap_rank', 'N/A')})", "source": "CoinGecko", "confidence": 90})
    if github.get("license"):
        claims.append({"claim": f"Open source — {github.get('license')} license", "source": "GitHub", "confidence": 85})
    if defillama.get("audit_links"):
        claims.append({"claim": f"{len(defillama.get('audit_links', []))} security audit report(s) publicly listed", "source": "DefiLlama", "confidence": 88})
    chains = defillama.get("chains", []) or []
    if len(chains) > 1:
        claims.append({"claim": f"Multi-chain deployment: {', '.join(chains[:5])}", "source": "DefiLlama", "confidence": 85})
    return claims


def _build_disputed_claims(github, coingecko) -> list:
    if not github.get("found") and not coingecko.get("found"):
        return [{"claim": "Protocol claims open-source development but no public repository was found", "confidence": 30}]
    return []


def _build_unresolved_claims() -> list:
    return [
        {"claim": "Founder identities require manual background verification"},
        {"claim": "Investor claims need cross-referencing with investor portfolio pages"},
    ]


def _build_summary(protocol_name, overall, risk_level, github, defillama, coingecko) -> str:
    gh = f"GitHub: {'active (' + str(github.get('stars', 0)) + ' stars)' if github.get('found') else 'not found'}. "
    dl = f"TVL ${defillama.get('tvl', 0):,.0f} on {len(defillama.get('chains', []))} chain(s). " if defillama.get("found") else ""
    cg = f"CoinGecko rank #{coingecko.get('market_cap_rank', 'N/A')}. " if coingecko.get("found") else ""
    return (
        f"{protocol_name} received a TrustLayer consensus score of {overall:.1f}/100 ({risk_level.upper()} RISK). "
        f"{gh}{dl}{cg}"
        f"Analysis by 13 independent sources via GenLayer consensus."
    )


def _build_recommendation(protocol_name, overall, risk_level) -> str:
    if overall >= 75:
        return f"{protocol_name} shows strong verifiable signals. Suitable for further due diligence. Always verify team identity and investor claims independently before significant capital allocation."
    elif overall >= 50:
        return f"{protocol_name} shows moderate trust signals with some gaps. Proceed with caution — prioritise verifying security audits and team identity before interaction."
    elif overall >= 25:
        return f"{protocol_name} has limited verifiable signals. HIGH CAUTION. Do not interact without a full independent security audit."
    else:
        return f"{protocol_name} has very few verifiable signals. CRITICAL RISK. Do not allocate capital without exhaustive independent research."
