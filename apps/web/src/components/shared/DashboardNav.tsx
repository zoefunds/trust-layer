"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/stores/auth";
import { truncateAddress, getInitials } from "@/lib/utils";
import { LayoutDashboard, Search, LogOut, Copy, ChevronDown } from "lucide-react";
import { toast } from "sonner";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/investigations", label: "Investigations", icon: Search },
];

export default function DashboardNav() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const copyWallet = () => {
    if (user?.wallet_address) {
      navigator.clipboard.writeText(user.wallet_address);
      toast.success("Wallet address copied");
    }
    setOpen(false);
  };

  return (
    <nav style={{
      position: "fixed", top: 0, left: 0, right: 0, zIndex: 50, height: 64,
      borderBottom: "1px solid #1C2333",
      background: "rgba(8,11,20,0.92)",
      backdropFilter: "blur(20px)",
    }}>
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px", height: "100%", display: "flex", alignItems: "center", justifyContent: "space-between" }}>

        {/* Left: Logo + Nav links */}
        <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
          <Link href="/dashboard" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
            <Image src="/icon.png" alt="TrustLayer" width={28} height={28} />
            <span style={{ fontWeight: 700, fontSize: 15, color: "#E2E8F0", letterSpacing: "-0.01em" }}>TrustLayer</span>
          </Link>

          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            {NAV_LINKS.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  style={{
                    display: "flex", alignItems: "center", gap: 7, padding: "7px 14px",
                    borderRadius: 9, fontSize: 13, fontWeight: active ? 600 : 500,
                    textDecoration: "none",
                    background: active ? "rgba(37,99,235,0.12)" : "transparent",
                    color: active ? "#60A5FA" : "#64748B",
                  }}
                >
                  <Icon style={{ width: 15, height: 15 }} />
                  <span>{label}</span>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Right: User menu */}
        {user && (
          <div ref={ref} style={{ position: "relative" }}>
            <button
              onClick={() => setOpen(!open)}
              style={{
                display: "flex", alignItems: "center", gap: 10,
                borderRadius: 10, border: "1px solid #1C2333", background: "#0D1117",
                padding: "7px 12px", cursor: "pointer",
              }}
            >
              <div style={{ width: 28, height: 28, borderRadius: "50%", background: "rgba(37,99,235,0.2)", border: "1px solid rgba(37,99,235,0.3)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: "#60A5FA" }}>
                {getInitials(user.email)}
              </div>
              <div style={{ textAlign: "left" }}>
                <div style={{ fontSize: 12, color: "#E2E8F0", fontWeight: 600 }}>{user.email.split("@")[0]}</div>
                <div style={{ fontSize: 10, color: "#64748B", fontFamily: "monospace" }}>{truncateAddress(user.wallet_address)}</div>
              </div>
              <ChevronDown style={{ width: 13, height: 13, color: "#64748B", marginLeft: 2 }} />
            </button>

            {open && (
              <div style={{
                position: "absolute", right: 0, top: "calc(100% + 8px)",
                width: 240, borderRadius: 12, border: "1px solid #1C2333",
                background: "#0D1117", boxShadow: "0 16px 48px rgba(0,0,0,0.5)",
                overflow: "hidden", zIndex: 100,
              }}>
                <div style={{ padding: "14px 16px", borderBottom: "1px solid #1C2333" }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "#E2E8F0" }}>{user.email}</div>
                  <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace", marginTop: 3 }}>{truncateAddress(user.wallet_address)}</div>
                </div>
                <button onClick={copyWallet} style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: "11px 16px", background: "none", border: "none", cursor: "pointer", color: "#94A3B8", fontSize: 13 }}>
                  <Copy style={{ width: 14, height: 14 }} /> Copy wallet address
                </button>
                <div style={{ borderTop: "1px solid #1C2333" }} />
                <button
                  onClick={() => { logout(); setOpen(false); }}
                  style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: "11px 16px", background: "none", border: "none", cursor: "pointer", color: "#EF4444", fontSize: 13 }}
                >
                  <LogOut style={{ width: 14, height: 14 }} /> Sign out
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
