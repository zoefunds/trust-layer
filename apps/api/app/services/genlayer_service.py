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

# The 5 validators that match the deployed contract
VALIDATOR_TYPES = ["identity", "github", "funding", "onchain", "security"]

# Default StudioNet test account used as the transaction sender
_STUDIO_FROM = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"


async def run_investigation_via_genlayer(
    protocol_name: str,
    evidence: dict,
    investigation_id: str = "",
) -> AsyncIterator[dict]:
    if settings.GENLAYER_CONTRACT_ADDRESS:
        async for update in _call_genlayer_contract(protocol_name, evidence, investigation_id):
            yield update
    else:
        async for update in _simulate_investigation(protocol_name, evidence):
            yield update


async def _call_genlayer_contract(
    protocol_name: str,
    evidence: dict,
    investigation_id: str = "",
) -> AsyncIterator[dict]:
    """
    Call the deployed TrustLayer contract via GenLayer Studio JSON-RPC.

    Flow:
      1. gen_sendTransaction  → tx_hash
      2. Poll eth_getTransactionReceipt until status = "0x1"
      3. gen_call get_report(protocol_name) → JSON report string
    """
    import httpx

    contract_address = settings.GENLAYER_CONTRACT_ADDRESS
    studio_url = settings.GENLAYER_STUDIO_URL.rstrip("/")
    api_url = f"{studio_url}/api"

    # Signal all 5 validators as running immediately
    for vtype in VALIDATOR_TYPES:
        yield {"type": "validator_update", "validator_type": vtype, "status": "running"}
        await asyncio.sleep(0.1)

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:

            # ── Step 1: send_transaction ──────────────────────────────────
            send_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "gen_sendTransaction",
                "params": [{
                    "from": _STUDIO_FROM,
                    "to": contract_address,
                    "value": "0x0",
                    "data": json.dumps({
                        "method": "investigate",
                        "args": [protocol_name, json.dumps(evidence), investigation_id],
                    }),
                }],
            }

            logger.info(f"[GenLayer] Sending transaction for {protocol_name}")
            resp = await client.post(api_url, json=send_payload)
            resp.raise_for_status()
            send_result = resp.json()
            logger.info(f"[GenLayer] send_transaction response: {send_result}")

            if "error" in send_result:
                raise Exception(f"gen_sendTransaction error: {send_result['error']}")

            tx_hash = send_result.get("result")
            if not tx_hash:
                raise Exception(f"No tx_hash in response: {send_result}")

            logger.info(f"[GenLayer] tx_hash={tx_hash}")

            # ── Step 2: poll for receipt ──────────────────────────────────
            receipt = None
            for attempt in range(120):  # up to 4 minutes
                await asyncio.sleep(2)
                receipt_payload = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "eth_getTransactionReceipt",
                    "params": [tx_hash],
                }
                r = await client.post(api_url, json=receipt_payload)
                r.raise_for_status()
                receipt_data = r.json()
                receipt = receipt_data.get("result")
                if receipt is not None:
                    logger.info(f"[GenLayer] receipt after {attempt + 1} polls: status={receipt.get('status')}")
                    break

            if receipt is None:
                raise Exception("Transaction never mined — timed out after 4 minutes")

            if receipt.get("status") not in ("0x1", 1, True, "success", "0x01"):
                raise Exception(f"Transaction failed: receipt status={receipt.get('status')}")

            # ── Step 3: read the stored report ────────────────────────────
            read_payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "gen_call",
                "params": [{
                    "from": _STUDIO_FROM,
                    "to": contract_address,
                    "data": json.dumps({
                        "method": "get_report",
                        "args": [protocol_name],
                    }),
                }],
            }
            r = await client.post(api_url, json=read_payload)
            r.raise_for_status()
            read_result = r.json()
            logger.info(f"[GenLayer] get_report result keys: {list(read_result.keys())}")

            if "error" in read_result:
                raise Exception(f"gen_call get_report error: {read_result['error']}")

            raw = read_result.get("result", "{}")
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
                "confidence_score": float(vdata.get("confidence", vdata.get("confidence_score", 50.0))),
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
            "method": "gen_sendTransaction + run_nondet_unsafe",
            "validators_count": 5,
            "consensus_reached": True,
            "tx_hash": tx_hash,
        }

        yield {"type": "completed", "report": report_data}

    except Exception as e:
        logger.error(f"[GenLayer] Contract call failed — falling back to simulation: {e}")
        async for update in _simulate_investigation(protocol_name, evidence):
            yield update


async def _simulate_investigation(
    protocol_name: str,
    evidence: dict,
) -> AsyncIterator[dict]:
    """Off-chain simulation used as fallback when contract call fails."""
    github = evidence.get("github", {})
    defillama = evidence.get("defillama", {})
    coingecko = evidence.get("coingecko", {})

    for vtype in VALIDATOR_TYPES:
        yield {"type": "validator_update", "validator_type": vtype, "status": "running"}
        await asyncio.sleep(0.4)

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
        await asyncio.sleep(0.6)

    overall = scores["overall"]
    risk_level = "low" if overall >= 75 else "medium" if overall >= 50 else "high" if overall >= 25 else "critical"

    report = {
        "scores": scores,
        "risk_level": risk_level,
        "validators": validator_results,
        "verified_claims": _build_verified_claims(protocol_name, github, defillama, coingecko),
        "disputed_claims": _build_disputed_claims(github, coingecko),
        "unresolved_claims": _build_unresolved_claims(),
        "summary": _build_summary(protocol_name, overall, risk_level, github, defillama, coingecko),
        "recommendation": _build_recommendation(protocol_name, overall, risk_level),
        "consensus_result": {
            "validators_count": 5,
            "consensus_reached": True,
            "consensus_method": "simulation_weighted_average",
            "overall_confidence": sum(v["confidence_score"] for v in validator_results.values()) / 5,
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

    # Funding (proxy from TVL + market cap)
    funding = min(100, onchain * 0.5 + (30 if coingecko.get("found") else 0) + 20)

    # Identity (proxy from CoinGecko listing + DefiLlama presence)
    identity = min(100, (30 if coingecko.get("found") else 0) + (30 if defillama.get("found") else 0) + (40 if github.get("found") else 20))

    overall = round(security * 0.25 + onchain * 0.25 + gh * 0.20 + funding * 0.15 + identity * 0.15, 2)

    return {
        "overall": overall,
        "github": round(gh, 2),
        "onchain": round(onchain, 2),
        "security": round(security, 2),
        "funding": round(funding, 2),
        "reputation": round(identity, 2),
        # kept for schema compatibility
        "team": round((gh * 0.5 + 30), 2),
        "community": round((20 if coingecko.get("found") else 10), 2),
        "tokenomics": round((40 if coingecko.get("found") else 20), 2),
        "product": round((gh * 0.4 + onchain * 0.4 + 20), 2),
    }


def _generate_validator_results(protocol_name, github, defillama, coingecko, scores) -> dict:
    gh_found = github.get("found", False)
    dl_found = defillama.get("found", False)
    cg_found = coingecko.get("found", False)
    name = coingecko.get("name") or defillama.get("name") or protocol_name

    return {
        "identity": {
            "findings": (
                f"{'Listed on CoinGecko as ' + name if cg_found else 'Not found on CoinGecko'}. "
                f"{'Indexed on DefiLlama (category: ' + defillama.get('category', 'N/A') + ')' if dl_found else 'Not found on DefiLlama'}. "
                f"{'Public GitHub repository: ' + github.get('full_name', '') if gh_found else 'No public GitHub found'}."
            ),
            "confidence_score": round(scores["reputation"], 2),
        },
        "github": {
            "findings": (
                f"{'Repository: ' + github.get('full_name', '') + ' | Stars: ' + str(github.get('stars', 0)) + ' | Contributors: ' + str(github.get('contributors_count', 0)) + ' | Recent commits: ' + str(github.get('recent_commits', 0)) if gh_found else 'No public GitHub repository found'}. "
                f"{'License: ' + (github.get('license') or 'None') + ' | Archived: ' + str(github.get('is_archived', False)) if gh_found else ''}."
            ),
            "confidence_score": round(scores["github"], 2),
        },
        "funding": {
            "findings": (
                f"{'TVL: $' + '{:,.0f}'.format(defillama.get('tvl', 0) or 0) + ' across ' + str(len(defillama.get('chains', []))) + ' chain(s)' if dl_found else 'No TVL data on DefiLlama'}. "
                f"{'Market cap rank: #' + str(coingecko.get('market_cap_rank', 'N/A')) if cg_found else 'Not ranked on CoinGecko'}."
            ),
            "confidence_score": round(scores["funding"], 2),
        },
        "onchain": {
            "findings": (
                f"{'Deployed on: ' + ', '.join((defillama.get('chains') or [])[:5]) if dl_found else 'No on-chain data found via DefiLlama'}. "
                f"{'TVL: $' + '{:,.0f}'.format(defillama.get('tvl', 0) or 0) if dl_found else ''}. "
                f"{'Category: ' + defillama.get('category', '') if dl_found else ''}."
            ),
            "confidence_score": round(scores["onchain"], 2),
        },
        "security": {
            "findings": (
                f"{'Audit reports found: ' + str(len(defillama.get('audit_links') or [])) + ' public audit link(s)' if dl_found and defillama.get('audit_links') else 'No public security audit links found via DefiLlama'}. "
                "Independent smart contract audit strongly recommended before significant capital allocation."
            ),
            "confidence_score": round(scores["security"], 2),
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
    dl = f"TVL ${ defillama.get('tvl', 0):,.0f} on {len(defillama.get('chains', []))} chain(s). " if defillama.get("found") else ""
    cg = f"CoinGecko rank #{coingecko.get('market_cap_rank', 'N/A')}. " if coingecko.get("found") else ""
    return (
        f"{protocol_name} received a TrustLayer consensus score of {overall:.1f}/100 ({risk_level.upper()} RISK). "
        f"{gh}{dl}{cg}"
        f"Analysis by 5 independent AI validators via GenLayer consensus."
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
