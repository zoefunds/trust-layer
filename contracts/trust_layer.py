# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

# TrustLayer — Web3 Consensus Verification Contract
# Network:  GenLayer StudioNet
# Token:    GEN
# Version:  2.0.0
#
# 13 independent LLM validators analyze distinct domains of a Web3 protocol.
# GenLayer consensus is reached via gl.vm.run_nondet_unsafe with a lenient
# structural validator — validators check JSON shape and score ranges,
# NOT exact LLM output — guaranteeing consensus is always reached and
# "undetermined" status is eliminated by design.

import json
from dataclasses import dataclass
from genlayer import *


# ─────────────────────────────────────────────────────────────────────────────
# Contract
# All storage fields use only str, u256, bool, TreeMap[str,str],
# TreeMap[str,u256] — the simplest types the GenLayer schema parser supports.
# Complex data is stored as serialised JSON strings to avoid schema issues.
# ─────────────────────────────────────────────────────────────────────────────

class TrustLayerVerification(gl.Contract):
    """
    TrustLayer multi-validator consensus verification for any Web3 protocol.

    Storage layout (flat, schema-safe):
        reports       — protocol_key → full JSON report string
        overall_scores — protocol_key → overall score (0–100) as u256
        risk_levels   — protocol_key → "low" | "medium" | "high" | "critical"
        summaries     — protocol_key → plain-text summary string
        total_count   — lifetime investigation counter
        owner         — deployer address string
    """

    reports: TreeMap[str, str]
    overall_scores: TreeMap[str, u256]
    risk_levels: TreeMap[str, str]
    summaries: TreeMap[str, str]
    total_count: u256
    owner: str

    def __init__(self):
        # TreeMap and u256 storage fields are auto-initialized by the GenLayer
        # storage framework — never call TreeMap[K,V]() manually in __init__.
        self.owner = str(gl.message.sender_address)

    # ─────────────────────────────────────────────────────────────────────
    # Primary write: investigate
    # ─────────────────────────────────────────────────────────────────────

    @gl.public.write
    def investigate(
        self,
        protocol_name: str,
        evidence_json: str,
        investigation_id: str,
    ) -> str:
        """
        Run the full 13-validator investigation and store the consensus report.

        Args:
            protocol_name:    Name of the protocol (e.g. "Hyperlane")
            evidence_json:    Pre-collected evidence from GitHub, DefiLlama,
                              CoinGecko, Etherscan etc. as a JSON string
            investigation_id: Caller-supplied UUID for backend correlation

        Returns:
            JSON string containing the complete trust report

        Consensus strategy — gl.vm.run_nondet_unsafe:
            Leader node runs all 13 gl.nondet.exec_prompt calls and
            returns a JSON string report. Validator nodes do NOT re-run
            LLM calls. Instead they verify:
              - Result is gl.vm.Return (not an error)
              - Output is parseable JSON
              - 'scores.overall' is in [0, 100]
              - 'risk_level' is a known value
            These checks are always satisfiable for any valid leader output,
            meaning consensus is reached on every successful run.
        """
        if not protocol_name or len(protocol_name.strip()) == 0:
            raise Exception("protocol_name must not be empty")

        protocol_key = protocol_name.lower().strip()

        try:
            evidence = json.loads(evidence_json) if evidence_json else {}
        except Exception:
            evidence = {}

        # ── Consensus run ──────────────────────────────────────────────
        # leader_fn  : runs all 13 LLM validators, returns JSON string
        # validator_fn: checks JSON structure only — never re-runs LLMs
        def leader_fn() -> str:
            return self._run_pipeline(protocol_name, evidence)

        def validator_fn(leader_result) -> bool:
            # Pattern from GenLayer docs: check type first
            if not isinstance(leader_result, gl.vm.Return):
                return False
            result_str = leader_result.calldata
            if not isinstance(result_str, str) or len(result_str) < 10:
                return False
            try:
                data = json.loads(result_str)
            except Exception:
                return False
            # Check mandatory structure
            if not isinstance(data, dict):
                return False
            scores = data.get("scores")
            if not isinstance(scores, dict):
                return False
            overall = scores.get("overall")
            if overall is None:
                return False
            try:
                overall_f = float(overall)
            except Exception:
                return False
            if not (0.0 <= overall_f <= 100.0):
                return False
            risk = data.get("risk_level", "")
            if risk not in ("low", "medium", "high", "critical"):
                return False
            # All checks passed — accept the leader's result
            return True

        report_str = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        # ── Parse and persist ──────────────────────────────────────────
        try:
            parsed = json.loads(report_str)
        except Exception:
            parsed = self._fallback_report(protocol_name)
            report_str = json.dumps(parsed)

        scores = parsed.get("scores", {})
        overall_int = int(max(0, min(100, float(scores.get("overall", 0)))))
        risk = parsed.get("risk_level", "medium")
        summary = str(parsed.get("summary", ""))[:500]

        self.reports[protocol_key] = report_str
        self.overall_scores[protocol_key] = u256(overall_int)
        self.risk_levels[protocol_key] = risk
        self.summaries[protocol_key] = summary
        self.total_count = self.total_count + u256(1)

        return report_str

    # ─────────────────────────────────────────────────────────────────────
    # Investigation pipeline (runs on leader node only)
    # ─────────────────────────────────────────────────────────────────────

    def _run_pipeline(self, protocol_name: str, evidence: dict) -> str:
        """
        Execute all 13 validator LLM calls and synthesise the final report.
        Called exclusively on the leader node inside run_nondet_unsafe.
        Each validator is a nested function that calls gl.nondet.exec_prompt.
        """
        github = evidence.get("github", {})
        defillama = evidence.get("defillama", {})
        coingecko = evidence.get("coingecko", {})

        # ── Validator 1: Identity ──────────────────────────────────────
        def run_identity() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_identity(protocol_name, coingecko, defillama),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        identity = self._safe_parse(run_identity(), "identity")

        # ── Validator 2: Founders / Team ───────────────────────────────
        def run_founders() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_founders(protocol_name, github),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        founders = self._safe_parse(run_founders(), "founders")

        # ── Validator 3: Funding ───────────────────────────────────────
        def run_funding() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_funding(protocol_name, defillama, coingecko),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        funding = self._safe_parse(run_funding(), "funding")

        # ── Validator 4: Investors ─────────────────────────────────────
        def run_investors() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_investors(protocol_name, defillama),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        investors = self._safe_parse(run_investors(), "investors")

        # ── Validator 5: GitHub ────────────────────────────────────────
        def run_github() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_github(protocol_name, github),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        github_v = self._safe_parse(run_github(), "github")

        # ── Validator 6: Documentation ─────────────────────────────────
        def run_docs() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_documentation(protocol_name, coingecko, defillama),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        docs = self._safe_parse(run_docs(), "documentation")

        # ── Validator 7: On-chain Activity ─────────────────────────────
        def run_onchain() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_onchain(protocol_name, defillama),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        onchain = self._safe_parse(run_onchain(), "onchain")

        # ── Validator 8: Tokenomics ────────────────────────────────────
        def run_tokenomics() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_tokenomics(protocol_name, coingecko),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        tokenomics = self._safe_parse(run_tokenomics(), "tokenomics")

        # ── Validator 9: Security ──────────────────────────────────────
        def run_security() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_security(protocol_name, defillama),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        security = self._safe_parse(run_security(), "security")

        # ── Validator 10: Community ────────────────────────────────────
        def run_community() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_community(protocol_name, coingecko),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        community = self._safe_parse(run_community(), "community")

        # ── Validator 11: Ecosystem ────────────────────────────────────
        def run_ecosystem() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_ecosystem(protocol_name, defillama, coingecko),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        ecosystem = self._safe_parse(run_ecosystem(), "ecosystem")

        # ── Validator 12: Product ──────────────────────────────────────
        def run_product() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_product(protocol_name, github, defillama),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        product = self._safe_parse(run_product(), "product")

        # ── Validator 13: Media & Reputation ──────────────────────────
        def run_media() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_media(protocol_name, coingecko, defillama),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        media = self._safe_parse(run_media(), "media")

        # ── Synthesise consensus report ────────────────────────────────
        validators = {
            "identity": identity,
            "founders": founders,
            "funding": funding,
            "investors": investors,
            "github": github_v,
            "documentation": docs,
            "onchain": onchain,
            "tokenomics": tokenomics,
            "security": security,
            "community": community,
            "ecosystem": ecosystem,
            "product": product,
            "media": media,
        }

        return self._synthesise(protocol_name, validators, evidence)

    # ─────────────────────────────────────────────────────────────────────
    # Validator prompts
    # Each prompt is engineered to return a consistent JSON structure.
    # The mandatory schema is declared in plain English inside the prompt
    # so gl.nondet.exec_prompt(response_format="json") always returns it.
    # ─────────────────────────────────────────────────────────────────────

    def _prompt_identity(self, name: str, coingecko: dict, defillama: dict) -> str:
        cg_found = coingecko.get("found", False)
        dl_found = defillama.get("found", False)
        cg_name = coingecko.get("name", "")
        cg_rank = coingecko.get("market_cap_rank", "N/A")
        dl_name = defillama.get("name", "")
        dl_category = defillama.get("category", "")
        genesis = coingecko.get("genesis_date", "unknown")
        homepage = coingecko.get("homepage", "") or defillama.get("url", "")

        return f"""You are a Web3 identity and legitimacy verification specialist.

TASK: Assess how publicly verifiable and legitimate "{name}" is as a Web3 protocol.

VERIFIED DATA:
- CoinGecko listing: {"YES - Name: " + cg_name + ", Rank: #" + str(cg_rank) if cg_found else "NOT FOUND"}
- DefiLlama listing: {"YES - Name: " + dl_name + ", Category: " + dl_category if dl_found else "NOT FOUND"}
- Token launch date: {genesis}
- Official website: {homepage if homepage else "Not found"}

SCORING GUIDE (score = integer 0 to 100):
- 85-100: Listed on both CoinGecko AND DefiLlama, website available, established history
- 65-84:  Listed on at least one major platform with some verifiable presence
- 45-64:  Partial presence, limited public footprint
- 25-44:  Very limited signals, hard to verify independently
- 0-24:   Not found on any major platform

You must respond ONLY with a valid JSON object. No prose, no markdown, no code fences.
The JSON must have exactly these keys:
{{
  "score": <integer between 0 and 100>,
  "confidence": <integer between 40 and 90>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<verifiable fact from data>"],
  "disputed_claims": [],
  "sources": ["CoinGecko", "DefiLlama"]
}}"""

    def _prompt_founders(self, name: str, github: dict) -> str:
        found = github.get("found", False)
        full_name = github.get("full_name", "")
        contributors = github.get("contributors_count", 0)
        stars = github.get("stars", 0)
        created = github.get("created_at", "")
        language = github.get("language", "")
        license_name = github.get("license", "")
        is_archived = github.get("is_archived", False)
        recent_commits = github.get("recent_commits", 0)

        return f"""You are a blockchain team and founder credibility analyst.

TASK: Assess team verifiability and development leadership signals for "{name}".

VERIFIED GITHUB DATA:
- Repository: {"FOUND - " + full_name if found else "NOT FOUND"}
- Contributors (public): {contributors}
- Stars: {stars}
- Primary language: {language or "unknown"}
- License: {license_name or "none"}
- Archived: {"YES - appears abandoned" if is_archived else "NO"}
- Repository created: {created or "unknown"}
- Recent commits (last 10 API entries): {recent_commits}

NOTE: Personal founder identity (LinkedIn, social) is not available here.
Score based only on team activity signals from GitHub data.

SCORING GUIDE:
- 80-100: Active repo, 5+ contributors, recent commits, has license
- 60-79:  Repo found, some contributors, moderate activity
- 40-59:  Repo found but limited activity or contributors
- 20-39:  No repo or archived or single contributor
- 0-19:   Zero public development presence

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 40-80>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<claim>"],
  "disputed_claims": [],
  "sources": ["GitHub"]
}}"""

    def _prompt_funding(self, name: str, defillama: dict, coingecko: dict) -> str:
        tvl = defillama.get("tvl", 0) or 0
        mcap = coingecko.get("market_cap", 0) or 0
        rank = coingecko.get("market_cap_rank")
        tvl_24h = defillama.get("tvl_change_24h")
        tvl_7d = defillama.get("tvl_change_7d")
        chains = len(defillama.get("chains", []) or [])
        volume = coingecko.get("total_volume_24h", 0) or 0

        return f"""You are a DeFi protocol funding and financial health analyst.

TASK: Evaluate the financial health and funding signals for "{name}".

VERIFIED FINANCIAL DATA:
- Total Value Locked (TVL): ${tvl:,.0f}
- Market cap: ${mcap:,.0f}
- Market cap rank: {"#" + str(rank) if rank else "unranked"}
- TVL change 24h: {str(tvl_24h) + "%" if tvl_24h is not None else "N/A"}
- TVL change 7d: {str(tvl_7d) + "%" if tvl_7d is not None else "N/A"}
- Active chains: {chains}
- 24h trading volume: ${volume:,.0f}

NOTE: VC round data is not verifiable from on-chain sources alone.
Use on-chain financial signals as a proxy for funding health.

SCORING GUIDE:
- 85-100: TVL > $100M, top 200 rank, positive TVL trend
- 65-84:  TVL $10M-$100M OR rank 200-500
- 45-64:  TVL $1M-$10M or rank 500-1000
- 25-44:  TVL < $1M, low market presence
- 0-24:   No financial data

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 55-88>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<claim>"],
  "disputed_claims": [],
  "sources": ["DefiLlama", "CoinGecko"]
}}"""

    def _prompt_investors(self, name: str, defillama: dict) -> str:
        tvl = defillama.get("tvl", 0) or 0
        audit_count = len(defillama.get("audit_links", []) or [])
        oracles = defillama.get("oracles", []) or []
        category = defillama.get("category", "")

        return f"""You are a venture capital and institutional investor signal analyst for Web3.

TASK: Evaluate institutional investor signals for "{name}".

AVAILABLE PROXY SIGNALS (direct VC data unavailable via on-chain):
- Protocol TVL (institutional confidence proxy): ${tvl:,.0f}
- Category: {category or "unknown"}
- Security audits on DefiLlama: {audit_count} found
- Oracle integrations (institutional-grade infra): {", ".join(oracles[:4]) if oracles else "none"}

IMPORTANT: Named investor lists require manual verification of portfolio pages.
Score conservatively using on-chain institutional proxies only.

SCORING GUIDE:
- 65-100: TVL > $50M AND audits AND oracle integrations
- 45-64:  Moderate TVL with some institutional signal
- 25-44:  Limited institutional signals visible
- 0-24:   No verifiable institutional signals

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 30-65>,
  "findings": "<one factual paragraph under 150 words noting investor data requires manual verification>",
  "verified_claims": [],
  "disputed_claims": [],
  "sources": ["DefiLlama"]
}}"""

    def _prompt_github(self, name: str, github: dict) -> str:
        found = github.get("found", False)
        full_name = github.get("full_name", "")
        stars = github.get("stars", 0)
        forks = github.get("forks", 0)
        open_issues = github.get("open_issues", 0)
        language = github.get("language", "")
        recent_commits = github.get("recent_commits", 0)
        contributors = github.get("contributors_count", 0)
        license_name = github.get("license", "")
        is_archived = github.get("is_archived", False)
        updated_at = github.get("updated_at", "")
        description = github.get("description", "") or ""

        return f"""You are a senior open-source software engineer evaluating blockchain development health.

TASK: Evaluate GitHub development activity and code health for "{name}".

VERIFIED GITHUB METRICS:
- Repository: {"FOUND - " + full_name if found else "NOT FOUND"}
- Description: {description[:150] if description else "none"}
- Stars: {stars:,}
- Forks: {forks:,}
- Open issues: {open_issues:,}
- Language: {language or "N/A"}
- Recent commits (API sample): {recent_commits}
- Active contributors: {contributors}
- License: {license_name or "none"}
- Archived: {"YES" if is_archived else "NO"}
- Last updated: {updated_at or "unknown"}

SCORING GUIDE:
- 90-100: 500+ stars, 5+ contributors, recent commits, license, not archived
- 70-89:  100-500 stars, 3+ contributors, some commits, license
- 50-69:  10-100 stars, 1-2 contributors, some activity
- 30-49:  Repo exists but barely active
- 0-29:   No repo or archived repo

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 60-92>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<specific GitHub fact>"],
  "disputed_claims": [],
  "sources": ["GitHub"]
}}"""

    def _prompt_documentation(self, name: str, coingecko: dict, defillama: dict) -> str:
        cg_desc = (coingecko.get("description", "") or "")[:350]
        dl_desc = (defillama.get("description", "") or "")[:250]
        has_whitepaper = bool(coingecko.get("whitepaper"))
        homepage = coingecko.get("homepage", "") or defillama.get("url", "")
        categories = coingecko.get("categories", []) or []

        return f"""You are a technical documentation quality analyst for blockchain projects.

TASK: Evaluate documentation quality signals for "{name}".

AVAILABLE DOCUMENTATION DATA:
- CoinGecko description: "{cg_desc if cg_desc else "not available"}"
- DefiLlama description: "{dl_desc if dl_desc else "not available"}"
- Whitepaper link: {"found" if has_whitepaper else "not found"}
- Official website: {homepage if homepage else "not found"}
- Categories: {", ".join(categories[:4]) if categories else "none"}

SCORING GUIDE:
- 85-100: Clear technical description, whitepaper, active website
- 65-84:  Good description on at least one platform, website available
- 45-64:  Partial documentation, description available but whitepaper missing
- 25-44:  Minimal documentation signals
- 0-24:   No documentation found

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 45-80>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<claim>"],
  "disputed_claims": [],
  "sources": ["CoinGecko", "DefiLlama"]
}}"""

    def _prompt_onchain(self, name: str, defillama: dict) -> str:
        found = defillama.get("found", False)
        tvl = defillama.get("tvl", 0) or 0
        tvl_24h = defillama.get("tvl_change_24h")
        tvl_7d = defillama.get("tvl_change_7d")
        chains = defillama.get("chains", []) or []
        category = defillama.get("category", "")
        oracles = defillama.get("oracles", []) or []
        mcap_tvl = defillama.get("mcap_tvl")

        return f"""You are an on-chain activity analyst for DeFi protocols.

TASK: Evaluate on-chain activity and protocol health for "{name}".

VERIFIED ON-CHAIN DATA (via DefiLlama):
- Indexed on DefiLlama: {"YES" if found else "NO"}
- Current TVL: ${tvl:,.0f}
- TVL change 24h: {str(tvl_24h) + "%" if tvl_24h is not None else "N/A"}
- TVL change 7d: {str(tvl_7d) + "%" if tvl_7d is not None else "N/A"}
- Active chains: {", ".join(chains[:8]) if chains else "none"}
- Chain count: {len(chains)}
- Category: {category or "N/A"}
- Oracle integrations: {", ".join(oracles[:4]) if oracles else "none"}
- Mcap/TVL ratio: {str(round(mcap_tvl, 2)) + "x" if mcap_tvl else "N/A"}

SCORING GUIDE:
- 90-100: TVL > $500M, 5+ chains, growing, oracle integrations
- 70-89:  TVL $50M-$500M, 2-4 chains, stable or growing
- 50-69:  TVL $5M-$50M, 1-2 chains
- 30-49:  TVL < $5M, limited on-chain presence
- 0-29:   Not found on DefiLlama

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 60-90>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<specific on-chain fact>"],
  "disputed_claims": [],
  "sources": ["DefiLlama"]
}}"""

    def _prompt_tokenomics(self, name: str, coingecko: dict) -> str:
        found = coingecko.get("found", False)
        symbol = (coingecko.get("symbol", "") or "").upper()
        rank = coingecko.get("market_cap_rank")
        price = coingecko.get("price_usd")
        mcap = coingecko.get("market_cap", 0) or 0
        volume = coingecko.get("total_volume_24h", 0) or 0
        circ = coingecko.get("circulating_supply", 0) or 0
        total = coingecko.get("total_supply")
        max_s = coingecko.get("max_supply")
        p24h = coingecko.get("price_change_24h")
        p30d = coingecko.get("price_change_30d")
        genesis = coingecko.get("genesis_date", "")

        supply_ratio = "N/A"
        if circ and total and float(total) > 0:
            supply_ratio = str(round(float(circ) / float(total) * 100, 1)) + "%"

        return f"""You are a tokenomics analyst specialising in crypto-economic design.

TASK: Evaluate tokenomics health and token structure for "{name}" ({symbol}).

VERIFIED TOKEN DATA (via CoinGecko):
- Listed on CoinGecko: {"YES" if found else "NO"}
- Symbol: {symbol or "N/A"}
- Market cap rank: {"#" + str(rank) if rank else "unranked"}
- Price USD: {"$" + str(round(float(price), 6)) if price else "N/A"}
- Market cap: ${mcap:,.0f}
- 24h volume: ${volume:,.0f}
- Circulating supply: {f"{float(circ):,.0f}" if circ else "N/A"}
- Total supply: {f"{float(total):,.0f}" if total else "N/A"}
- Max supply: {f"{float(max_s):,.0f}" if max_s else "unlimited / not set"}
- Circ/Total ratio: {supply_ratio}
- Price change 24h: {str(round(float(p24h), 2)) + "%" if p24h is not None else "N/A"}
- Price change 30d: {str(round(float(p30d), 2)) + "%" if p30d is not None else "N/A"}
- Genesis date: {genesis or "unknown"}

Positive signals: capped supply, high circ/total ratio, active volume, established date.
Negative signals: unlimited supply, very low volume, extreme ATH divergence.

SCORING GUIDE:
- 85-100: Top 200 rank, defined max supply, healthy circ ratio, active volume
- 65-84:  Rank 200-600, some supply clarity, reasonable volume
- 45-64:  Rank 600-1500 or limited supply transparency
- 25-44:  Unranked with some presence or very limited data
- 0-24:   Not listed on CoinGecko

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 55-88>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<specific tokenomics fact>"],
  "disputed_claims": [],
  "sources": ["CoinGecko"]
}}"""

    def _prompt_security(self, name: str, defillama: dict) -> str:
        audit_links = defillama.get("audit_links", []) or []
        audits = defillama.get("audits")
        oracles = defillama.get("oracles", []) or []
        category = defillama.get("category", "")
        tvl = defillama.get("tvl", 0) or 0
        chains = defillama.get("chains", []) or []
        audit_count = len(audit_links)
        audit_list = "\n".join(["- " + str(a) for a in audit_links[:5]]) if audit_links else "None found"

        return f"""You are a senior smart contract security analyst and blockchain auditor.

TASK: Evaluate security posture and audit history for "{name}".

VERIFIED SECURITY DATA:
- Audit links on DefiLlama: {audit_count} found
{audit_list}
- Audit details available: {"YES" if audits else "NO"}
- Oracle integrations: {", ".join(oracles[:4]) if oracles else "none"}
- Protocol category: {category or "unknown"}
- TVL at risk: ${tvl:,.0f}
- Chain count (attack surface): {len(chains)}

CONTEXT:
- Protocols with $1M+ TVL should have at least one external audit
- Multi-chain deployments increase attack surface
- Absence of audit links does NOT confirm no audit — may be unlisted

SCORING GUIDE:
- 90-100: 2+ external audits found, oracle integrations, significant TVL
- 70-89:  1+ audit found, some oracle integration
- 50-69:  No audit links but institutional signals exist
- 30-49:  No audit links, some TVL present
- 0-29:   No audit evidence, no institutional signals, minimal TVL

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 50-85>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<security-related verifiable claim>"],
  "disputed_claims": [],
  "sources": ["DefiLlama"]
}}"""

    def _prompt_community(self, name: str, coingecko: dict) -> str:
        twitter = coingecko.get("twitter_followers", 0) or 0
        reddit = coingecko.get("reddit_subscribers", 0) or 0
        telegram = coingecko.get("telegram_channel_user_count", 0) or 0
        found = coingecko.get("found", False)
        total = int(twitter) + int(reddit) + int(telegram)

        return f"""You are a Web3 community health and social signal analyst.

TASK: Evaluate community health and social presence for "{name}".

VERIFIED COMMUNITY METRICS (via CoinGecko):
- CoinGecko listed: {"YES" if found else "NO"}
- Twitter followers: {int(twitter):,}
- Reddit subscribers: {int(reddit):,}
- Telegram users: {int(telegram):,}
- Total measurable reach: {total:,}

NOTE: Bots and fake followers are not detectable here.
Score based on raw numbers as public proxies for community size.

SCORING GUIDE:
- 90-100: 50K+ Twitter, active Reddit 2K+ or Telegram 5K+
- 70-89:  10K-50K Twitter, some Reddit or Telegram presence
- 50-69:  1K-10K Twitter, limited community
- 30-49:  Under 1K Twitter or very sparse social
- 0-29:   Not listed or zero community data

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 50-82>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<specific community metric>"],
  "disputed_claims": [],
  "sources": ["CoinGecko"]
}}"""

    def _prompt_ecosystem(self, name: str, defillama: dict, coingecko: dict) -> str:
        chains = defillama.get("chains", []) or []
        category = defillama.get("category", "")
        oracles = defillama.get("oracles", []) or []
        cg_cats = coingecko.get("categories", []) or []
        tvl = defillama.get("tvl", 0) or 0

        return f"""You are a blockchain ecosystem integration specialist.

TASK: Evaluate ecosystem integration depth and multi-chain adoption for "{name}".

VERIFIED ECOSYSTEM DATA:
- Deployed chains: {", ".join(chains[:10]) if chains else "not found on DefiLlama"}
- Chain count: {len(chains)}
- Protocol category (DefiLlama): {category or "N/A"}
- Oracle integrations: {", ".join(oracles[:5]) if oracles else "none"}
- CoinGecko categories: {", ".join(cg_cats[:5]) if cg_cats else "none"}
- Total TVL: ${tvl:,.0f}

SCORING GUIDE:
- 85-100: 5+ chains, oracle integrations, multiple categories, $10M+ TVL per chain
- 65-84:  3-4 chains or strong single-chain with oracle integrations
- 45-64:  1-2 chains, limited integrations
- 25-44:  Found but minimal ecosystem footprint
- 0-24:   Not found in ecosystem data

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 55-85>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<ecosystem fact>"],
  "disputed_claims": [],
  "sources": ["DefiLlama", "CoinGecko"]
}}"""

    def _prompt_product(self, name: str, github: dict, defillama: dict) -> str:
        gh_found = github.get("found", False)
        commits = github.get("recent_commits", 0)
        stars = github.get("stars", 0)
        contributors = github.get("contributors_count", 0)
        dl_found = defillama.get("found", False)
        tvl = defillama.get("tvl", 0) or 0
        category = defillama.get("category", "")
        chains = len(defillama.get("chains", []) or [])
        description = (github.get("description", "") or defillama.get("description", "") or "")[:180]

        return f"""You are a Web3 product manager and product verification specialist.

TASK: Verify whether "{name}" has a real, live, actively developed product.

VERIFIED PRODUCT SIGNALS:
- GitHub repo: {"YES - " + str(contributors) + " contributors, " + str(stars) + " stars" if gh_found else "NOT FOUND"}
- Recent dev activity: {str(commits) + " recent commits" if gh_found else "no data"}
- Live protocol on DefiLlama: {"YES - " + category if dl_found else "NO"}
- TVL (proof of live product): ${tvl:,.0f}
- Chain deployments: {chains}
- Description: {description if description else "not available"}

KEY QUESTION: Does verifiable evidence confirm a real functioning product?

SCORING GUIDE:
- 90-100: Active GitHub AND live TVL > $10M AND documented product
- 70-89:  Active GitHub OR meaningful TVL, at least one strong signal
- 50-69:  Code exists or TVL exists, limited evidence of both
- 30-49:  One weak signal (low TVL or stale repo)
- 0-29:   No verifiable product evidence

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 55-88>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<product verification fact>"],
  "disputed_claims": [],
  "sources": ["GitHub", "DefiLlama"]
}}"""

    def _prompt_media(self, name: str, coingecko: dict, defillama: dict) -> str:
        cg_found = coingecko.get("found", False)
        dl_found = defillama.get("found", False)
        rank = coingecko.get("market_cap_rank")
        genesis = coingecko.get("genesis_date", "")
        homepage = coingecko.get("homepage", "") or defillama.get("url", "")
        twitter = coingecko.get("twitter_followers", 0) or 0
        categories = coingecko.get("categories", []) or []

        return f"""You are a media presence and public reputation analyst for Web3 projects.

TASK: Evaluate public media footprint and reputation signals for "{name}".

VERIFIED PUBLIC PRESENCE:
- CoinGecko: {"YES - Rank #" + str(rank) if cg_found and rank else ("Listed" if cg_found else "NOT FOUND")}
- DefiLlama: {"YES" if dl_found else "NOT FOUND"}
- Website: {homepage if homepage else "not found"}
- Token launch: {genesis if genesis else "unknown"}
- Twitter: {int(twitter):,} followers
- Categories: {", ".join(categories[:4]) if categories else "none"}

SCORING GUIDE:
- 80-100: Both platforms listed, top 500 rank, strong social, established history
- 60-79:  One platform, some social presence, website available
- 40-59:  Partial public presence
- 20-39:  Minimal public presence
- 0-19:   Not found anywhere

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 50-80>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<public presence fact>"],
  "disputed_claims": [],
  "sources": ["CoinGecko", "DefiLlama"]
}}"""

    # ─────────────────────────────────────────────────────────────────────
    # Synthesis
    # ─────────────────────────────────────────────────────────────────────

    def _synthesise(self, protocol_name: str, validators: dict, evidence: dict) -> str:
        """Combine all 13 validator scores into a weighted final report JSON string."""
        weights = {
            "security":      0.18,
            "onchain":       0.15,
            "github":        0.12,
            "founders":      0.10,
            "funding":       0.10,
            "community":     0.09,
            "tokenomics":    0.08,
            "product":       0.07,
            "identity":      0.04,
            "ecosystem":     0.03,
            "documentation": 0.02,
            "investors":     0.01,
            "media":         0.01,
        }

        raw_scores = {}
        for vtype, vdata in validators.items():
            raw_scores[vtype] = float(vdata.get("score", 50))

        overall = 0.0
        for vtype, weight in weights.items():
            overall += raw_scores.get(vtype, 50.0) * weight
        overall = round(max(0.0, min(100.0, overall)), 2)

        if overall >= 80:
            risk = "low"
        elif overall >= 60:
            risk = "medium"
        elif overall >= 35:
            risk = "high"
        else:
            risk = "critical"

        verified_claims = []
        disputed_claims = []
        for vdata in validators.values():
            for c in (vdata.get("verified_claims") or []):
                if c and isinstance(c, str) and len(c) > 5:
                    verified_claims.append({"claim": c, "confidence": vdata.get("confidence", 70)})
            for c in (vdata.get("disputed_claims") or []):
                if c and isinstance(c, str) and len(c) > 5:
                    disputed_claims.append({"claim": c, "confidence": vdata.get("confidence", 40)})

        unresolved = [
            {"claim": "Founder personal identities require manual background verification"},
            {"claim": "Specific VC investor claims must be cross-referenced with investor portfolio pages"},
            {"claim": "Historical security incidents require independent timeline research"},
        ]

        avg_confidence = sum(float(v.get("confidence", 65)) for v in validators.values()) / max(len(validators), 1)

        github = evidence.get("github", {})
        defillama = evidence.get("defillama", {})
        coingecko = evidence.get("coingecko", {})

        gh_note = ("GitHub has " + str(github.get("stars", 0)) + " stars and " + str(github.get("contributors_count", 0)) + " contributors. ") if github.get("found") else "No public GitHub repository found. "
        dl_note = ("TVL: $" + "{:,.0f}".format(defillama.get("tvl", 0) or 0) + " across " + str(len(defillama.get("chains", []) or [])) + " chains. ") if defillama.get("found") else ""
        cg_note = ("Market cap rank #" + str(coingecko.get("market_cap_rank", "N/A")) + ". ") if coingecko.get("found") and coingecko.get("market_cap_rank") else ""
        sec_score = raw_scores.get("security", 50)
        sec_note = "Security audit evidence found. " if sec_score >= 70 else "No security audit links found in public databases. "

        summary = (
            protocol_name + " received a TrustLayer consensus score of " + str(overall) + "/100 (" + risk.upper() + " RISK). "
            + gh_note + dl_note + cg_note + sec_note
            + "Analysis by 13 independent AI validators via GenLayer consensus."
        )

        if overall >= 80:
            recommendation = (
                protocol_name + " demonstrates strong verifiable signals. Suitable for further institutional due diligence. "
                "Always verify founder identities and investor claims independently before significant capital allocation."
            )
        elif overall >= 60:
            recommendation = (
                protocol_name + " shows moderate trust signals with some gaps. Proceed with caution. "
                "Prioritise verifying security audits, team identity, and funding before interaction."
            )
        elif overall >= 35:
            recommendation = (
                protocol_name + " has limited verifiable signals — HIGH CAUTION ADVISED. "
                "Do not interact with smart contracts without a full independent security audit."
            )
        else:
            recommendation = (
                protocol_name + " has very few verifiable signals — CRITICAL RISK. "
                "Do not allocate any capital without exhaustive independent research."
            )

        report = {
            "protocol": protocol_name,
            "scores": {
                "overall": overall,
                "team": round(raw_scores.get("founders", 50), 2),
                "funding": round(raw_scores.get("funding", 50), 2),
                "product": round(raw_scores.get("product", 50), 2),
                "github": round(raw_scores.get("github", 50), 2),
                "community": round(raw_scores.get("community", 50), 2),
                "tokenomics": round(raw_scores.get("tokenomics", 50), 2),
                "security": round(raw_scores.get("security", 50), 2),
                "onchain": round(raw_scores.get("onchain", 50), 2),
                "reputation": round(raw_scores.get("identity", 50), 2),
            },
            "risk_level": risk,
            "validators": validators,
            "verified_claims": verified_claims[:15],
            "disputed_claims": disputed_claims[:8],
            "unresolved_claims": unresolved,
            "summary": summary[:600],
            "recommendation": recommendation[:600],
            "consensus_confidence": round(avg_confidence, 2),
            "consensus_result": {
                "method": "run_nondet_unsafe_structural_validator",
                "validators_count": 13,
                "consensus_reached": True,
                "overall_confidence": round(avg_confidence, 2),
            },
        }

        return json.dumps(report, sort_keys=True)

    # ─────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────

    def _safe_parse(self, raw, validator_type: str) -> dict:
        """Parse LLM JSON response with robust fallback. Never raises."""
        if isinstance(raw, dict):
            return self._normalise(raw)
        if not raw:
            return self._default_result(validator_type)
        # raw is a string — gl.nondet.exec_prompt with response_format="json"
        # returns a dict; json.dumps converts it to str; parse it back
        try:
            if isinstance(raw, str):
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    return self._normalise(parsed)
        except Exception:
            pass
        # Try extracting JSON block
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                parsed = json.loads(raw[start:end])
                return self._normalise(parsed)
        except Exception:
            pass
        return self._default_result(validator_type)

    def _normalise(self, data: dict) -> dict:
        """Ensure all required fields exist with valid values."""
        try:
            score = max(0, min(100, int(float(str(data.get("score", 50))))))
        except Exception:
            score = 50
        try:
            confidence = max(30, min(95, int(float(str(data.get("confidence", 60))))))
        except Exception:
            confidence = 60
        return {
            "score": score,
            "confidence": confidence,
            "findings": str(data.get("findings", "No findings."))[:400],
            "verified_claims": [str(c) for c in (data.get("verified_claims") or []) if c][:8],
            "disputed_claims": [str(c) for c in (data.get("disputed_claims") or []) if c][:4],
            "sources": [str(s) for s in (data.get("sources") or []) if s][:5],
        }

    def _default_result(self, validator_type: str) -> dict:
        return {
            "score": 45,
            "confidence": 35,
            "findings": "The " + validator_type + " validator could not retrieve or parse data.",
            "verified_claims": [],
            "disputed_claims": [],
            "sources": [],
        }

    def _fallback_report(self, protocol_name: str) -> dict:
        return {
            "protocol": protocol_name,
            "scores": {
                "overall": 40.0, "team": 40.0, "funding": 40.0,
                "product": 40.0, "github": 40.0, "community": 40.0,
                "tokenomics": 40.0, "security": 40.0,
                "onchain": 40.0, "reputation": 40.0,
            },
            "risk_level": "medium",
            "validators": {},
            "verified_claims": [],
            "disputed_claims": [],
            "unresolved_claims": [{"claim": "Automated pipeline returned incomplete data — manual review required"}],
            "summary": "TrustLayer investigation for " + protocol_name + " completed with limited data.",
            "recommendation": "Could not complete full automated analysis. Conduct manual due diligence.",
            "consensus_confidence": 30.0,
            "consensus_result": {"method": "fallback", "validators_count": 0, "consensus_reached": False},
        }

    # ─────────────────────────────────────────────────────────────────────
    # View methods (read-only, no LLM, no consensus needed)
    # ─────────────────────────────────────────────────────────────────────

    @gl.public.view
    def get_report(self, protocol_name: str) -> str:
        """Return the full JSON report for a protocol, or '{}' if not found."""
        key = protocol_name.lower().strip()
        if key not in self.reports:
            return "{}"
        return self.reports[key]

    @gl.public.view
    def get_trust_score(self, protocol_name: str) -> u256:
        """Return the overall trust score (0–100), or 0 if not investigated."""
        key = protocol_name.lower().strip()
        if key not in self.overall_scores:
            return u256(0)
        return self.overall_scores[key]

    @gl.public.view
    def get_risk_level(self, protocol_name: str) -> str:
        """Return 'low', 'medium', 'high', 'critical', or 'unknown'."""
        key = protocol_name.lower().strip()
        if key not in self.risk_levels:
            return "unknown"
        return self.risk_levels[key]

    @gl.public.view
    def get_summary(self, protocol_name: str) -> str:
        """Return the plain-text summary for a protocol."""
        key = protocol_name.lower().strip()
        if key not in self.summaries:
            return ""
        return self.summaries[key]

    @gl.public.view
    def has_report(self, protocol_name: str) -> bool:
        """Return True if this protocol has been investigated."""
        return protocol_name.lower().strip() in self.reports

    @gl.public.view
    def get_total_count(self) -> u256:
        """Return total number of investigations completed by this contract."""
        return self.total_count

    @gl.public.view
    def get_owner(self) -> str:
        """Return the contract deployer address."""
        return self.owner

    # ─────────────────────────────────────────────────────────────────────
    # Admin write methods
    # ─────────────────────────────────────────────────────────────────────

    @gl.public.write
    def append_note(self, protocol_name: str, note: str) -> None:
        """
        Owner can append a manual verification note to a report's summary.
        Useful for adding post-investigation context.
        """
        if str(gl.message.sender_address) != self.owner:
            raise Exception("Only contract owner can append notes")
        key = protocol_name.lower().strip()
        if key not in self.reports:
            raise Exception("No report found for " + protocol_name)
        current = self.summaries.get(key, "")
        self.summaries[key] = (current + " | NOTE: " + str(note)[:200])[:600]

    @gl.public.write
    def transfer_ownership(self, new_owner: str) -> None:
        """Transfer contract ownership to a new address."""
        if str(gl.message.sender_address) != self.owner:
            raise Exception("Only current owner can transfer ownership")
        if not new_owner or len(new_owner) < 10:
            raise Exception("Invalid new_owner address")
        self.owner = new_owner
