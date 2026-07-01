"use client";

import { useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useInvestigationsStore } from "@/stores/investigations";
import { createSSEConnection } from "@/lib/api";
import { VALIDATOR_LABELS } from "@/types";
import type { SSEEvent, ValidatorType } from "@/types";
import { getTrustColor, getRiskColor, getRiskLabel, formatDate } from "@/lib/utils";
import {
  Shield, GitBranch, Users, DollarSign, Globe, Lock,
  FileText, Link2, Coins, MessageCircle, Package, Radio,
  Briefcase, CheckCircle2, XCircle, Clock, AlertTriangle, ArrowLeft,
} from "lucide-react";

const VALIDATOR_ICONS: Record<ValidatorType, React.ElementType> = {
  identity: Shield,
  founders: Users,
  funding: DollarSign,
  investors: Briefcase,
  github: GitBranch,
  documentation: FileText,
  onchain: Link2,
  tokenomics: Coins,
  security: Lock,
  community: MessageCircle,
  ecosystem: Globe,
  product: Package,
  media: Radio,
};

const SCORE_CATEGORIES = [
  { key: "team" as const, label: "Team" },
  { key: "funding" as const, label: "Funding" },
  { key: "product" as const, label: "Product" },
  { key: "github" as const, label: "GitHub" },
  { key: "community" as const, label: "Community" },
  { key: "tokenomics" as const, label: "Tokenomics" },
  { key: "security" as const, label: "Security" },
  { key: "onchain" as const, label: "On-chain" },
  { key: "reputation" as const, label: "Reputation" },
];

export default function InvestigationPage() {
  const { id } = useParams<{ id: string }>();
  const { current, fetchOne, updateValidator, setCurrentStatus } = useInvestigationsStore();
  const router = useRouter();
  const sseRef = useRef<EventSource | null>(null);

  useEffect(() => { fetchOne(id); }, [id]);

  useEffect(() => {
    if (!current) return;
    if (current.status === "completed" || current.status === "failed") return;
    const sse = createSSEConnection(id);
    sseRef.current = sse;
    sse.onmessage = (e) => {
      try {
        const event: SSEEvent = JSON.parse(e.data);
        if (event.type === "validator_update" && event.data.validator_type) {
          updateValidator(id, event.data.validator_type, { status: event.data.status, findings: event.data.findings || null, confidence_score: event.data.confidence_score || null });
        }
        if (event.type === "completed") { setCurrentStatus("completed"); fetchOne(id); sse.close(); }
        if (event.type === "failed") { setCurrentStatus("failed"); sse.close(); }
      } catch {}
    };
    return () => { sse.close(); };
  }, [current?.id, current?.status]);

  if (!current) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh" }}>
        <span style={{ width: 24, height: 24, border: "2px solid rgba(37,99,235,0.3)", borderTopColor: "#2563EB", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite" }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  const validators = current.validators || [];
  const report = current.report;
  const isRunning = current.status === "running" || current.status === "pending";
  const completedValidators = validators.filter((v) => v.status === "completed").length;
  const totalValidators = validators.length || 13;
  const progress = validators.length > 0 ? (completedValidators / validators.length) * 100 : 0;

  const statusColor = current.status === "completed" ? "#10B981" : current.status === "running" ? "#2563EB" : current.status === "failed" ? "#EF4444" : "#64748B";
  const statusBg = current.status === "completed" ? "rgba(16,185,129,0.1)" : current.status === "running" ? "rgba(37,99,235,0.1)" : current.status === "failed" ? "rgba(239,68,68,0.1)" : "rgba(100,116,139,0.1)";

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "40px 24px", fontFamily: "system-ui,-apple-system,sans-serif", color: "#E2E8F0" }}>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 32 }}>
        <button onClick={() => router.push("/dashboard")} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: "#64748B", background: "none", border: "none", cursor: "pointer", padding: 0 }}>
          <ArrowLeft style={{ width: 15, height: 15 }} /> Back
        </button>
        <div style={{ width: 1, height: 16, background: "#1C2333" }} />
        <h1 style={{ fontSize: 20, fontWeight: 800, letterSpacing: "-0.01em" }}>{current.protocol_name}</h1>
        <span style={{ fontSize: 11, padding: "3px 10px", borderRadius: 6, background: statusBg, color: statusColor, fontFamily: "monospace", border: `1px solid ${statusColor}30` }}>
          {current.status}
        </span>

        {current.status === "completed" && report && (
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 32, fontWeight: 900, color: getTrustColor(report.scores.overall), lineHeight: 1 }}>
                {report.scores.overall.toFixed(1)}
              </div>
              <div style={{ fontSize: 11, color: "#64748B", marginTop: 2 }}>Trust Score / 100</div>
            </div>
            <div style={{ width: 1, height: 40, background: "#1C2333" }} />
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: getRiskColor(report.risk_level) }}>{getRiskLabel(report.risk_level)}</div>
              <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace", marginTop: 2 }}>{completedValidators} validators</div>
            </div>
          </div>
        )}
      </div>

      {/* Hero image strip */}
      <div style={{ borderRadius: 16, overflow: "hidden", height: 140, position: "relative", marginBottom: 28 }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&q=80"
          alt="blockchain verification"
          style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.4 }}
        />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(90deg, #080B14 0%, transparent 40%, #080B14 100%)" }} />
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", padding: "0 32px" }}>
          <div>
            <div style={{ fontSize: 12, color: "#64748B", fontFamily: "monospace", marginBottom: 4 }}>INVESTIGATION · {id.slice(0, 8).toUpperCase()}</div>
            <div style={{ fontSize: 18, fontWeight: 700 }}>{current.protocol_name}</div>
            <div style={{ fontSize: 12, color: "#64748B", marginTop: 2 }}>{formatDate(current.created_at)}</div>
          </div>
        </div>
      </div>

      {/* Progress bar */}
      {isRunning && (
        <div style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", padding: "20px 24px", marginBottom: 24 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#2563EB", display: "inline-block", boxShadow: "0 0 8px #2563EB" }} />
              <span style={{ fontSize: 13, fontWeight: 600 }}>Investigation Running</span>
              <span style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>GenLayer consensus active</span>
            </div>
            <span style={{ fontSize: 12, fontFamily: "monospace", color: "#64748B" }}>{completedValidators}/{totalValidators}</span>
          </div>
          <div style={{ height: 6, borderRadius: 99, background: "#1C2333", overflow: "hidden" }}>
            <div style={{ height: "100%", background: "linear-gradient(90deg, #2563EB, #10B981)", borderRadius: 99, width: `${progress}%`, transition: "width 0.5s ease" }} />
          </div>
          <div style={{ marginTop: 10, fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>
            {progress.toFixed(0)}% complete · Running 13 sources…
          </div>
        </div>
      )}

      {/* Main grid */}
      <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 20 }}>

        {/* Validators sidebar */}
        <div style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", overflow: "hidden", alignSelf: "start", position: "sticky", top: 84 }}>
          <div style={{ padding: "14px 18px", borderBottom: "1px solid #1C2333", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#94A3B8" }}>Validators</span>
            <span style={{ fontSize: 11, fontFamily: "monospace", color: "#64748B" }}>{completedValidators}/{totalValidators}</span>
          </div>
          <div style={{ maxHeight: "70vh", overflowY: "auto" }}>
            {(validators.length > 0
              ? validators
              : Object.keys(VALIDATOR_LABELS).map((t) => ({ validator_type: t as ValidatorType, status: "pending" as const, id: t, investigation_id: id, findings: null, confidence_score: null, sources: null, created_at: "" }))
            ).map((v) => {
              const Icon = VALIDATOR_ICONS[v.validator_type];
              const iconColor = v.status === "completed" ? "#10B981" : v.status === "running" ? "#2563EB" : v.status === "failed" ? "#EF4444" : "#2D3748";
              return (
                <div key={v.id || v.validator_type} style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 18px", borderBottom: "1px solid #0D1117" }}>
                  <Icon style={{ width: 14, height: 14, color: iconColor, flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 12, color: v.status === "pending" ? "#2D3748" : "#E2E8F0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {VALIDATOR_LABELS[v.validator_type]}
                    </div>
                    {v.confidence_score != null && (
                      <div style={{ fontSize: 10, fontFamily: "monospace", color: getTrustColor(v.confidence_score), marginTop: 2 }}>{v.confidence_score.toFixed(1)}%</div>
                    )}
                  </div>
                  {v.status === "completed" && <CheckCircle2 style={{ width: 13, height: 13, color: "#10B981", flexShrink: 0 }} />}
                  {v.status === "running" && <span style={{ width: 12, height: 12, border: "2px solid rgba(37,99,235,0.3)", borderTopColor: "#2563EB", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite", flexShrink: 0 }} />}
                  {v.status === "failed" && <XCircle style={{ width: 13, height: 13, color: "#EF4444", flexShrink: 0 }} />}
                  {v.status === "pending" && <Clock style={{ width: 13, height: 13, color: "#2D3748", flexShrink: 0 }} />}
                </div>
              );
            })}
          </div>
        </div>

        {/* Report area */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

          {report && (
            <>
              {/* Score grid */}
              <div style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", padding: "24px" }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 16 }}>Score Breakdown</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
                  {SCORE_CATEGORIES.map(({ key, label }) => {
                    const score = report.scores[key];
                    return (
                      <div key={key} style={{ borderRadius: 12, border: "1px solid #1C2333", background: "#080B14", padding: "12px 14px" }}>
                        <div style={{ fontSize: 11, color: "#64748B", marginBottom: 6 }}>{label}</div>
                        <div style={{ fontSize: 22, fontWeight: 800, color: getTrustColor(score), lineHeight: 1 }}>{score.toFixed(1)}</div>
                        <div style={{ marginTop: 8, height: 3, borderRadius: 99, background: "#1C2333", overflow: "hidden" }}>
                          <div style={{ height: "100%", borderRadius: 99, width: `${score}%`, backgroundColor: getTrustColor(score) }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Summary */}
              {report.summary && (
                <div style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", padding: "24px" }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 12 }}>Consensus Summary</div>
                  <p style={{ fontSize: 14, color: "#94A3B8", lineHeight: 1.8 }}>{report.summary}</p>
                </div>
              )}

              {/* Evidence */}
              <div style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", padding: "24px" }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 16 }}>Evidence Review</div>
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  {(report.verified_claims?.length ?? 0) > 0 && (
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, fontFamily: "monospace", color: "#10B981", marginBottom: 8 }}>
                        <CheckCircle2 style={{ width: 12, height: 12 }} /> VERIFIED ({report.verified_claims!.length})
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                        {report.verified_claims!.map((c, i) => (
                          <div key={i} style={{ borderRadius: 10, border: "1px solid rgba(16,185,129,0.2)", background: "rgba(16,185,129,0.05)", padding: "10px 14px" }}>
                            <div style={{ fontSize: 13, color: "#E2E8F0" }}>{typeof c === "string" ? c : c.claim}</div>
                            {typeof c !== "string" && c.source && <div style={{ fontSize: 11, color: "#64748B", marginTop: 4 }}>{c.source}</div>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {(report.disputed_claims?.length ?? 0) > 0 && (
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, fontFamily: "monospace", color: "#EF4444", marginBottom: 8 }}>
                        <XCircle style={{ width: 12, height: 12 }} /> DISPUTED ({report.disputed_claims!.length})
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                        {report.disputed_claims!.map((c, i) => (
                          <div key={i} style={{ borderRadius: 10, border: "1px solid rgba(239,68,68,0.2)", background: "rgba(239,68,68,0.05)", padding: "10px 14px" }}>
                            <div style={{ fontSize: 13, color: "#E2E8F0" }}>{typeof c === "string" ? c : c.claim}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {(report.unresolved_claims?.length ?? 0) > 0 && (
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, fontFamily: "monospace", color: "#F59E0B", marginBottom: 8 }}>
                        <AlertTriangle style={{ width: 12, height: 12 }} /> UNRESOLVED ({report.unresolved_claims!.length})
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                        {report.unresolved_claims!.map((c, i) => (
                          <div key={i} style={{ borderRadius: 10, border: "1px solid rgba(245,158,11,0.2)", background: "rgba(245,158,11,0.05)", padding: "10px 14px" }}>
                            <div style={{ fontSize: 13, color: "#E2E8F0" }}>{typeof c === "string" ? c : c.claim}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Recommendation */}
              {report.recommendation && (
                <div style={{ borderRadius: 16, border: "1px solid rgba(37,99,235,0.2)", background: "rgba(37,99,235,0.05)", padding: "24px" }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: "#60A5FA", marginBottom: 10 }}>Recommendation</div>
                  <p style={{ fontSize: 14, color: "#94A3B8", lineHeight: 1.8 }}>{report.recommendation}</p>
                  <div style={{ marginTop: 12, fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>
                    Report generated: {formatDate(report.created_at)}
                  </div>
                </div>
              )}
            </>
          )}

          {/* Live findings (running) */}
          {isRunning && validators.some((v) => v.findings) && (
            <div style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", padding: "24px" }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 16 }}>Live Findings</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {validators.filter((v) => v.findings).map((v) => (
                  <div key={v.id} style={{ borderRadius: 12, border: "1px solid #1C2333", background: "#080B14", padding: "14px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                      <CheckCircle2 style={{ width: 12, height: 12, color: "#10B981" }} />
                      <span style={{ fontSize: 11, fontWeight: 600, color: "#10B981" }}>{VALIDATOR_LABELS[v.validator_type]}</span>
                      {v.confidence_score != null && <span style={{ marginLeft: "auto", fontSize: 11, fontFamily: "monospace", color: "#64748B" }}>{v.confidence_score.toFixed(1)}%</span>}
                    </div>
                    <p style={{ fontSize: 12, color: "#64748B", lineHeight: 1.6 }}>{v.findings}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {current.status === "failed" && (
            <div style={{ borderRadius: 16, border: "1px solid rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.05)", padding: "40px", textAlign: "center" }}>
              <XCircle style={{ width: 40, height: 40, color: "#EF4444", margin: "0 auto 12px" }} />
              <div style={{ fontSize: 14, fontWeight: 600, color: "#EF4444" }}>Investigation Failed</div>
              <div style={{ fontSize: 12, color: "#64748B", marginTop: 4 }}>Please try again.</div>
            </div>
          )}

          {current.status === "pending" && validators.length === 0 && (
            <div style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", padding: "60px", textAlign: "center" }}>
              <span style={{ width: 32, height: 32, border: "2px solid rgba(37,99,235,0.3)", borderTopColor: "#2563EB", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite", marginBottom: 16 }} />
              <div style={{ fontSize: 13, color: "#64748B" }}>Initializing 13 sources…</div>
            </div>
          )}
        </div>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
