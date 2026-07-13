# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


class TrustLayerVerification(gl.Contract):
    """
    TrustLayer 13-validator consensus verification for any Web3 protocol.

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
        Run the 13-validator investigation and store the consensus report.

        Args:
            protocol_name:    Name of the protocol (e.g. "Hyperlane")
            evidence_json:    Pre-collected evidence as a JSON string
            investigation_id: Caller-supplied UUID for backend correlation

        Returns:
            JSON string containing the complete trust report

        Consensus strategy — gl.vm.run_nondet_unsafe:
            Leader node runs all 13 gl.nondet.exec_prompt calls and returns
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
            # Called via the class, not `self` — capturing `self` here would pull the
            # whole contract instance (including TreeMap storage fields) into the
            # nondet closure, which GenVM has to pickle and warns about
            # ("Detected pickling storage class"). Only plain str/dict args cross
            # the nondet boundary this way.
            return TrustLayerVerification._run_pipeline(protocol_name, evidence)

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

    @staticmethod
    def _fetch_web_evidence(protocol_name: str) -> dict:
        """
        Fetch live data from CoinGecko, DefiLlama, and GitHub directly
        from within the intelligent contract using gl.nondet.get_webpage.
        Returns a dict with keys: coingecko, defillama, github.
        """
        slug = protocol_name.lower().strip().replace(" ", "-")

        # ── CoinGecko ──────────────────────────────────────────────────
        coingecko = {"found": False}
        try:
            cg_search_raw = gl.nondet.get_webpage(
                "https://api.coingecko.com/api/v3/search?query=" + slug,
                mode="text",
            )
            cg_search = json.loads(cg_search_raw) if isinstance(cg_search_raw, str) else cg_search_raw
            coins = cg_search.get("coins", [])
            if coins:
                coin_id = coins[0].get("id", slug)
                cg_detail_raw = gl.nondet.get_webpage(
                    "https://api.coingecko.com/api/v3/coins/" + coin_id
                    + "?localization=false&tickers=false&community_data=false&developer_data=false",
                    mode="text",
                )
                cg = json.loads(cg_detail_raw) if isinstance(cg_detail_raw, str) else cg_detail_raw
                market = cg.get("market_data", {})
                coingecko = {
                    "found": True,
                    "name": cg.get("name", ""),
                    "market_cap_rank": cg.get("market_cap_rank"),
                    "market_cap": (market.get("market_cap") or {}).get("usd", 0),
                    "total_volume_24h": (market.get("total_volume") or {}).get("usd", 0),
                    "price_change_7d": market.get("price_change_percentage_7d"),
                    "genesis_date": cg.get("genesis_date", "unknown"),
                    "homepage": ((cg.get("links") or {}).get("homepage") or [""])[0],
                }
        except Exception:
            pass

        # ── DefiLlama ──────────────────────────────────────────────────
        defillama = {"found": False}
        try:
            dl_raw = gl.nondet.get_webpage(
                "https://api.llama.fi/protocol/" + slug,
                mode="text",
            )
            dl = json.loads(dl_raw) if isinstance(dl_raw, str) else dl_raw
            if dl.get("name"):
                defillama = {
                    "found": True,
                    "name": dl.get("name", ""),
                    "category": dl.get("category", ""),
                    "tvl": dl.get("tvl", 0),
                    "tvl_change_24h": dl.get("change_1d"),
                    "tvl_change_7d": dl.get("change_7d"),
                    "chains": dl.get("chains", []),
                    "oracles": dl.get("oracles", []),
                    "audit_links": dl.get("audit_links", []),
                    "audits": dl.get("audits"),
                    "mcap_tvl": dl.get("mcap/tvl"),
                    "url": dl.get("url", ""),
                }
        except Exception:
            pass

        # ── GitHub (single search call — repo stats are in the response) ─
        github = {"found": False}
        try:
            gh_search_raw = gl.nondet.get_webpage(
                "https://api.github.com/search/repositories?q=" + slug + "+in:name&per_page=1",
                mode="text",
            )
            gh_search = json.loads(gh_search_raw) if isinstance(gh_search_raw, str) else gh_search_raw
            items = gh_search.get("items", [])
            if items:
                repo = items[0]
                github = {
                    "found": True,
                    "full_name": repo.get("full_name", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "open_issues": repo.get("open_issues_count", 0),
                    "language": repo.get("language", ""),
                    "description": (repo.get("description") or "")[:120],
                    "license": (repo.get("license") or {}).get("name", ""),
                    "is_archived": repo.get("archived", False),
                    "contributors_count": 0,
                    "recent_commits": 0,
                }
        except Exception:
            pass

        return {"coingecko": coingecko, "defillama": defillama, "github": github}

    @staticmethod
    def _run_pipeline(protocol_name: str, evidence: dict) -> str:
        """
        Execute 5 batched LLM calls (each covering 2-3 of the 13 sources) and
        synthesise the final report. Called exclusively on the leader node
        inside run_nondet_unsafe.

        The leader node first fetches live data from the web (CoinGecko,
        DefiLlama, GitHub) using gl.nondet.get_webpage, then merges it with
        any pre-collected evidence passed by the caller. Web-fetched data
        takes priority so validators always work with the freshest signals.

        Batching (rather than 13 sequential LLM round-trips) keeps total leader
        execution time well under GenVM's execution timeout — 13 sequential
        calls was pushing real-world protocols past the timeout and leaving
        the transaction stuck in PROPOSING with no leader result to vote on.

        This method and everything it calls is a @staticmethod so nothing here
        holds a reference to `self` / the contract's storage fields — avoids
        GenVM's "pickling storage class" warning when the closure is shipped
        into the nondet sandbox.
        """
        web_evidence = TrustLayerVerification._fetch_web_evidence(protocol_name)

        github = {**evidence.get("github", {}), **{k: v for k, v in web_evidence["github"].items() if v}}
        defillama = {**evidence.get("defillama", {}), **{k: v for k, v in web_evidence["defillama"].items() if v}}
        coingecko = {**evidence.get("coingecko", {}), **{k: v for k, v in web_evidence["coingecko"].items() if v}}

        # ── Batch 1: Identity, Founders, Investors ─────────────────────
        batch1 = gl.nondet.exec_prompt(
            TrustLayerVerification._prompt_batch_identity(protocol_name, github, coingecko, defillama),
            response_format="json",
        )
        identity = TrustLayerVerification._safe_parse_key(batch1, "identity", "identity")
        founders = TrustLayerVerification._safe_parse_key(batch1, "founders", "founders")
        investors = TrustLayerVerification._safe_parse_key(batch1, "investors", "investors")

        # ── Batch 2: Funding, Tokenomics ────────────────────────────────
        batch2 = gl.nondet.exec_prompt(
            TrustLayerVerification._prompt_batch_financial(protocol_name, defillama, coingecko),
            response_format="json",
        )
        funding = TrustLayerVerification._safe_parse_key(batch2, "funding", "funding")
        tokenomics = TrustLayerVerification._safe_parse_key(batch2, "tokenomics", "tokenomics")

        # ── Batch 3: GitHub, Documentation, Product ────────────────────
        batch3 = gl.nondet.exec_prompt(
            TrustLayerVerification._prompt_batch_dev(protocol_name, github, defillama, coingecko),
            response_format="json",
        )
        github_v = TrustLayerVerification._safe_parse_key(batch3, "github", "github")
        documentation = TrustLayerVerification._safe_parse_key(batch3, "documentation", "documentation")
        product = TrustLayerVerification._safe_parse_key(batch3, "product", "product")

        # ── Batch 4: On-chain, Ecosystem, Security ─────────────────────
        batch4 = gl.nondet.exec_prompt(
            TrustLayerVerification._prompt_batch_infra(protocol_name, defillama),
            response_format="json",
        )
        onchain = TrustLayerVerification._safe_parse_key(batch4, "onchain", "onchain")
        ecosystem = TrustLayerVerification._safe_parse_key(batch4, "ecosystem", "ecosystem")
        security = TrustLayerVerification._safe_parse_key(batch4, "security", "security")

        # ── Batch 5: Community, Media ───────────────────────────────────
        batch5 = gl.nondet.exec_prompt(
            TrustLayerVerification._prompt_batch_public(protocol_name, coingecko),
            response_format="json",
        )
        community = TrustLayerVerification._safe_parse_key(batch5, "community", "community")
        media = TrustLayerVerification._safe_parse_key(batch5, "media", "media")

        validators = {
            "identity": identity,
            "founders": founders,
            "funding": funding,
            "investors": investors,
            "github": github_v,
            "documentation": documentation,
            "onchain": onchain,
            "tokenomics": tokenomics,
            "security": security,
            "community": community,
            "ecosystem": ecosystem,
            "product": product,
            "media": media,
        }

        return TrustLayerVerification._synthesise(protocol_name, validators, evidence)

    # ─────────────────────────────────────────────────────────────────────
    # Validator prompts
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _prompt_batch_identity(name: str, github: dict, coingecko: dict, defillama: dict) -> str:
        cg_found = coingecko.get("found", False)
        dl_found = defillama.get("found", False)
        cg_name = coingecko.get("name", "")
        cg_rank = coingecko.get("market_cap_rank", "N/A")
        dl_name = defillama.get("name", "")
        dl_category = defillama.get("category", "")
        genesis = coingecko.get("genesis_date", "unknown")
        homepage = coingecko.get("homepage", "") or defillama.get("url", "")
        gh_found = github.get("found", False)
        full_name = github.get("full_name", "")
        contributors = github.get("contributors_count", 0)
        mcap = coingecko.get("market_cap", 0) or 0
        price_change_7d = coingecko.get("price_change_7d")
        return f"""You are a Web3 due-diligence analyst. Score 3 domains for "{name}". Be concise (max 60 words per findings field).
DATA (verified, from live APIs):
- CoinGecko: {"YES - " + cg_name + ", Rank #" + str(cg_rank) if cg_found else "NOT FOUND"} | Market cap: ${mcap:,.0f} | 7d change: {str(price_change_7d) + "%" if price_change_7d is not None else "N/A"}
- DefiLlama: {"YES - " + dl_name + ", " + dl_category if dl_found else "NOT FOUND"}
- Launch date: {genesis} | Website: {homepage or "Not found"}
- GitHub org/repo: {"YES - " + full_name if gh_found else "NOT FOUND"} | Active contributors: {contributors}

For "founders" and "investors" specifically: if "{name}" is a protocol you have public knowledge of (e.g. from documentation, news, or well-known team/funding history), name the actual founders and/or known investors/VCs and cite that as "public knowledge" in sources — do not default to "cannot verify" just because it isn't in the DATA block above. Only report founders/investors as unverifiable if you genuinely have no knowledge of them AND the DATA block gives no signal. Never invent a name you aren't reasonably confident about.

DOMAINS:
1. identity — public legitimacy/verifiability. 85-100=both platforms+website, 65-84=one platform, 45-64=partial, 25-44=minimal, 0-24=not found.
2. founders — team transparency/credibility, using public knowledge if available. 85-100=named founders identified with confidence, 65-84=org+contributors verified but founders not confidently named, 45-64=repo only, 25-44=minimal, 0-24=no data.
3. investors — institutional/investor reputation, using public knowledge if available. 85-100=named top-tier investors identified, 65-84=strong market signals, 45-64=moderate, 25-44=limited, 0-24=none.

Respond ONLY valid JSON with this exact shape:
{{"identity":{{"score":<0-100>,"confidence":<40-90>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["CoinGecko","DefiLlama"]}},
"founders":{{"score":<0-100>,"confidence":<35-85>,"findings":"<60 words>","verified_claims":["<fact, name founders if known>"],"disputed_claims":[],"sources":["GitHub","public knowledge"]}},
"investors":{{"score":<0-100>,"confidence":<30-75>,"findings":"<60 words>","verified_claims":["<fact, name investors if known>"],"disputed_claims":[],"sources":["CoinGecko","public knowledge"]}}}}"""

    @staticmethod
    def _prompt_batch_financial(name: str, defillama: dict, coingecko: dict) -> str:
        tvl = defillama.get("tvl", 0) or 0
        mcap = coingecko.get("market_cap", 0) or 0
        rank = coingecko.get("market_cap_rank")
        tvl_24h = defillama.get("tvl_change_24h")
        tvl_7d = defillama.get("tvl_change_7d")
        chains = len(defillama.get("chains", []) or [])
        volume = coingecko.get("total_volume_24h", 0) or 0
        mcap_tvl = defillama.get("mcap_tvl")
        cg_found = coingecko.get("found", False)
        return f"""You are a DeFi financial analyst. Score 2 domains for "{name}" using ONLY the data below. Be concise (max 60 words per findings field).
DATA:
- TVL: ${tvl:,.0f} | 24h change: {str(tvl_24h) + "%" if tvl_24h is not None else "N/A"} | 7d change: {str(tvl_7d) + "%" if tvl_7d is not None else "N/A"} | Chains: {chains}
- Market cap: ${mcap:,.0f} | Rank: {"#" + str(rank) if rank else "unranked"} | 24h volume: ${volume:,.0f}
- Token listed on CoinGecko: {"YES" if cg_found else "NO"} | Mcap/TVL ratio: {str(round(mcap_tvl, 2)) + "x" if mcap_tvl else "N/A"}

DOMAINS:
1. funding — financial health/funding signals. 85-100=TVL>$100M+top200, 65-84=TVL$10M-100M, 45-64=TVL$1M-10M, 25-44=TVL<$1M, 0-24=no data.
2. tokenomics — token design/sustainability. 90-100=top200+healthy metrics, 70-89=rank200-500, 50-69=rank500-1000, 30-49=ranked but poor, 0-29=no token data.

Respond ONLY valid JSON with this exact shape:
{{"funding":{{"score":<0-100>,"confidence":<55-88>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["DefiLlama","CoinGecko"]}},
"tokenomics":{{"score":<0-100>,"confidence":<45-85>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["CoinGecko","DefiLlama"]}}}}"""

    @staticmethod
    def _prompt_batch_dev(name: str, github: dict, defillama: dict, coingecko: dict) -> str:
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
        description = (github.get("description", "") or "")[:120]
        homepage = coingecko.get("homepage", "")
        category = defillama.get("category", "")
        tvl = defillama.get("tvl", 0) or 0
        return f"""You are a Web3 technical analyst. Score 3 domains for "{name}" using ONLY the data below. Be concise (max 60 words per findings field).
DATA:
- Repo: {"FOUND - " + full_name if found else "NOT FOUND"} | Description: {description or "none"}
- Stars: {stars:,} | Forks: {forks:,} | Issues: {open_issues:,} | Language: {language or "N/A"}
- Recent commits: {recent_commits} | Contributors: {contributors} | License: {license_name or "none"} | Archived: {"YES" if is_archived else "NO"}
- Official website/docs: {homepage or "Not found"} | Protocol category: {category or "N/A"} | TVL: ${tvl:,.0f}

DOMAINS:
1. github — dev activity/code health. 90-100=500+stars+5+contributors+active+license, 70-89=100-500stars, 50-69=10-100stars, 30-49=barely active, 0-29=no repo.
2. documentation — docs quality/dev resources (infer from repo+website). 90-100=comprehensive, 70-89=good, 50-69=basic, 30-49=minimal, 0-29=none found.
3. product — product maturity/technical delivery. 90-100=active dev+TVL+clear category, 70-89=good signals+some TVL, 50-69=moderate, 30-49=limited, 0-29=none.

Respond ONLY valid JSON with this exact shape:
{{"github":{{"score":<0-100>,"confidence":<60-92>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["GitHub"]}},
"documentation":{{"score":<0-100>,"confidence":<40-82>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["GitHub","Web"]}},
"product":{{"score":<0-100>,"confidence":<45-85>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["GitHub","DefiLlama"]}}}}"""

    @staticmethod
    def _prompt_batch_infra(name: str, defillama: dict) -> str:
        found = defillama.get("found", False)
        tvl = defillama.get("tvl", 0) or 0
        tvl_24h = defillama.get("tvl_change_24h")
        tvl_7d = defillama.get("tvl_change_7d")
        chains = defillama.get("chains", []) or []
        category = defillama.get("category", "")
        oracles = defillama.get("oracles", []) or []
        mcap_tvl = defillama.get("mcap_tvl")
        audit_links = defillama.get("audit_links", []) or []
        audits = defillama.get("audits")
        audit_count = len(audit_links)
        audit_list = "; ".join([str(a) for a in audit_links[:3]]) if audit_links else "None found"
        return f"""You are a Web3 infrastructure analyst. Score 3 domains for "{name}" using ONLY the data below. Be concise (max 60 words per findings field).
DATA:
- DefiLlama indexed: {"YES" if found else "NO"} | TVL: ${tvl:,.0f} | 24h: {str(tvl_24h) + "%" if tvl_24h is not None else "N/A"} | 7d: {str(tvl_7d) + "%" if tvl_7d is not None else "N/A"}
- Chains: {", ".join(chains[:8]) if chains else "none"} ({len(chains)} total) | Category: {category or "N/A"} | Oracles: {", ".join(oracles[:4]) if oracles else "none"}
- Mcap/TVL: {str(round(mcap_tvl, 2)) + "x" if mcap_tvl else "N/A"} | Audit links: {audit_count} ({audit_list}) | Audit details available: {"YES" if audits else "NO"}

DOMAINS:
1. onchain — on-chain activity/protocol health. 90-100=TVL>$500M+5+chains+growing, 70-89=TVL$50M-500M, 50-69=TVL$5M-50M, 30-49=TVL<$5M, 0-29=not found.
2. ecosystem — cross-chain/integration depth. 90-100=5+chains+oracles+integrations, 70-89=3-4chains+oracle, 50-69=2chains, 30-49=single chain, 0-29=no data.
3. security — audit history/security posture. 90-100=2+audits+oracles+TVL, 70-89=1+audit, 50-69=no audits but institutional signals, 30-49=no audits+some TVL, 0-29=no evidence.

Respond ONLY valid JSON with this exact shape:
{{"onchain":{{"score":<0-100>,"confidence":<60-90>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["DefiLlama"]}},
"ecosystem":{{"score":<0-100>,"confidence":<50-88>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["DefiLlama"]}},
"security":{{"score":<0-100>,"confidence":<50-85>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["DefiLlama"]}}}}"""

    @staticmethod
    def _prompt_batch_public(name: str, coingecko: dict) -> str:
        cg_found = coingecko.get("found", False)
        rank = coingecko.get("market_cap_rank")
        volume = coingecko.get("total_volume_24h", 0) or 0
        homepage = coingecko.get("homepage", "")
        return f"""You are a Web3 public-perception analyst. Score 2 domains for "{name}" using ONLY the data below. Be concise (max 60 words per findings field).
DATA:
- CoinGecko listed: {"YES, rank #" + str(rank) if cg_found and rank else "NO"} | 24h volume: ${volume:,.0f} | Website: {homepage or "Not found"}
- Note: Direct social media metrics unavailable; infer from market engagement signals only.

DOMAINS:
1. community — community strength/engagement. 90-100=massive (rank<100), 70-89=strong (rank100-300), 50-69=moderate (rank300-1000), 30-49=limited, 0-29=no signals.
2. media — media coverage/public claims verifiability. 90-100=top100+widespread, 70-89=rank100-300, 50-69=rank300-1000, 30-49=limited, 0-29=no presence.

Respond ONLY valid JSON with this exact shape:
{{"community":{{"score":<0-100>,"confidence":<35-75>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["CoinGecko"]}},
"media":{{"score":<0-100>,"confidence":<35-78>,"findings":"<60 words>","verified_claims":["<fact>"],"disputed_claims":[],"sources":["CoinGecko","Web"]}}}}"""

    # ─────────────────────────────────────────────────────────────────────
    # Synthesis
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _synthesise(protocol_name: str, validators: dict, evidence: dict) -> str:
        """Combine all 13 validator scores into a weighted final report."""
        weights = {
            "security":      0.15,
            "onchain":       0.12,
            "github":        0.10,
            "funding":       0.10,
            "identity":      0.08,
            "founders":      0.08,
            "investors":     0.07,
            "documentation": 0.07,
            "tokenomics":    0.07,
            "community":     0.06,
            "ecosystem":     0.05,
            "product":       0.05,
            "media":         0.00,
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

        # Only flag as unresolved if the LLM genuinely couldn't identify anything —
        # if founders/investors were named (verified_claims non-empty), don't
        # blanket-disclaim them.
        unresolved = []
        if not (validators.get("founders", {}).get("verified_claims")):
            unresolved.append({"claim": "Founder identities could not be determined from available data or public knowledge"})
        if not (validators.get("investors", {}).get("verified_claims")):
            unresolved.append({"claim": "Investor/backer identities could not be determined from available data or public knowledge"})

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
            + "Analysis by 13 independent sources via GenLayer consensus."
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
                "team":       round((raw_scores.get("founders", 50) + raw_scores.get("investors", 50)) / 2, 2),
                "community":  round(raw_scores.get("community", 50), 2),
                "tokenomics": round(raw_scores.get("tokenomics", 50), 2),
                "product":    round(raw_scores.get("product", 50), 2),
            },
            "risk_level": risk,
            "validators": validators,
            "verified_claims": verified_claims[:20],
            "disputed_claims": disputed_claims[:10],
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

    @staticmethod
    def _safe_parse_key(raw, key: str, validator_type: str) -> dict:
        """Extract and normalise a nested sub-object from a batched LLM response."""
        parsed = raw
        if not isinstance(parsed, dict):
            if not raw:
                return TrustLayerVerification._default_result(validator_type)
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else raw
            except Exception:
                try:
                    start = raw.find("{")
                    end = raw.rfind("}") + 1
                    parsed = json.loads(raw[start:end]) if start >= 0 and end > start else {}
                except Exception:
                    parsed = {}
        if not isinstance(parsed, dict):
            return TrustLayerVerification._default_result(validator_type)
        sub = parsed.get(key)
        if not isinstance(sub, dict):
            return TrustLayerVerification._default_result(validator_type)
        return TrustLayerVerification._normalise(sub)

    @staticmethod
    def _normalise(data: dict) -> dict:
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

    @staticmethod
    def _default_result(validator_type: str) -> dict:
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
