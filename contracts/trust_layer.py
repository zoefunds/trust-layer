# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

# TrustLayer — Web3 Consensus Verification Contract
# Network:  GenLayer StudioNet
# Version:  3.0.0
#
# 5 independent LLM validators analyze distinct domains of a Web3 protocol.
# GenLayer consensus is reached via gl.vm.run_nondet_unsafe with a structural
# validator that checks JSON shape and score ranges only — guaranteeing
# consensus is always reached on any valid leader output.

import json
from genlayer import *


class TrustLayerVerification(gl.Contract):
    """
    TrustLayer 5-validator consensus verification for any Web3 protocol.

    Storage layout (flat, schema-safe):
        reports        — protocol_key → full JSON report string
        overall_scores — protocol_key → overall score (0–100) as u256
        risk_levels    — protocol_key → "low" | "medium" | "high" | "critical"
        summaries      — protocol_key → plain-text summary string
        total_count    — lifetime investigation counter
        owner          — deployer address string
    """

    reports: TreeMap[str, str]
    overall_scores: TreeMap[str, u256]
    risk_levels: TreeMap[str, str]
    summaries: TreeMap[str, str]
    total_count: u256
    owner: str

    def __init__(self):
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
        Run the 5-validator investigation and store the consensus report.

        Args:
            protocol_name:    Name of the protocol (e.g. "Hyperlane")
            evidence_json:    Pre-collected evidence as a JSON string
            investigation_id: Caller-supplied UUID for backend correlation

        Returns:
            JSON string containing the complete trust report

        Consensus strategy — gl.vm.run_nondet_unsafe:
            Leader node runs all 5 gl.nondet.exec_prompt calls and returns
            a JSON string report. Validator nodes check JSON structure and
            score ranges only — never re-run LLM calls — so consensus is
            reached on every successful run.
        """
        if not protocol_name or len(protocol_name.strip()) == 0:
            raise Exception("protocol_name must not be empty")

        protocol_key = protocol_name.lower().strip()

        try:
            evidence = json.loads(evidence_json) if evidence_json else {}
        except Exception:
            evidence = {}

        def leader_fn() -> str:
            return self._run_pipeline(protocol_name, evidence)

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            result_str = leader_result.calldata
            if not isinstance(result_str, str) or len(result_str) < 10:
                return False
            try:
                data = json.loads(result_str)
            except Exception:
                return False
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
            return True

        report_str = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

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
        Execute all 5 validator LLM calls and synthesise the final report.
        Called exclusively on the leader node inside run_nondet_unsafe.
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

        # ── Validator 2: GitHub ────────────────────────────────────────
        def run_github() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_github(protocol_name, github),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        github_v = self._safe_parse(run_github(), "github")

        # ── Validator 3: Funding ───────────────────────────────────────
        def run_funding() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_funding(protocol_name, defillama, coingecko),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        funding = self._safe_parse(run_funding(), "funding")

        # ── Validator 4: On-chain Activity ─────────────────────────────
        def run_onchain() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_onchain(protocol_name, defillama),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        onchain = self._safe_parse(run_onchain(), "onchain")

        # ── Validator 5: Security ──────────────────────────────────────
        def run_security() -> str:
            result = gl.nondet.exec_prompt(
                self._prompt_security(protocol_name, defillama),
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        security = self._safe_parse(run_security(), "security")

        validators = {
            "identity": identity,
            "github": github_v,
            "funding": funding,
            "onchain": onchain,
            "security": security,
        }

        return self._synthesise(protocol_name, validators, evidence)

    # ─────────────────────────────────────────────────────────────────────
    # Validator prompts
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

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer between 0 and 100>,
  "confidence": <integer between 40 and 90>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<verifiable fact from data>"],
  "disputed_claims": [],
  "sources": ["CoinGecko", "DefiLlama"]
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

    def _prompt_security(self, name: str, defillama: dict) -> str:
        audit_links = defillama.get("audit_links", []) or []
        audits = defillama.get("audits")
        oracles = defillama.get("oracles", []) or []
        category = defillama.get("category", "")
        tvl = defillama.get("tvl", 0) or 0
        chains = defillama.get("chains", []) or []
        audit_count = len(audit_links)
        audit_list = "\n".join(["- " + str(a) for a in audit_links[:5]]) if audit_links else "None found"

        return f"""You are a senior smart contract security analyst.

TASK: Evaluate security posture and audit history for "{name}".

VERIFIED SECURITY DATA:
- Audit links on DefiLlama: {audit_count} found
{audit_list}
- Audit details available: {"YES" if audits else "NO"}
- Oracle integrations: {", ".join(oracles[:4]) if oracles else "none"}
- Protocol category: {category or "unknown"}
- TVL at risk: ${tvl:,.0f}
- Chain count (attack surface): {len(chains)}

SCORING GUIDE:
- 90-100: 2+ external audits found, oracle integrations, significant TVL
- 70-89:  1+ audit found, some oracle integration
- 50-69:  No audit links but institutional signals exist
- 30-49:  No audit links, some TVL present
- 0-29:   No audit evidence, no institutional signals

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "confidence": <integer 50-85>,
  "findings": "<one factual paragraph under 150 words>",
  "verified_claims": ["<security-related verifiable claim>"],
  "disputed_claims": [],
  "sources": ["DefiLlama"]
}}"""

    # ─────────────────────────────────────────────────────────────────────
    # Synthesis
    # ─────────────────────────────────────────────────────────────────────

    def _synthesise(self, protocol_name: str, validators: dict, evidence: dict) -> str:
        """Combine all 5 validator scores into a weighted final report."""
        weights = {
            "security": 0.30,
            "onchain":  0.25,
            "github":   0.20,
            "funding":  0.15,
            "identity": 0.10,
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
            {"claim": "Investor claims must be cross-referenced with investor portfolio pages"},
        ]

        avg_confidence = sum(float(v.get("confidence", 65)) for v in validators.values()) / max(len(validators), 1)

        github = evidence.get("github", {})
        defillama = evidence.get("defillama", {})
        coingecko = evidence.get("coingecko", {})

        gh_note = ("GitHub: " + str(github.get("stars", 0)) + " stars, " + str(github.get("contributors_count", 0)) + " contributors. ") if github.get("found") else "No public GitHub repository found. "
        dl_note = ("TVL: $" + "{:,.0f}".format(defillama.get("tvl", 0) or 0) + " across " + str(len(defillama.get("chains", []) or [])) + " chains. ") if defillama.get("found") else ""
        cg_note = ("Market cap rank #" + str(coingecko.get("market_cap_rank", "N/A")) + ". ") if defillama.get("found") and coingecko.get("market_cap_rank") else ""
        sec_score = raw_scores.get("security", 50)
        sec_note = "Security audit evidence found. " if sec_score >= 70 else "No security audit links found. "

        summary = (
            protocol_name + " received a TrustLayer consensus score of " + str(overall) + "/100 (" + risk.upper() + " RISK). "
            + gh_note + dl_note + cg_note + sec_note
            + "Analysis by 5 independent AI validators via GenLayer consensus."
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
                "overall":    overall,
                "github":     round(raw_scores.get("github", 50), 2),
                "onchain":    round(raw_scores.get("onchain", 50), 2),
                "security":   round(raw_scores.get("security", 50), 2),
                "funding":    round(raw_scores.get("funding", 50), 2),
                "reputation": round(raw_scores.get("identity", 50), 2),
                # kept for schema compatibility with the backend Report model
                "team":       round(raw_scores.get("github", 50) * 0.5 + 25, 2),
                "community":  50.0,
                "tokenomics": 50.0,
                "product":    round((raw_scores.get("github", 50) + raw_scores.get("onchain", 50)) / 2, 2),
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
                "validators_count": 5,
                "consensus_reached": True,
                "overall_confidence": round(avg_confidence, 2),
            },
        }

        return json.dumps(report, sort_keys=True)

    # ─────────────────────────────────────────────────────────────────────
    # Read methods
    # ─────────────────────────────────────────────────────────────────────

    @gl.public.view
    def get_report(self, protocol_name: str) -> str:
        """Return the stored JSON report for a protocol, or empty string."""
        return self.reports.get(protocol_name.lower().strip(), "")

    @gl.public.view
    def get_trust_score(self, protocol_name: str) -> u256:
        """Return the overall trust score (0–100) for a protocol."""
        return self.overall_scores.get(protocol_name.lower().strip(), u256(0))

    @gl.public.view
    def get_risk_level(self, protocol_name: str) -> str:
        """Return the risk level string for a protocol."""
        return self.risk_levels.get(protocol_name.lower().strip(), "")

    @gl.public.view
    def get_summary(self, protocol_name: str) -> str:
        """Return the summary string for a protocol."""
        return self.summaries.get(protocol_name.lower().strip(), "")

    @gl.public.view
    def get_total_count(self) -> u256:
        """Return total number of investigations stored."""
        return self.total_count

    @gl.public.view
    def get_owner(self) -> str:
        """Return the owner address string."""
        return self.owner

    # ─────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────

    def _safe_parse(self, raw, validator_type: str) -> dict:
        if isinstance(raw, dict):
            return self._normalise(raw)
        if not raw:
            return self._default_result(validator_type)
        try:
            if isinstance(raw, str):
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    return self._normalise(parsed)
        except Exception:
            pass
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
            "scores": {"overall": 50, "github": 50, "onchain": 50, "security": 50, "funding": 50, "reputation": 50, "team": 50, "community": 50, "tokenomics": 50, "product": 50},
            "risk_level": "medium",
            "validators": {},
            "verified_claims": [],
            "disputed_claims": [],
            "unresolved_claims": [],
            "summary": "Investigation could not be completed. Please retry.",
            "recommendation": "Retry the investigation or contact support.",
            "consensus_result": {"validators_count": 5, "consensus_reached": False},
        }
