"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/auth";
import { Eye, EyeOff, ArrowRight, Shield, Lock, Activity } from "lucide-react";

const INPUT = {
  width: "100%", background: "#080B14", border: "1px solid #1C2333",
  borderRadius: 12, padding: "13px 16px", fontSize: 14,
  color: "#E2E8F0", outline: "none", boxSizing: "border-box" as const,
};

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const { login, isLoading } = useAuthStore();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      toast.success("Signed in successfully");
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Invalid credentials";
      toast.error(msg);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#080B14", display: "flex", color: "#E2E8F0", fontFamily: "system-ui,-apple-system,sans-serif" }}>

      {/* ── Left panel ── */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px 32px", position: "relative" }}>

        {/* Background grid */}
        <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(28,35,51,0.3) 1px,transparent 1px),linear-gradient(90deg,rgba(28,35,51,0.3) 1px,transparent 1px)", backgroundSize: "40px 40px", zIndex: 0 }} />
        <div style={{ position: "absolute", top: "30%", left: "30%", width: 300, height: 300, background: "radial-gradient(circle,rgba(37,99,235,0.1) 0%,transparent 70%)", zIndex: 0 }} />

        {/* Logo */}
        <div style={{ position: "absolute", top: 28, left: 32, display: "flex", alignItems: "center", gap: 10, zIndex: 1 }}>
          <Link href="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
            <Image src="/icon.png" alt="TrustLayer" width={28} height={28} />
            <span style={{ fontWeight: 700, fontSize: 16, color: "#E2E8F0" }}>TrustLayer</span>
          </Link>
        </div>

        {/* Card */}
        <div style={{ width: "100%", maxWidth: 420, position: "relative", zIndex: 1 }}>
          <div style={{ borderRadius: 20, border: "1px solid #1C2333", background: "#0D1117", padding: "40px 36px", boxShadow: "0 24px 64px rgba(0,0,0,0.5)" }}>

            {/* Icon */}
            <div style={{ width: 52, height: 52, borderRadius: 14, background: "rgba(37,99,235,0.12)", border: "1px solid rgba(37,99,235,0.25)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px" }}>
              <Shield style={{ width: 24, height: 24, color: "#2563EB" }} />
            </div>

            <h1 style={{ fontSize: 24, fontWeight: 800, textAlign: "center", marginBottom: 6, letterSpacing: "-0.02em" }}>Welcome back</h1>
            <p style={{ fontSize: 14, color: "#64748B", textAlign: "center", marginBottom: 32 }}>Sign in to your TrustLayer account</p>

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", fontSize: 13, color: "#94A3B8", marginBottom: 8, fontWeight: 500 }}>Email address</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required style={INPUT} />
              </div>

              <div style={{ marginBottom: 24 }}>
                <label style={{ display: "block", fontSize: 13, color: "#94A3B8", marginBottom: 8, fontWeight: 500 }}>Password</label>
                <div style={{ position: "relative" }}>
                  <input type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required style={{ ...INPUT, paddingRight: 48 }} />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} style={{ position: "absolute", right: 14, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "#64748B", display: "flex" }}>
                    {showPassword ? <EyeOff style={{ width: 16, height: 16 }} /> : <Eye style={{ width: 16, height: 16 }} />}
                  </button>
                </div>
              </div>

              <button type="submit" disabled={isLoading} style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, background: "#2563EB", color: "#fff", padding: "14px", borderRadius: 12, fontWeight: 700, fontSize: 15, border: "none", cursor: isLoading ? "not-allowed" : "pointer", opacity: isLoading ? 0.7 : 1 }}>
                {isLoading
                  ? <span style={{ width: 18, height: 18, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite" }} />
                  : <><span>Sign In</span><ArrowRight style={{ width: 16, height: 16 }} /></>
                }
              </button>
            </form>

            <p style={{ textAlign: "center", fontSize: 14, color: "#64748B", marginTop: 24 }}>
              No account?{" "}
              <Link href="/register" style={{ color: "#2563EB", fontWeight: 600, textDecoration: "none" }}>Create one free</Link>
            </p>
          </div>
        </div>
      </div>

      {/* ── Right panel (feature showcase) ── */}
      <div style={{ width: 480, background: "#0A0E1A", borderLeft: "1px solid #1C2333", display: "flex", flexDirection: "column", padding: "60px 48px" }}>
        {/* Unsplash: blockchain/web3 */}
        <div style={{ borderRadius: 16, overflow: "hidden", marginBottom: 36, height: 220, position: "relative" }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="https://images.unsplash.com/photo-1639762681057-408e52192e55?w=800&q=80"
            alt="Web3 blockchain network"
            style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.7 }}
          />
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to top, #0A0E1A 0%, transparent 60%)" }} />
        </div>

        <h2 style={{ fontSize: 22, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 12 }}>
          AI-Powered Web3 Due Diligence
        </h2>
        <p style={{ fontSize: 14, color: "#64748B", lineHeight: 1.75, marginBottom: 36 }}>
          TrustLayer deploys 5 independent AI validators to analyze every angle of a Web3 protocol — from on-chain activity to team credibility — and returns a consensus-backed trust score.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {[
            { icon: Shield, label: "5 Independent Validators", desc: "Each analyzing a different signal layer" },
            { icon: Activity, label: "Real-time Consensus", desc: "GenLayer reconciles all findings live" },
            { icon: Lock, label: "Encrypted Wallet", desc: "Auto-generated, AES-256-GCM secured" },
          ].map(({ icon: Icon, label, desc }) => (
            <div key={label} style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(37,99,235,0.12)", border: "1px solid rgba(37,99,235,0.2)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <Icon style={{ width: 16, height: 16, color: "#2563EB" }} />
              </div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#E2E8F0", marginBottom: 2 }}>{label}</div>
                <div style={{ fontSize: 12, color: "#64748B" }}>{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
