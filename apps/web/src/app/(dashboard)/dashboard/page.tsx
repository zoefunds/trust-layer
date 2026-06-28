"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/auth";
import { useInvestigationsStore } from "@/stores/investigations";
import { getTrustColor, getRiskColor, getRiskLabel, formatDate } from "@/lib/utils";
import { Search, Zap, Shield, TrendingUp, Clock, ArrowRight } from "lucide-react";

const EXAMPLE_PROTOCOLS = [
  "Hyperlane", "Meteora", "Initia", "Monad", "Pump.fun",
  "Eigenlayer", "Scroll", "Optimism", "Arbitrum", "Uniswap",
];

const STATUS_STYLES: Record<string, { bg: string; color: string; dot: string }> = {
  completed: { bg: "rgba(16,185,129,0.12)", color: "#10B981", dot: "#10B981" },
  running:   { bg: "rgba(37,99,235,0.12)",  color: "#2563EB", dot: "#2563EB" },
  failed:    { bg: "rgba(239,68,68,0.12)",  color: "#EF4444", dot: "#EF4444" },
  pending:   { bg: "rgba(100,116,139,0.12)", color: "#64748B", dot: "#64748B" },
};

export default function DashboardPage() {
  const [query, setQuery] = useState("");
  const { user } = useAuthStore();
  const { investigations, fetchAll, create, isCreating } = useInvestigationsStore();
  const router = useRouter();

  useEffect(() => { fetchAll(); }, []);

  const handleInvestigate = async (protocol?: string) => {
    const name = protocol || query.trim();
    if (!name) { toast.error("Enter a protocol name"); return; }
    try {
      const inv = await create(name);
      router.push(`/investigations/${inv.id}`);
    } catch {
      toast.error("Failed to start investigation");
    }
  };

  const completedCount = investigations.filter((i) => i.status === "completed").length;
  const withReport = investigations.filter((i) => i.report);
  const avgScore = withReport.length
    ? withReport.reduce((a, i) => a + (i.report?.scores.overall ?? 0), 0) / withReport.length
    : 0;

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "40px 24px" }}>

      {/* Greeting */}
      <div style={{ marginBottom: 36 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, color: "#E2E8F0", letterSpacing: "-0.02em", marginBottom: 6 }}>
          {greeting},{" "}
          <span style={{ color: "#2563EB" }}>{user?.email.split("@")[0]}</span>
        </h1>
        <p style={{ fontSize: 14, color: "#64748B" }}>
          Investigate any Web3 protocol using consensus-backed AI validation.
        </p>
      </div>

      {/* New Investigation box */}
      <div style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", padding: "24px", marginBottom: 28, boxShadow: "0 0 32px rgba(37,99,235,0.08)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
          <Search style={{ width: 16, height: 16, color: "#2563EB" }} />
          <span style={{ fontSize: 14, fontWeight: 700, color: "#E2E8F0" }}>New Investigation</span>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleInvestigate()}
            placeholder="Enter protocol name (e.g. Hyperlane, Meteora, Initia...)"
            style={{
              flex: 1, background: "#080B14", border: "1px solid #1C2333",
              borderRadius: 12, padding: "12px 16px", fontSize: 14,
              color: "#E2E8F0", outline: "none",
            }}
          />
          <button
            onClick={() => handleInvestigate()}
            disabled={isCreating}
            style={{
              display: "flex", alignItems: "center", gap: 8,
              background: isCreating ? "#1D4ED8" : "#2563EB",
              color: "#fff", padding: "12px 24px", borderRadius: 12,
              fontWeight: 700, fontSize: 14, border: "none", cursor: isCreating ? "not-allowed" : "pointer",
              whiteSpace: "nowrap", opacity: isCreating ? 0.7 : 1,
            }}
          >
            {isCreating
              ? <span style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite" }} />
              : <><Zap style={{ width: 15, height: 15 }} /> Investigate</>
            }
          </button>
        </div>
        <div style={{ marginTop: 14, display: "flex", flexWrap: "wrap", gap: 8 }}>
          {EXAMPLE_PROTOCOLS.map((p) => (
            <button
              key={p}
              onClick={() => handleInvestigate(p)}
              style={{
                fontSize: 12, padding: "6px 12px", borderRadius: 8,
                border: "1px solid #1C2333", background: "#080B14",
                color: "#64748B", cursor: "pointer",
              }}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14, marginBottom: 28 }}>
        {[
          { label: "Total Investigations", value: investigations.length, icon: Search, color: "#2563EB" },
          { label: "Completed", value: completedCount, icon: Shield, color: "#10B981" },
          { label: "Avg Trust Score", value: avgScore > 0 ? avgScore.toFixed(1) : "—", icon: TrendingUp, color: "#F59E0B" },
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} style={{ borderRadius: 14, border: "1px solid #1C2333", background: "#0D1117", padding: "20px 22px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                <span style={{ fontSize: 12, color: "#64748B" }}>{stat.label}</span>
                <div style={{ width: 30, height: 30, borderRadius: 8, background: `${stat.color}18`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Icon style={{ width: 14, height: 14, color: stat.color }} />
                </div>
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>{stat.value}</div>
            </div>
          );
        })}
      </div>

      {/* Recent investigations */}
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: "#94A3B8", textTransform: "uppercase", letterSpacing: "0.05em" }}>Recent Investigations</h2>
          <button
            onClick={() => router.push("/investigations")}
            style={{ fontSize: 12, color: "#2563EB", background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}
          >
            View all <ArrowRight style={{ width: 12, height: 12 }} />
          </button>
        </div>

        {investigations.length === 0 ? (
          <div style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", padding: "60px 24px", textAlign: "center" }}>
            <Shield style={{ width: 36, height: 36, color: "#1C2333", margin: "0 auto 12px" }} />
            <div style={{ fontSize: 14, color: "#64748B" }}>No investigations yet.</div>
            <div style={{ fontSize: 12, color: "#334155", marginTop: 4 }}>Enter a protocol name above to get started.</div>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {investigations.slice(0, 8).map((inv) => {
              const s = STATUS_STYLES[inv.status] || STATUS_STYLES.pending;
              return (
                <button
                  key={inv.id}
                  onClick={() => router.push(`/investigations/${inv.id}`)}
                  style={{
                    width: "100%", textAlign: "left", borderRadius: 14,
                    border: "1px solid #1C2333", background: "#0D1117",
                    padding: "16px 20px", cursor: "pointer",
                    display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 12, minWidth: 0 }}>
                    <span style={{ width: 8, height: 8, borderRadius: "50%", background: s.dot, flexShrink: 0 }} />
                    <span style={{ fontWeight: 700, fontSize: 14, color: "#E2E8F0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {inv.protocol_name}
                    </span>
                    <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 6, background: s.bg, color: s.color, fontFamily: "monospace", flexShrink: 0 }}>
                      {inv.status}
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 20, flexShrink: 0 }}>
                    {inv.report && (
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: 15, fontWeight: 800, color: getTrustColor(inv.report.scores.overall) }}>
                          {inv.report.scores.overall.toFixed(1)}
                        </div>
                        <div style={{ fontSize: 10, color: getRiskColor(inv.report.risk_level) }}>
                          {getRiskLabel(inv.report.risk_level)}
                        </div>
                      </div>
                    )}
                    <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: "#475569" }}>
                      <Clock style={{ width: 12, height: 12 }} />
                      {formatDate(inv.created_at)}
                    </div>
                    <ArrowRight style={{ width: 14, height: 14, color: "#334155" }} />
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
