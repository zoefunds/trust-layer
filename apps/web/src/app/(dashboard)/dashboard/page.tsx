"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/auth";
import { useInvestigationsStore } from "@/stores/investigations";
import { formatDate, getTrustColor, getRiskColor, getRiskLabel } from "@/lib/utils";
import { Search, Zap, Shield, TrendingUp, Clock, ArrowRight, AlertTriangle } from "lucide-react";
import { useEffect } from "react";

const EXAMPLE_PROTOCOLS = [
  "Hyperlane", "Meteora", "Initia", "Monad", "Pump.fun",
  "Eigenlayer", "Scroll", "Optimism", "Arbitrum", "Uniswap",
];

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
  const avgScore = investigations
    .filter((i) => i.report)
    .reduce((acc, i) => acc + (i.report?.scores.overall || 0), 0) /
    (investigations.filter((i) => i.report).length || 1);

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      {/* Greeting */}
      <div className="mb-10">
        <h1 className="text-2xl font-bold mb-1">
          Good {new Date().getHours() < 12 ? "morning" : "afternoon"},{" "}
          <span className="text-[#2563EB]">{user?.email.split("@")[0]}</span>
        </h1>
        <p className="text-[#64748B] text-sm">Investigate any Web3 protocol using consensus-backed AI validation.</p>
      </div>

      {/* Search / Investigate box */}
      <div className="rounded-2xl border border-[#1C2333] bg-[#0D1117] p-6 mb-8 glow-pulse">
        <div className="flex items-center gap-2 mb-3">
          <Search className="w-4 h-4 text-[#2563EB]" />
          <span className="text-sm font-semibold text-[#E2E8F0]">New Investigation</span>
        </div>
        <div className="flex gap-3">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleInvestigate()}
            placeholder="Enter protocol name (e.g. Hyperlane, Meteora, Initia...)"
            className="flex-1 bg-[#080B14] border border-[#1C2333] rounded-xl px-4 py-3 text-sm text-[#E2E8F0] placeholder-[#64748B] focus:outline-none focus:border-[#2563EB]/50 focus:ring-1 focus:ring-[#2563EB]/20 transition-all"
          />
          <button
            onClick={() => handleInvestigate()}
            disabled={isCreating}
            className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] disabled:opacity-50 text-white px-6 py-3 rounded-xl font-semibold text-sm transition-all whitespace-nowrap"
          >
            {isCreating ? (
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <><Zap className="w-4 h-4" /> Investigate</>
            )}
          </button>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          {EXAMPLE_PROTOCOLS.map((p) => (
            <button
              key={p}
              onClick={() => handleInvestigate(p)}
              className="text-xs px-3 py-1.5 rounded-lg border border-[#1C2333] bg-[#080B14] text-[#64748B] hover:text-white hover:border-[#2563EB]/40 transition-all"
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: "Total Investigations", value: investigations.length, icon: Search, color: "#2563EB" },
          { label: "Completed", value: completedCount, icon: Shield, color: "#10B981" },
          { label: "Avg Trust Score", value: avgScore > 0 ? avgScore.toFixed(1) : "—", icon: TrendingUp, color: "#F59E0B" },
        ].map((stat) => (
          <div key={stat.label} className="rounded-xl border border-[#1C2333] bg-[#0D1117] p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-[#64748B]">{stat.label}</span>
              <stat.icon className="w-4 h-4" style={{ color: stat.color }} />
            </div>
            <div className="text-2xl font-bold text-white">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Recent investigations */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-[#94A3B8]">Recent Investigations</h2>
          <button
            onClick={() => router.push("/investigations")}
            className="text-xs text-[#2563EB] hover:text-[#60A5FA] flex items-center gap-1 transition-colors"
          >
            View all <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        {investigations.length === 0 ? (
          <div className="rounded-xl border border-[#1C2333] bg-[#0D1117] p-10 text-center">
            <Shield className="w-10 h-10 text-[#1C2333] mx-auto mb-3" />
            <div className="text-sm text-[#64748B]">No investigations yet.</div>
            <div className="text-xs text-[#1C2333] mt-1">Enter a protocol name above to get started.</div>
          </div>
        ) : (
          <div className="space-y-3">
            {investigations.slice(0, 5).map((inv) => (
              <button
                key={inv.id}
                onClick={() => router.push(`/investigations/${inv.id}`)}
                className="w-full text-left rounded-xl border border-[#1C2333] bg-[#0D1117] px-5 py-4 hover:border-[#2563EB]/30 transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      inv.status === "completed" ? "bg-[#10B981]" :
                      inv.status === "running" ? "bg-[#2563EB] pulse-dot" :
                      inv.status === "failed" ? "bg-[#EF4444]" :
                      "bg-[#64748B]"
                    }`} />
                    <span className="font-semibold text-sm text-white">{inv.protocol_name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-mono ${
                      inv.status === "completed" ? "badge-verified" :
                      inv.status === "running" ? "border-[#2563EB]/30 text-[#2563EB] bg-[#2563EB]/10" :
                      inv.status === "failed" ? "badge-disputed" :
                      "border-[#64748B]/30 text-[#64748B] bg-[#64748B]/10"
                    }`}>
                      {inv.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    {inv.report && (
                      <div className="text-right">
                        <div className="text-sm font-bold" style={{ color: getTrustColor(inv.report.scores.overall) }}>
                          {inv.report.scores.overall.toFixed(1)}
                        </div>
                        <div className="text-xs" style={{ color: getRiskColor(inv.report.risk_level) }}>
                          {getRiskLabel(inv.report.risk_level)}
                        </div>
                      </div>
                    )}
                    <div className="flex items-center gap-1 text-xs text-[#64748B]">
                      <Clock className="w-3 h-3" />
                      {formatDate(inv.created_at)}
                    </div>
                    <ArrowRight className="w-4 h-4 text-[#64748B] group-hover:text-white transition-colors" />
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
