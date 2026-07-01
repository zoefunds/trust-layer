"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/auth";
import { Eye, EyeOff, ArrowRight, CheckCircle2, Copy, Shield, Wallet, Zap } from "lucide-react";

const INPUT: React.CSSProperties = {
  width: "100%", background: "#080B14", border: "1px solid #1C2333",
  borderRadius: 12, padding: "13px 16px", fontSize: 14,
  color: "#E2E8F0", outline: "none", boxSizing: "border-box",
};

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const { register, isLoading } = useAuthStore();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) { toast.error("Passwords do not match"); return; }
    if (password.length < 8) { toast.error("Password must be at least 8 characters"); return; }
    try {
      const { wallet_address } = await register(email, password);
      setWalletAddress(wallet_address);
      toast.success("Account created! Your wallet has been generated.");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Registration failed";
      toast.error(msg);
    }
  };

  const copyAddress = () => {
    if (walletAddress) { navigator.clipboard.writeText(walletAddress); toast.success("Wallet address copied"); }
  };

  if (walletAddress) {
    return (
      <div style={{ minHeight: "100vh", background: "#080B14", display: "flex", alignItems: "center", justifyContent: "center", padding: 24, fontFamily: "system-ui,-apple-system,sans-serif", color: "#E2E8F0" }}>
        <div style={{ width: "100%", maxWidth: 440 }}>
          <div style={{ borderRadius: 20, border: "1px solid rgba(16,185,129,0.3)", background: "#0D1117", padding: "40px 36px", textAlign: "center", boxShadow: "0 24px 64px rgba(0,0,0,0.5)" }}>

            <div style={{ width: 64, height: 64, borderRadius: "50%", background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.3)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px" }}>
              <CheckCircle2 style={{ width: 32, height: 32, color: "#10B981" }} />
            </div>

            <h2 style={{ fontSize: 24, fontWeight: 800, marginBottom: 8, letterSpacing: "-0.02em" }}>Account Created!</h2>
            <p style={{ fontSize: 14, color: "#64748B", marginBottom: 28, lineHeight: 1.6 }}>
              A blockchain wallet has been automatically generated and linked to your account.
            </p>

            <div style={{ borderRadius: 12, border: "1px solid #1C2333", background: "#080B14", padding: "16px", marginBottom: 16, textAlign: "left" }}>
              <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace", marginBottom: 8, letterSpacing: "0.08em" }}>YOUR WALLET ADDRESS</div>
              <div style={{ fontFamily: "monospace", fontSize: 12, color: "#10B981", wordBreak: "break-all", lineHeight: 1.6 }}>{walletAddress}</div>
              <button onClick={copyAddress} style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "#64748B", background: "none", border: "none", cursor: "pointer", padding: 0 }}>
                <Copy style={{ width: 12, height: 12 }} /> Copy address
              </button>
            </div>

            <div style={{ borderRadius: 12, border: "1px solid rgba(245,158,11,0.2)", background: "rgba(245,158,11,0.05)", padding: "14px 16px", marginBottom: 24, textAlign: "left" }}>
              <div style={{ fontSize: 12, color: "#F59E0B", fontWeight: 600, marginBottom: 4 }}>Important</div>
              <div style={{ fontSize: 12, color: "#94A3B8", lineHeight: 1.6 }}>
                Your wallet is encrypted with AES-256-GCM and stored securely. You can export your private key from account settings using your password.
              </div>
            </div>

            <button onClick={() => router.push("/dashboard")} style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, background: "#2563EB", color: "#fff", padding: "14px", borderRadius: 12, fontWeight: 700, fontSize: 15, border: "none", cursor: "pointer" }}>
              Go to Dashboard <ArrowRight style={{ width: 16, height: 16 }} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#080B14", display: "flex", color: "#E2E8F0", fontFamily: "system-ui,-apple-system,sans-serif" }}>

      {/* ── Left panel ── */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px 32px", position: "relative" }}>

        <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(28,35,51,0.3) 1px,transparent 1px),linear-gradient(90deg,rgba(28,35,51,0.3) 1px,transparent 1px)", backgroundSize: "40px 40px", zIndex: 0 }} />
        <div style={{ position: "absolute", top: "30%", left: "30%", width: 300, height: 300, background: "radial-gradient(circle,rgba(16,185,129,0.07) 0%,transparent 70%)", zIndex: 0 }} />

        <div style={{ position: "absolute", top: 28, left: 32, zIndex: 1 }}>
          <Link href="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
            <Image src="/icon.png" alt="TrustLayer" width={28} height={28} />
            <span style={{ fontWeight: 700, fontSize: 16, color: "#E2E8F0" }}>TrustLayer</span>
          </Link>
        </div>

        <div style={{ width: "100%", maxWidth: 420, position: "relative", zIndex: 1 }}>
          <div style={{ borderRadius: 20, border: "1px solid #1C2333", background: "#0D1117", padding: "40px 36px", boxShadow: "0 24px 64px rgba(0,0,0,0.5)" }}>

            <div style={{ width: 52, height: 52, borderRadius: 14, background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.25)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px" }}>
              <Wallet style={{ width: 24, height: 24, color: "#10B981" }} />
            </div>

            <h1 style={{ fontSize: 24, fontWeight: 800, textAlign: "center", marginBottom: 6, letterSpacing: "-0.02em" }}>Create Account</h1>
            <p style={{ fontSize: 14, color: "#64748B", textAlign: "center", marginBottom: 32, lineHeight: 1.6 }}>
              A blockchain wallet is automatically generated for you
            </p>

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", fontSize: 13, color: "#94A3B8", marginBottom: 8, fontWeight: 500 }}>Email address</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required style={INPUT} />
              </div>

              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", fontSize: 13, color: "#94A3B8", marginBottom: 8, fontWeight: 500 }}>Password</label>
                <div style={{ position: "relative" }}>
                  <input type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Min. 8 characters" required style={{ ...INPUT, paddingRight: 48 }} />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} style={{ position: "absolute", right: 14, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "#64748B", display: "flex" }}>
                    {showPassword ? <EyeOff style={{ width: 16, height: 16 }} /> : <Eye style={{ width: 16, height: 16 }} />}
                  </button>
                </div>
              </div>

              <div style={{ marginBottom: 24 }}>
                <label style={{ display: "block", fontSize: 13, color: "#94A3B8", marginBottom: 8, fontWeight: 500 }}>Confirm Password</label>
                <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="••••••••" required style={INPUT} />
              </div>

              <button type="submit" disabled={isLoading} style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, background: "#10B981", color: "#fff", padding: "14px", borderRadius: 12, fontWeight: 700, fontSize: 15, border: "none", cursor: isLoading ? "not-allowed" : "pointer", opacity: isLoading ? 0.7 : 1 }}>
                {isLoading
                  ? <span style={{ width: 18, height: 18, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite" }} />
                  : <><span>Create Account</span><ArrowRight style={{ width: 16, height: 16 }} /></>
                }
              </button>
            </form>

            <p style={{ textAlign: "center", fontSize: 14, color: "#64748B", marginTop: 24 }}>
              Already have an account?{" "}
              <Link href="/login" style={{ color: "#2563EB", fontWeight: 600, textDecoration: "none" }}>Sign in</Link>
            </p>
          </div>
        </div>
      </div>

      {/* ── Right panel ── */}
      <div style={{ width: 480, background: "#0A0E1A", borderLeft: "1px solid #1C2333", display: "flex", flexDirection: "column", padding: "60px 48px" }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <div style={{ borderRadius: 16, overflow: "hidden", marginBottom: 36, height: 220, position: "relative" }}>
          <img
            src="https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=800&q=80"
            alt="DeFi crypto trust verification"
            style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.65 }}
          />
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to top, #0A0E1A 0%, transparent 60%)" }} />
        </div>

        <h2 style={{ fontSize: 22, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 12 }}>
          Your Trust Intelligence Hub
        </h2>
        <p style={{ fontSize: 14, color: "#64748B", lineHeight: 1.75, marginBottom: 36 }}>
          Get instant, AI-consensus analysis of any Web3 protocol. Know before you invest — verify team credibility, smart contract security, tokenomics, and community trust in seconds.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {[
            { icon: Shield, label: "Wallet Auto-Generated", desc: "No MetaMask needed — we create one for you" },
            { icon: Zap, label: "Instant Investigations", desc: "Results in under 60 seconds across 13 sources" },
            { icon: CheckCircle2, label: "GenLayer Consensus", desc: "Decentralized agreement prevents single points of failure" },
          ].map(({ icon: Icon, label, desc }) => (
            <div key={label} style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <Icon style={{ width: 16, height: 16, color: "#10B981" }} />
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
