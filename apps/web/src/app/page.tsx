import Link from "next/link";
import Image from "next/image";
import { Shield, GitBranch, Zap, Globe, Lock, Users, ArrowRight, CheckCircle2, ChevronRight } from "lucide-react";

const VALIDATORS = [
  { label: "Identity Verification", icon: Shield, delay: "0ms" },
  { label: "Founder History", icon: Users, delay: "100ms" },
  { label: "GitHub Activity", icon: GitBranch, delay: "200ms" },
  { label: "On-chain Activity", icon: Globe, delay: "300ms" },
  { label: "Security Audit", icon: Lock, delay: "400ms" },
  { label: "Tokenomics", icon: Zap, delay: "500ms" },
];

const STATS = [
  { label: "Protocols Verified", value: "2,400+" },
  { label: "Validators Active", value: "13" },
  { label: "Avg. Consensus Time", value: "~90s" },
  { label: "Evidence Points", value: "180K+" },
];

const TRUSTED_BY = ["DeFi Protocols", "VC Funds", "CEX Platforms", "AI Agents", "Wallet Apps"];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#080B14] text-[#E2E8F0] overflow-hidden">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-[#1C2333] bg-[#080B14]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image src="/icon.png" alt="TrustLayer" width={32} height={32} />
            <span className="font-bold text-lg tracking-tight">TrustLayer</span>
            <span className="hidden sm:inline-block text-xs px-2 py-0.5 rounded-full border border-[#2563EB]/40 text-[#2563EB] font-mono">BETA</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-[#94A3B8] hover:text-white transition-colors px-4 py-2">
              Sign In
            </Link>
            <Link href="/register" className="text-sm bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-2 rounded-lg transition-colors font-medium">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-24 px-6 grid-bg">
        {/* Gradient orbs */}
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-[#2563EB]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-40 right-1/4 w-64 h-64 bg-[#10B981]/8 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-5xl mx-auto text-center relative">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#10B981]/30 bg-[#10B981]/10 text-[#10B981] text-xs font-mono mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] pulse-dot inline-block" />
            Powered by GenLayer Consensus
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-none mb-6">
            Verify Any Protocol.
            <br />
            <span className="text-[#2563EB]">Trust</span> the{" "}
            <span className="text-[#10B981]">Consensus.</span>
          </h1>

          <p className="text-lg sm:text-xl text-[#94A3B8] max-w-2xl mx-auto mb-10 leading-relaxed">
            TrustLayer runs 13 independent AI validators across on-chain data, GitHub,
            funding trails, and public records. GenLayer consensus reconciles findings
            into an evidence-backed trust score — in seconds.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Link
              href="/register"
              className="flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-8 py-3.5 rounded-xl font-semibold text-base transition-all glow-pulse"
            >
              Start Investigating <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/login"
              className="flex items-center gap-2 border border-[#1C2333] hover:border-[#2563EB]/50 text-[#94A3B8] hover:text-white px-8 py-3.5 rounded-xl font-medium text-base transition-all"
            >
              View a Sample Report <ChevronRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Terminal preview */}
          <div className="relative max-w-2xl mx-auto rounded-2xl border border-[#1C2333] bg-[#0D1117] overflow-hidden shadow-2xl">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-[#1C2333]">
              <span className="w-3 h-3 rounded-full bg-[#EF4444]/70" />
              <span className="w-3 h-3 rounded-full bg-[#F59E0B]/70" />
              <span className="w-3 h-3 rounded-full bg-[#10B981]/70" />
              <span className="ml-4 text-xs text-[#64748B] font-mono">trustlayer — investigation</span>
            </div>
            <div className="p-6 text-left font-mono text-sm">
              <div className="text-[#64748B]">$ investigate --protocol</div>
              <div className="text-[#E2E8F0] mt-1">
                <span className="text-[#10B981]">❯</span>{" "}
                <span className="text-[#2563EB]">Hyperlane</span>
              </div>
              <div className="mt-4 space-y-1.5 text-xs">
                {[
                  { label: "Identity Verification", score: 94, done: true },
                  { label: "GitHub Activity", score: 88, done: true },
                  { label: "Funding Verification", score: 91, done: true },
                  { label: "On-chain Activity", score: 85, done: true },
                  { label: "Security Audit", score: 79, done: false },
                ].map((v) => (
                  <div key={v.label} className="flex items-center gap-3">
                    {v.done ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#10B981] shrink-0" />
                    ) : (
                      <span className="w-3.5 h-3.5 shrink-0 flex items-center justify-center">
                        <span className="w-2 h-2 rounded-full bg-[#2563EB] pulse-dot inline-block" />
                      </span>
                    )}
                    <span className={v.done ? "text-[#64748B]" : "text-[#E2E8F0]"}>{v.label}</span>
                    {v.done && (
                      <span className="ml-auto text-[#10B981]">{v.score}/100</span>
                    )}
                  </div>
                ))}
              </div>
              <div className="mt-5 pt-4 border-t border-[#1C2333]">
                <div className="text-[#64748B] text-xs">Overall Trust Score</div>
                <div className="text-4xl font-bold text-[#10B981] mt-1">87.4</div>
                <div className="text-[#10B981]/70 text-xs mt-0.5">Low Risk · Consensus: 13/13 validators</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 border-y border-[#1C2333]">
        <div className="max-w-5xl mx-auto px-6 grid grid-cols-2 sm:grid-cols-4 gap-8">
          {STATS.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-3xl font-bold text-white mb-1">{s.value}</div>
              <div className="text-sm text-[#64748B]">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <div className="text-xs font-mono text-[#2563EB] mb-3 tracking-widest uppercase">Investigation Pipeline</div>
            <h2 className="text-3xl sm:text-4xl font-bold">How TrustLayer Works</h2>
            <p className="text-[#64748B] mt-4 max-w-xl mx-auto">
              Every investigation runs through a structured pipeline — evidence collection, independent validation, and consensus synthesis.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-6">
            {[
              {
                step: "01",
                title: "Evidence Collection",
                desc: "TrustLayer pulls data from GitHub, DefiLlama, CoinGecko, Etherscan, Solscan, and public records simultaneously.",
                color: "#2563EB",
              },
              {
                step: "02",
                title: "Independent Validators",
                desc: "13 specialized AI validators run in parallel — each analyzing a distinct domain without influencing the others.",
                color: "#10B981",
              },
              {
                step: "03",
                title: "Consensus Engine",
                desc: "GenLayer's consensus mechanism reconciles validator findings and produces confidence-scored, evidence-backed results.",
                color: "#F59E0B",
              },
            ].map((item) => (
              <div key={item.step} className="rounded-2xl border border-[#1C2333] bg-[#0D1117] p-6 hover:border-[#2563EB]/30 transition-colors">
                <div className="text-5xl font-bold mb-4" style={{ color: `${item.color}20` }}>
                  {item.step}
                </div>
                <h3 className="text-lg font-semibold mb-2" style={{ color: item.color }}>
                  {item.title}
                </h3>
                <p className="text-sm text-[#64748B] leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Validators */}
      <section className="py-24 px-6 bg-[#0D1117] border-y border-[#1C2333]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <div className="text-xs font-mono text-[#10B981] mb-3 tracking-widest uppercase">Validator Network</div>
            <h2 className="text-3xl sm:text-4xl font-bold">Every Angle. Every Layer.</h2>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {[
              "Identity Verification", "Founder History", "Funding Verification",
              "Investor Reputation", "GitHub Activity", "Documentation Analysis",
              "On-chain Activity", "Tokenomics", "Security Audit",
              "Community Health", "Ecosystem Integrations", "Product Verification",
              "Media & Public Claims",
            ].map((v, i) => (
              <div
                key={v}
                className="flex items-center gap-2.5 rounded-xl border border-[#1C2333] bg-[#080B14] px-4 py-3 hover:border-[#2563EB]/40 transition-colors"
              >
                <CheckCircle2 className="w-4 h-4 text-[#10B981] shrink-0" />
                <span className="text-sm text-[#94A3B8]">{v}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust infrastructure */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <div className="text-xs font-mono text-[#2563EB] mb-3 tracking-widest uppercase">Platform</div>
            <h2 className="text-3xl sm:text-4xl font-bold">
              Trust Infrastructure for Web3
            </h2>
            <p className="text-[#64748B] mt-4 max-w-xl mx-auto">
              TrustLayer is designed to be queried by other platforms — not just humans.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { label: "Wallets", desc: "Flag risky protocols before users interact." },
              { label: "Exchanges", desc: "Pre-listing due diligence at scale." },
              { label: "Launchpads", desc: "Screen projects before they go live." },
              { label: "DEX Aggregators", desc: "Warn on unverified token routes." },
              { label: "Venture Funds", desc: "Automate initial protocol screening." },
              { label: "AI Agents", desc: "Real-time trust data for autonomous agents." },
            ].map((item) => (
              <div key={item.label} className="rounded-xl border border-[#1C2333] bg-[#0D1117] p-5 hover:border-[#2563EB]/30 transition-colors">
                <div className="text-sm font-semibold text-white mb-1">{item.label}</div>
                <div className="text-xs text-[#64748B]">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <Image src="/icon.png" alt="TrustLayer" width={64} height={64} className="mx-auto mb-6" />
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Start Your First Investigation
          </h2>
          <p className="text-[#64748B] mb-8">
            Enter any protocol name. Get a full consensus report in under 2 minutes.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-10 py-4 rounded-xl font-semibold text-lg transition-all"
          >
            Create Free Account <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#1C2333] py-8 px-6">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-[#64748B]">
          <div className="flex items-center gap-2">
            <Image src="/icon.png" alt="TrustLayer" width={20} height={20} />
            <span>TrustLayer © 2025</span>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/login" className="hover:text-white transition-colors">Sign In</Link>
            <Link href="/register" className="hover:text-white transition-colors">Register</Link>
            <span className="text-[#1C2333]">|</span>
            <span className="font-mono text-xs">Powered by GenLayer</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
