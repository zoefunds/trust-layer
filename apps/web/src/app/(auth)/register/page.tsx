"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/auth";
import { Eye, EyeOff, ArrowRight, CheckCircle2, Copy, Download } from "lucide-react";

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
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }
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
    if (walletAddress) {
      navigator.clipboard.writeText(walletAddress);
      toast.success("Wallet address copied");
    }
  };

  if (walletAddress) {
    return (
      <div className="min-h-screen bg-[#080B14] grid-bg flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="rounded-2xl border border-[#10B981]/30 bg-[#0D1117] p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-[#10B981]/10 border border-[#10B981]/30 flex items-center justify-center mx-auto mb-5">
              <CheckCircle2 className="w-8 h-8 text-[#10B981]" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Account Created</h2>
            <p className="text-[#64748B] text-sm mb-6">
              A blockchain wallet has been automatically generated and linked to your account.
            </p>

            <div className="rounded-xl border border-[#1C2333] bg-[#080B14] p-4 mb-4 text-left">
              <div className="text-xs text-[#64748B] mb-2 font-mono">YOUR WALLET ADDRESS</div>
              <div className="font-mono text-xs text-[#10B981] break-all">{walletAddress}</div>
              <button
                onClick={copyAddress}
                className="mt-3 flex items-center gap-1.5 text-xs text-[#64748B] hover:text-white transition-colors"
              >
                <Copy className="w-3 h-3" /> Copy address
              </button>
            </div>

            <div className="rounded-xl border border-[#F59E0B]/20 bg-[#F59E0B]/5 p-4 mb-6 text-left">
              <div className="text-xs text-[#F59E0B] font-semibold mb-1">Important</div>
              <div className="text-xs text-[#94A3B8]">
                Your wallet is encrypted and stored securely. You can export your private key any time from your account settings using your password.
              </div>
            </div>

            <button
              onClick={() => router.push("/dashboard")}
              className="w-full flex items-center justify-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white py-3 rounded-xl font-semibold transition-all"
            >
              Go to Dashboard <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#080B14] grid-bg flex items-center justify-center px-4">
      <div className="absolute top-8 left-8">
        <Link href="/" className="flex items-center gap-2 text-[#64748B] hover:text-white transition-colors">
          <Image src="/icon.png" alt="TrustLayer" width={24} height={24} />
          <span className="font-semibold text-sm">TrustLayer</span>
        </Link>
      </div>

      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-[#1C2333] bg-[#0D1117] p-8">
          <div className="flex items-center justify-center mb-6">
            <Image src="/icon.png" alt="TrustLayer" width={48} height={48} />
          </div>
          <h1 className="text-2xl font-bold text-center mb-1">Create Account</h1>
          <p className="text-[#64748B] text-sm text-center mb-8">
            A blockchain wallet is automatically generated for you
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-[#94A3B8] mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="w-full bg-[#080B14] border border-[#1C2333] rounded-xl px-4 py-3 text-sm text-[#E2E8F0] placeholder-[#64748B] focus:outline-none focus:border-[#2563EB]/50 focus:ring-1 focus:ring-[#2563EB]/30 transition-all"
              />
            </div>

            <div>
              <label className="block text-sm text-[#94A3B8] mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min. 8 characters"
                  required
                  className="w-full bg-[#080B14] border border-[#1C2333] rounded-xl px-4 py-3 pr-12 text-sm text-[#E2E8F0] placeholder-[#64748B] focus:outline-none focus:border-[#2563EB]/50 focus:ring-1 focus:ring-[#2563EB]/30 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#64748B] hover:text-[#94A3B8] transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm text-[#94A3B8] mb-1.5">Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full bg-[#080B14] border border-[#1C2333] rounded-xl px-4 py-3 text-sm text-[#E2E8F0] placeholder-[#64748B] focus:outline-none focus:border-[#2563EB]/50 focus:ring-1 focus:ring-[#2563EB]/30 transition-all"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 bg-[#2563EB] hover:bg-[#1D4ED8] disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 rounded-xl font-semibold transition-all mt-2"
            >
              {isLoading ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>Create Account <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-[#64748B] mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-[#2563EB] hover:text-[#60A5FA] transition-colors font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
