"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useInvestigationsStore } from "@/stores/investigations";
import { formatDate, getTrustColor, getRiskColor, getRiskLabel } from "@/lib/utils";
import { Search, Clock, Shield, ArrowRight } from "lucide-react";

export default function InvestigationsPage() {
  const { investigations, fetchAll, isLoading } = useInvestigationsStore();
  const router = useRouter();

  useEffect(() => { fetchAll(); }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">All Investigations</h1>
          <p className="text-sm text-[#64748B] mt-1">{investigations.length} total</p>
        </div>
        <button
          onClick={() => router.push("/dashboard")}
          className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition-all"
        >
          <Search className="w-4 h-4" /> New Investigation
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <span className="w-6 h-6 border-2 border-[#2563EB]/30 border-t-[#2563EB] rounded-full animate-spin" />
        </div>
      ) : investigations.length === 0 ? (
        <div className="rounded-xl border border-[#1C2333] bg-[#0D1117] p-16 text-center">
          <Shield className="w-12 h-12 text-[#1C2333] mx-auto mb-4" />
          <div className="text-[#64748B]">No investigations yet.</div>
          <button
            onClick={() => router.push("/dashboard")}
            className="mt-4 text-sm text-[#2563EB] hover:text-[#60A5FA] transition-colors"
          >
            Start your first investigation →
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {investigations.map((inv) => (
            <button
              key={inv.id}
              onClick={() => router.push(`/investigations/${inv.id}`)}
              className="w-full text-left rounded-xl border border-[#1C2333] bg-[#0D1117] px-6 py-4 hover:border-[#2563EB]/30 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-2.5 h-2.5 rounded-full ${
                    inv.status === "completed" ? "bg-[#10B981]" :
                    inv.status === "running" ? "bg-[#2563EB] pulse-dot" :
                    inv.status === "failed" ? "bg-[#EF4444]" : "bg-[#64748B]"
                  }`} />
                  <div>
                    <div className="font-semibold text-sm text-white">{inv.protocol_name}</div>
                    <div className="flex items-center gap-1 text-xs text-[#64748B] mt-0.5">
                      <Clock className="w-3 h-3" /> {formatDate(inv.created_at)}
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full border font-mono ${
                    inv.status === "completed" ? "badge-verified" :
                    inv.status === "running" ? "border-[#2563EB]/30 text-[#2563EB] bg-[#2563EB]/10" :
                    inv.status === "failed" ? "badge-disputed" :
                    "border-[#64748B]/30 text-[#64748B]"
                  }`}>
                    {inv.status}
                  </span>
                </div>

                <div className="flex items-center gap-6">
                  {inv.report && (
                    <>
                      <div className="text-right">
                        <div className="text-lg font-bold" style={{ color: getTrustColor(inv.report.scores.overall) }}>
                          {inv.report.scores.overall.toFixed(1)}
                        </div>
                        <div className="text-xs" style={{ color: getRiskColor(inv.report.risk_level) }}>
                          {getRiskLabel(inv.report.risk_level)}
                        </div>
                      </div>
                    </>
                  )}
                  <ArrowRight className="w-4 h-4 text-[#64748B] group-hover:text-white transition-colors" />
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
