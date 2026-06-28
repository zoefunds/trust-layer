"use client";
import Link from "next/link";
import Image from "next/image";
import { Shield, GitBranch, Zap, Globe, Lock, Users, ArrowRight, CheckCircle2, ChevronRight, Activity, Coins, Eye, FileText, BarChart3, Newspaper } from "lucide-react";

const VALIDATORS = [
  { label: "Identity Verification", icon: Shield },
  { label: "Founder History", icon: Users },
  { label: "Funding Verification", icon: Coins },
  { label: "Investor Reputation", icon: BarChart3 },
  { label: "GitHub Activity", icon: GitBranch },
  { label: "Documentation", icon: FileText },
  { label: "On-chain Activity", icon: Activity },
  { label: "Tokenomics", icon: Zap },
  { label: "Security Audit", icon: Lock },
  { label: "Community Health", icon: Users },
  { label: "Ecosystem Integrations", icon: Globe },
  { label: "Product Verification", icon: Eye },
  { label: "Media & Public Claims", icon: Newspaper },
];

const STATS = [
  { label: "Protocols Verified", value: "2,400+" },
  { label: "Validators Active", value: "13" },
  { label: "Avg. Consensus Time", value: "~90s" },
  { label: "Evidence Points", value: "180K+" },
];

export default function LandingPage() {
  return (
    <div style={{ background: "#080B14", color: "#E2E8F0", minHeight: "100vh", fontFamily: "system-ui, -apple-system, sans-serif" }}>

      {/* ── Nav ───────────────────────────────────────────── */}
      <nav style={{
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 50,
        borderBottom: "1px solid #1C2333",
        background: "rgba(8,11,20,0.85)",
        backdropFilter: "blur(20px)",
      }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Image src="/icon.png" alt="TrustLayer" width={30} height={30} />
            <span style={{ fontWeight: 700, fontSize: 18, letterSpacing: "-0.02em" }}>TrustLayer</span>
            <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 999, border: "1px solid rgba(37,99,235,0.4)", color: "#2563EB", fontFamily: "monospace", marginLeft: 4 }}>BETA</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Link href="/login" style={{ fontSize: 14, color: "#94A3B8", padding: "8px 16px", textDecoration: "none", transition: "color 0.2s" }}>
              Sign In
            </Link>
            <Link href="/register" style={{ fontSize: 14, background: "#2563EB", color: "#fff", padding: "8px 18px", borderRadius: 8, textDecoration: "none", fontWeight: 600 }}>
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────────────── */}
      <section style={{ paddingTop: 140, paddingBottom: 100, paddingLeft: 24, paddingRight: 24, position: "relative", overflow: "hidden" }}>
        {/* grid background */}
        <div style={{
          position: "absolute", inset: 0, zIndex: 0,
          backgroundImage: "linear-gradient(rgba(28,35,51,0.35) 1px, transparent 1px), linear-gradient(90deg, rgba(28,35,51,0.35) 1px, transparent 1px)",
          backgroundSize: "44px 44px",
        }} />
        {/* glow orbs */}
        <div style={{ position: "absolute", top: 80, left: "20%", width: 400, height: 400, background: "radial-gradient(circle, rgba(37,99,235,0.12) 0%, transparent 70%)", zIndex: 0, pointerEvents: "none" }} />
        <div style={{ position: "absolute", top: 160, right: "18%", width: 280, height: 280, background: "radial-gradient(circle, rgba(16,185,129,0.10) 0%, transparent 70%)", zIndex: 0, pointerEvents: "none" }} />

        <div style={{ maxWidth: 860, margin: "0 auto", textAlign: "center", position: "relative", zIndex: 1 }}>
          {/* badge */}
          <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px", borderRadius: 999, border: "1px solid rgba(16,185,129,0.3)", background: "rgba(16,185,129,0.08)", color: "#10B981", fontSize: 12, fontFamily: "monospace", marginBottom: 32 }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#10B981", display: "inline-block", animation: "pulse 1.8s ease-in-out infinite" }} />
            Powered by GenLayer Consensus
          </div>

          <h1 style={{ fontSize: "clamp(2.4rem, 6vw, 4.5rem)", fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.03em", marginBottom: 24 }}>
            Verify Any Protocol.
            <br />
            <span style={{ color: "#2563EB" }}>Trust</span>{" "}
            the{" "}
            <span style={{ color: "#10B981" }}>Consensus.</span>
          </h1>

          <p style={{ fontSize: "clamp(1rem, 2vw, 1.2rem)", color: "#94A3B8", maxWidth: 600, margin: "0 auto 40px", lineHeight: 1.7 }}>
            TrustLayer runs 13 independent AI validators across on-chain data, GitHub,
            funding trails, and public records. GenLayer consensus reconciles findings
            into an evidence-backed trust score — in seconds.
          </p>

          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "center", gap: 12, marginBottom: 64 }}>
            <Link href="/register" style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "#2563EB", color: "#fff", padding: "14px 32px", borderRadius: 12, fontWeight: 700, fontSize: 16, textDecoration: "none", boxShadow: "0 0 24px rgba(37,99,235,0.35)" }}>
              Start Investigating <ArrowRight style={{ width: 18, height: 18 }} />
            </Link>
            <Link href="/login" style={{ display: "inline-flex", alignItems: "center", gap: 8, border: "1px solid #1C2333", color: "#94A3B8", padding: "14px 28px", borderRadius: 12, fontWeight: 600, fontSize: 15, textDecoration: "none" }}>
              View a Sample Report <ChevronRight style={{ width: 16, height: 16 }} />
            </Link>
          </div>

          {/* Terminal */}
          <div style={{ maxWidth: 560, margin: "0 auto", borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", overflow: "hidden", boxShadow: "0 32px 80px rgba(0,0,0,0.6)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "12px 16px", borderBottom: "1px solid #1C2333", background: "#080B14" }}>
              <span style={{ width: 12, height: 12, borderRadius: "50%", background: "#EF4444", opacity: 0.7 }} />
              <span style={{ width: 12, height: 12, borderRadius: "50%", background: "#F59E0B", opacity: 0.7 }} />
              <span style={{ width: 12, height: 12, borderRadius: "50%", background: "#10B981", opacity: 0.7 }} />
              <span style={{ marginLeft: 12, fontSize: 11, color: "#475569", fontFamily: "monospace" }}>trustlayer — investigation</span>
            </div>
            <div style={{ padding: "20px 24px", fontFamily: "monospace", fontSize: 13, textAlign: "left" }}>
              <div style={{ color: "#475569" }}>$ investigate --protocol</div>
              <div style={{ marginTop: 4, color: "#E2E8F0" }}>
                <span style={{ color: "#10B981" }}>❯</span>{" "}
                <span style={{ color: "#2563EB", fontWeight: 700 }}>Hyperlane</span>
              </div>
              <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 10 }}>
                {[
                  { label: "Identity Verification", score: 94, done: true },
                  { label: "GitHub Activity", score: 88, done: true },
                  { label: "Funding Verification", score: 91, done: true },
                  { label: "On-chain Activity", score: 85, done: true },
                  { label: "Security Audit", done: false },
                ].map((v) => (
                  <div key={v.label} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    {v.done
                      ? <CheckCircle2 style={{ width: 14, height: 14, color: "#10B981", flexShrink: 0 }} />
                      : <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#2563EB", flexShrink: 0, display: "inline-block" }} />
                    }
                    <span style={{ color: v.done ? "#64748B" : "#E2E8F0", flex: 1 }}>{v.label}</span>
                    {v.done && <span style={{ color: "#10B981", marginLeft: "auto" }}>{v.score}/100</span>}
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 20, paddingTop: 16, borderTop: "1px solid #1C2333" }}>
                <div style={{ fontSize: 11, color: "#64748B" }}>Overall Trust Score</div>
                <div style={{ fontSize: 40, fontWeight: 800, color: "#10B981", lineHeight: 1.1, marginTop: 4 }}>87.4</div>
                <div style={{ fontSize: 11, color: "rgba(16,185,129,0.65)", marginTop: 4 }}>Low Risk · Consensus: 13/13 validators</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats ─────────────────────────────────────────── */}
      <section style={{ borderTop: "1px solid #1C2333", borderBottom: "1px solid #1C2333", background: "#0A0E1A" }}>
        <div style={{ maxWidth: 900, margin: "0 auto", padding: "56px 24px", display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 0 }}>
          {STATS.map((s, i) => (
            <div key={s.label} style={{ textAlign: "center", padding: "0 24px", borderRight: i < 3 ? "1px solid #1C2333" : "none" }}>
              <div style={{ fontSize: 36, fontWeight: 800, color: "#fff", letterSpacing: "-0.03em" }}>{s.value}</div>
              <div style={{ fontSize: 13, color: "#64748B", marginTop: 6 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────── */}
      <section style={{ padding: "96px 24px" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 60 }}>
            <div style={{ fontSize: 11, fontFamily: "monospace", color: "#2563EB", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 12 }}>Investigation Pipeline</div>
            <h2 style={{ fontSize: "clamp(1.8rem, 4vw, 2.6rem)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 16 }}>How TrustLayer Works</h2>
            <p style={{ fontSize: 15, color: "#64748B", maxWidth: 480, margin: "0 auto", lineHeight: 1.7 }}>
              Every investigation runs through a structured pipeline — evidence collection, independent validation, and consensus synthesis.
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
            {[
              { step: "01", title: "Evidence Collection", desc: "TrustLayer pulls data from GitHub, DefiLlama, CoinGecko, Etherscan, and public records simultaneously.", accent: "#2563EB" },
              { step: "02", title: "Independent Validators", desc: "13 specialized AI validators run in parallel — each analyzing a distinct domain without influencing others.", accent: "#10B981" },
              { step: "03", title: "Consensus Engine", desc: "GenLayer's consensus mechanism reconciles validator findings into confidence-scored, evidence-backed results.", accent: "#F59E0B" },
            ].map((item) => (
              <div key={item.step} style={{ borderRadius: 16, border: "1px solid #1C2333", background: "#0D1117", padding: "28px 28px", position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", top: -10, right: 12, fontSize: 72, fontWeight: 900, color: item.accent, opacity: 0.07, lineHeight: 1, pointerEvents: "none", userSelect: "none" }}>{item.step}</div>
                <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 40, height: 40, borderRadius: 10, background: `${item.accent}18`, border: `1px solid ${item.accent}30`, marginBottom: 20 }}>
                  <span style={{ fontSize: 16, fontWeight: 800, color: item.accent, fontFamily: "monospace" }}>{item.step}</span>
                </div>
                <h3 style={{ fontSize: 17, fontWeight: 700, color: item.accent, marginBottom: 10 }}>{item.title}</h3>
                <p style={{ fontSize: 14, color: "#64748B", lineHeight: 1.7 }}>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Validators ────────────────────────────────────── */}
      <section style={{ padding: "80px 24px", background: "#0A0E1A", borderTop: "1px solid #1C2333", borderBottom: "1px solid #1C2333" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 48 }}>
            <div style={{ fontSize: 11, fontFamily: "monospace", color: "#10B981", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 12 }}>Validator Network</div>
            <h2 style={{ fontSize: "clamp(1.8rem, 4vw, 2.6rem)", fontWeight: 800, letterSpacing: "-0.02em" }}>Every Angle. Every Layer.</h2>
            <p style={{ fontSize: 15, color: "#64748B", marginTop: 12 }}>13 specialized validators. One unified consensus score.</p>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 12 }}>
            {VALIDATORS.map((v) => {
              const Icon = v.icon;
              return (
                <div key={v.label} style={{ display: "flex", alignItems: "center", gap: 12, borderRadius: 12, border: "1px solid #1C2333", background: "#080B14", padding: "14px 16px" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 32, height: 32, borderRadius: 8, background: "rgba(16,185,129,0.1)", flexShrink: 0 }}>
                    <Icon style={{ width: 15, height: 15, color: "#10B981" }} />
                  </div>
                  <span style={{ fontSize: 13, color: "#94A3B8", fontWeight: 500 }}>{v.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Trust infrastructure ──────────────────────────── */}
      <section style={{ padding: "96px 24px" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 56 }}>
            <div style={{ fontSize: 11, fontFamily: "monospace", color: "#2563EB", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 12 }}>Platform</div>
            <h2 style={{ fontSize: "clamp(1.8rem, 4vw, 2.6rem)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 14 }}>Trust Infrastructure for Web3</h2>
            <p style={{ fontSize: 15, color: "#64748B", maxWidth: 460, margin: "0 auto", lineHeight: 1.7 }}>
              TrustLayer is designed to be queried by other platforms — not just humans.
            </p>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
            {[
              { label: "Wallets", desc: "Flag risky protocols before users interact.", icon: "🔒" },
              { label: "Exchanges", desc: "Pre-listing due diligence at scale.", icon: "📊" },
              { label: "Launchpads", desc: "Screen projects before they go live.", icon: "🚀" },
              { label: "DEX Aggregators", desc: "Warn on unverified token routes.", icon: "⚡" },
              { label: "Venture Funds", desc: "Automate initial protocol screening.", icon: "💼" },
              { label: "AI Agents", desc: "Real-time trust data for autonomous agents.", icon: "🤖" },
            ].map((item) => (
              <div key={item.label} style={{ borderRadius: 14, border: "1px solid #1C2333", background: "#0D1117", padding: "22px 22px", display: "flex", gap: 16, alignItems: "flex-start" }}>
                <div style={{ fontSize: 24, lineHeight: 1, flexShrink: 0, marginTop: 2 }}>{item.icon}</div>
                <div>
                  <div style={{ fontSize: 15, fontWeight: 700, color: "#E2E8F0", marginBottom: 6 }}>{item.label}</div>
                  <div style={{ fontSize: 13, color: "#64748B", lineHeight: 1.6 }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────── */}
      <section style={{ padding: "80px 24px" }}>
        <div style={{ maxWidth: 640, margin: "0 auto", textAlign: "center", borderRadius: 24, border: "1px solid #1C2333", background: "linear-gradient(135deg, #0D1117 0%, #0F1A2E 100%)", padding: "64px 40px", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", width: 400, height: 300, background: "radial-gradient(ellipse, rgba(37,99,235,0.12) 0%, transparent 70%)", pointerEvents: "none" }} />
          <Image src="/icon.png" alt="TrustLayer" width={56} height={56} style={{ margin: "0 auto 24px", display: "block" }} />
          <h2 style={{ fontSize: "clamp(1.6rem, 3.5vw, 2.2rem)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 14 }}>
            Start Your First Investigation
          </h2>
          <p style={{ fontSize: 15, color: "#64748B", lineHeight: 1.7, marginBottom: 32 }}>
            Enter any protocol name. Get a full consensus report in under 2 minutes.
          </p>
          <Link href="/register" style={{ display: "inline-flex", alignItems: "center", gap: 10, background: "#2563EB", color: "#fff", padding: "15px 36px", borderRadius: 12, fontWeight: 700, fontSize: 16, textDecoration: "none", boxShadow: "0 0 32px rgba(37,99,235,0.4)" }}>
            Create Free Account <ArrowRight style={{ width: 18, height: 18 }} />
          </Link>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────── */}
      <footer style={{ borderTop: "1px solid #1C2333", padding: "28px 24px" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Image src="/icon.png" alt="TrustLayer" width={20} height={20} />
            <span style={{ fontSize: 13, color: "#64748B" }}>TrustLayer © 2025</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 24, fontSize: 13, color: "#64748B" }}>
            <Link href="/login" style={{ color: "#64748B", textDecoration: "none" }}>Sign In</Link>
            <Link href="/register" style={{ color: "#64748B", textDecoration: "none" }}>Register</Link>
            <span style={{ fontFamily: "monospace", fontSize: 11, color: "#475569" }}>Powered by GenLayer</span>
          </div>
        </div>
      </footer>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(0.85); }
        }
        @media (max-width: 700px) {
          .stats-grid { grid-template-columns: repeat(2, 1fr) !important; }
          .steps-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
