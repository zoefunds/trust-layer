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
  Briefcase, CheckCircle2, XCircle, Clock, AlertTriangle,
  ArrowLeft
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

export default function InvestigationPage() {
  const { id } = useParams<{ id: string }>();
  const { current, fetchOne, updateValidator, setCurrentStatus } = useInvestigationsStore();
  const router = useRouter();
  const sseRef = useRef<EventSource | null>(null);

  useEffect(() => {
    fetchOne(id);
  }, [id]);

  useEffect(() => {
    if (!current) return;
    if (current.status === "completed" || current.status === "failed") return;

    const sse = createSSEConnection(id);
    sseRef.current = sse;

    sse.onmessage = (e) => {
      try {
        const event: SSEEvent = JSON.parse(e.data);
        if (event.type === "validator_update" && event.data.validator_type) {
          updateValidator(id, event.data.validator_type, {
            status: event.data.status,
            findings: event.data.findings || null,
            confidence_score: event.data.confidence_score || null,
          });
        }
        if (event.type === "completed") {
          setCurrentStatus("completed");
          fetchOne(id);
          sse.close();
        }
        if (event.type === "failed") {
          setCurrentStatus("failed");
          sse.close();
        }
      } catch {}
    };

    return () => { sse.close(); };
  }, [current?.id, current?.status]);

  if (!current) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <span className="w-6 h-6 border-2 border-[#2563EB]/30 border-t-[#2563EB] rounded-full animate-spin" />
      </div>
    );
  }

  const validators = current.validators || [];
  const report = current.report;
  const isRunning = current.status === "running" || current.status === "pending";
  const completedValidators = validators.filter((v) => v.status === "completed").length;
  const progress = validators.length > 0 ? (completedValidators / validators.length) * 100 : 0;

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

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={() => router.push("/dashboard")}
          className="flex items-center gap-2 text-sm text-[#64748B] hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <div className="h-4 w-px bg-[#1C2333]" />
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold">{current.protocol_name}</h1>
          <span className={`text-xs px-2 py-0.5 rounded-full border font-mono ${
            current.status === "completed" ? "badge-verified" :
            current.status === "running" ? "border-[#2563EB]/30 text-[#2563EB] bg-[#2563EB]/10" :
            current.status === "failed" ? "badge-disputed" :
            "border-[#64748B]/30 text-[#64748B]"
          }`}>
            {current.status}
          </span>
        </div>
        {current.status === "completed" && report && (
          <div className="ml-auto flex items-center gap-3">
            <div className="text-right">
              <div className="text-3xl font-bold" style={{ color: getTrustColor(report.scores.overall) }}>
                {report.scores.overall.toFixed(1)}
              </div>
              <div className="text-xs text-[#64748B]">Trust Score</div>
            </div>
            <div className="h-10 w-px bg-[#1C2333]" />
            <div>
              <div className="text-sm font-semibold" style={{ color: getRiskColor(report.risk_level) }}>
                {getRiskLabel(report.risk_level)}
              </div>
              <div className="text-xs text-[#64748B] font-mono">{validators.filter(v => v.status === "completed").length} validators</div>
            </div>
          </div>
        )}
      </div>

      {/* Progress bar */}
      {isRunning && (
        <div className="rounded-2xl border border-[#1C2333] bg-[#0D1117] p-6 mb-6 overflow-hidden relative">
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            <div className="scan-line absolute left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-[#2563EB]/30 to-transparent" />
          </div>
          <div className="flex items-center justify-between mb-3 relative">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#2563EB] pulse-dot inline-block" />
              <span className="text-sm font-semibold">Investigation Running</span>
              <span className="text-xs text-[#64748B] font-mono">GenLayer consensus active</span>
            </div>
            <span className="text-xs font-mono text-[#64748B]">{completedValidators}/{validators.length}</span>
          </div>
          <div className="h-1.5 rounded-full bg-[#1C2333] overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-[#2563EB] to-[#10B981] transition-all duration-500 rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="mt-3 text-xs text-[#64748B] font-mono">
            {progress.toFixed(0)}% complete · Running 13 independent validators…
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Validators list */}
        <div className="lg:col-span-1">
          <div className="rounded-2xl border border-[#1C2333] bg-[#0D1117] overflow-hidden sticky top-20">
            <div className="px-5 py-4 border-b border-[#1C2333] flex items-center justify-between">
              <h2 className="text-sm font-semibold text-[#94A3B8]">Validators</h2>
              <span className="text-xs font-mono text-[#64748B]">{completedValidators}/{validators.length || 13}</span>
            </div>
            <div className="divide-y divide-[#1C2333] max-h-[70vh] overflow-y-auto">
              {(validators.length > 0 ? validators : Object.keys(VALIDATOR_LABELS).map(t => ({ validator_type: t as ValidatorType, status: "pending", id: t, investigation_id: id, findings: null, confidence_score: null, sources: null, created_at: "" }))).map((v) => {
                const Icon = VALIDATOR_ICONS[v.validator_type];
                const label = VALIDATOR_LABELS[v.validator_type];
                return (
                  <div key={v.id || v.validator_type} className="flex items-center gap-3 px-5 py-3 hover:bg-[#080B14]/50 transition-colors">
                    <Icon className={`w-4 h-4 shrink-0 ${
                      v.status === "completed" ? "text-[#10B981]" :
                      v.status === "running" ? "text-[#2563EB]" :
                      v.status === "failed" ? "text-[#EF4444]" :
                      "text-[#1C2333]"
                    }`} />
                    <div className="flex-1 min-w-0">
                      <div className={`text-xs truncate ${v.status === "pending" ? "text-[#1C2333]" : "text-[#E2E8F0]"}`}>{label}</div>
                      {v.confidence_score != null && (
                        <div className="text-xs font-mono mt-0.5" style={{ color: getTrustColor(v.confidence_score) }}>
                          {v.confidence_score.toFixed(1)}%
                        </div>
                      )}
                    </div>
                    {v.status === "completed" && <CheckCircle2 className="w-4 h-4 text-[#10B981] shrink-0" />}
                    {v.status === "running" && <span className="w-3.5 h-3.5 border-2 border-[#2563EB]/30 border-t-[#2563EB] rounded-full animate-spin inline-block shrink-0" />}
                    {v.status === "failed" && <XCircle className="w-4 h-4 text-[#EF4444] shrink-0" />}
                    {v.status === "pending" && <Clock className="w-4 h-4 text-[#1C2333] shrink-0" />}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Report */}
        <div className="lg:col-span-2 space-y-6">
          {report && (
            <>
              {/* Score grid */}
              <div className="rounded-2xl border border-[#1C2333] bg-[#0D1117] p-6">
                <h2 className="text-sm font-semibold text-[#94A3B8] mb-4">Score Breakdown</h2>
                <div className="grid grid-cols-3 gap-3">
                  {SCORE_CATEGORIES.map(({ key, label }) => {
                    const score = report.scores[key];
                    return (
                      <div key={key} className="rounded-xl border border-[#1C2333] bg-[#080B14] p-3">
                        <div className="text-xs text-[#64748B] mb-1.5">{label}</div>
                        <div className="text-2xl font-bold" style={{ color: getTrustColor(score) }}>
                          {score.toFixed(1)}
                        </div>
                        <div className="mt-2 h-1 rounded-full bg-[#1C2333] overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: `${score}%`, backgroundColor: getTrustColor(score) }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Summary */}
              {report.summary && (
                <div className="rounded-2xl border border-[#1C2333] bg-[#0D1117] p-6">
                  <h2 className="text-sm font-semibold text-[#94A3B8] mb-3">Consensus Summary</h2>
                  <p className="text-sm text-[#94A3B8] leading-relaxed">{report.summary}</p>
                </div>
              )}

              {/* Claims evidence */}
              <div className="rounded-2xl border border-[#1C2333] bg-[#0D1117] p-6">
                <h2 className="text-sm font-semibold text-[#94A3B8] mb-4">Evidence Review</h2>
                <div className="space-y-4">
                  {(report.verified_claims?.length ?? 0) > 0 && (
                    <div>
                      <div className="text-xs font-mono text-[#10B981] mb-2 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5" /> VERIFIED ({report.verified_claims!.length})
                      </div>
                      <div className="space-y-2">
                        {report.verified_claims!.map((c, i) => (
                          <div key={i} className="rounded-lg border border-[#10B981]/20 bg-[#10B981]/5 p-3">
                            <div className="text-sm text-[#E2E8F0]">{typeof c === "string" ? c : c.claim}</div>
                            {typeof c !== "string" && c.source && <div className="text-xs text-[#64748B] mt-1">{c.source}</div>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {(report.disputed_claims?.length ?? 0) > 0 && (
                    <div>
                      <div className="text-xs font-mono text-[#EF4444] mb-2 flex items-center gap-1.5">
                        <XCircle className="w-3.5 h-3.5" /> DISPUTED ({report.disputed_claims!.length})
                      </div>
                      <div className="space-y-2">
                        {report.disputed_claims!.map((c, i) => (
                          <div key={i} className="rounded-lg border border-[#EF4444]/20 bg-[#EF4444]/5 p-3">
                            <div className="text-sm text-[#E2E8F0]">{typeof c === "string" ? c : c.claim}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {(report.unresolved_claims?.length ?? 0) > 0 && (
                    <div>
                      <div className="text-xs font-mono text-[#F59E0B] mb-2 flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5" /> UNRESOLVED ({report.unresolved_claims!.length})
                      </div>
                      <div className="space-y-2">
                        {report.unresolved_claims!.map((c, i) => (
                          <div key={i} className="rounded-lg border border-[#F59E0B]/20 bg-[#F59E0B]/5 p-3">
                            <div className="text-sm text-[#E2E8F0]">{typeof c === "string" ? c : c.claim}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Recommendation */}
              {report.recommendation && (
                <div className="rounded-2xl border border-[#2563EB]/20 bg-[#2563EB]/5 p-6">
                  <h2 className="text-sm font-semibold text-[#60A5FA] mb-2">Recommendation</h2>
                  <p className="text-sm text-[#94A3B8] leading-relaxed">{report.recommendation}</p>
                  <div className="mt-3 text-xs text-[#64748B] font-mono">
                    Report generated: {formatDate(report.created_at)}
                  </div>
                </div>
              )}
            </>
          )}

          {/* Live validator findings (running state) */}
          {isRunning && validators.some((v) => v.findings) && (
            <div className="rounded-2xl border border-[#1C2333] bg-[#0D1117] p-6">
              <h2 className="text-sm font-semibold text-[#94A3B8] mb-4">Live Findings</h2>
              <div className="space-y-3">
                {validators.filter((v) => v.findings).map((v) => (
                  <div key={v.id} className="rounded-xl border border-[#1C2333] bg-[#080B14] p-4 fade-in-up">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#10B981]" />
                      <span className="text-xs font-semibold text-[#10B981]">{VALIDATOR_LABELS[v.validator_type]}</span>
                      {v.confidence_score != null && (
                        <span className="ml-auto text-xs font-mono text-[#64748B]">{v.confidence_score.toFixed(1)}%</span>
                      )}
                    </div>
                    <p className="text-xs text-[#64748B] leading-relaxed">{v.findings}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {current.status === "failed" && (
            <div className="rounded-2xl border border-[#EF4444]/30 bg-[#EF4444]/5 p-8 text-center">
              <XCircle className="w-10 h-10 text-[#EF4444] mx-auto mb-3" />
              <div className="text-sm font-semibold text-[#EF4444]">Investigation Failed</div>
              <div className="text-xs text-[#64748B] mt-1">Please try again.</div>
            </div>
          )}

          {current.status === "pending" && validators.length === 0 && (
            <div className="rounded-2xl border border-[#1C2333] bg-[#0D1117] p-12 text-center">
              <span className="w-8 h-8 border-2 border-[#2563EB]/30 border-t-[#2563EB] rounded-full animate-spin inline-block mb-4" />
              <div className="text-sm text-[#64748B]">Initializing validators…</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
