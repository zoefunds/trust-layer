"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useInvestigationsStore } from "@/stores/investigations";
import { formatDate, getTrustColor, getRiskColor, getRiskLabel } from "@/lib/utils";
import { Search, Clock, Shield, ArrowRight } from "lucide-react";

const STATUS_STYLES: Record<string, { bg: string; color: string; dot: string }> = {
  completed: { bg: "rgba(16,185,129,0.12)", color: "#10B981", dot: "#10B981" },
  running:   { bg: "rgba(37,99,235,0.12)",  color: "#2563EB", dot: "#2563EB" },
  failed:    { bg: "rgba(239,68,68,0.12)",  color: "#EF4444", dot: "#EF4444" },
  pending:   { bg: "rgba(100,116,139,0.12)", color: "#64748B", dot: "#64748B" },
};

export default function InvestigationsPage() {
  const { investigations, fetchAll, isLoading } = useInvestigationsStore();
  const router = useRouter();

  useEffect(() => { fetchAll(); }, []);

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "40px 24px" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: "#E2E8F0", letterSpacing: "-0.02em" }}>All Investigations</h1>
          <p style={{ fontSize: 13, color: "#64748B", marginTop: 4 }}>{investigations.length} total</p>
        </div>
        <button
          onClick={() => router.push("/dashboard")}
          style={{ display: "flex", alignItems: "center", gap: 8, background: "#2563EB", color: "#fff", padding: "10px 20px", borderRadius: 10, fontSize: 14, fontWeight: 600, border: "none", cursor: "pointer" }}
        >
          <Search style={{ width: 15, height: 15 }} /> New Investigation
        </button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: "80px 0" }}>
          <span style={{ width: 24, height: 24, border: "2px solid rgba(37,99,235,0.3)", borderTopColor: "#2563EB", borderRadius: "50%", animation: "spin 0.7s linear infinite", display: "inline-block" }} />
        </div>
      ) : investigations.length === 0 ? (
        <div style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", padding: "80px 24px", textAlign: "center" }}>
          <Shield style={{ width: 44, height: 44, color: "#1C2333", margin: "0 auto 16px" }} />
          <div style={{ fontSize: 15, color: "#64748B", marginBottom: 12 }}>No investigations yet.</div>
          <button
            onClick={() => router.push("/dashboard")}
            style={{ fontSize: 14, color: "#2563EB", background: "none", border: "none", cursor: "pointer" }}
          >
            Start your first investigation →
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {investigations.map((inv) => {
            const s = STATUS_STYLES[inv.status] || STATUS_STYLES.pending;
            return (
              <button
                key={inv.id}
                onClick={() => router.push(`/investigations/${inv.id}`)}
                style={{
                  width: "100%", textAlign: "left", borderRadius: 14,
                  border: "1px solid #1C2333", background: "#0D1117",
                  padding: "18px 22px", cursor: "pointer",
                  display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 14, minWidth: 0 }}>
                  <span style={{ width: 10, height: 10, borderRadius: "50%", background: s.dot, flexShrink: 0 }} />
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontWeight: 700, fontSize: 15, color: "#E2E8F0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {inv.protocol_name}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: "#64748B", marginTop: 3 }}>
                      <Clock style={{ width: 11, height: 11 }} /> {formatDate(inv.created_at)}
                    </div>
                  </div>
                  <span style={{ fontSize: 11, padding: "3px 10px", borderRadius: 6, background: s.bg, color: s.color, fontFamily: "monospace", flexShrink: 0 }}>
                    {inv.status}
                  </span>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 24, flexShrink: 0 }}>
                  {inv.report && (
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: 18, fontWeight: 800, color: getTrustColor(inv.report.scores.overall) }}>
                        {inv.report.scores.overall.toFixed(1)}
                      </div>
                      <div style={{ fontSize: 11, color: getRiskColor(inv.report.risk_level) }}>
                        {getRiskLabel(inv.report.risk_level)}
                      </div>
                    </div>
                  )}
                  <ArrowRight style={{ width: 15, height: 15, color: "#334155" }} />
                </div>
              </button>
            );
          })}
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
