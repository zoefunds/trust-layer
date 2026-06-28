"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth";
import DashboardNav from "@/components/shared/DashboardNav";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, fetchMe } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    fetchMe().catch(() => router.push("/login"));
  }, []);

  if (!isAuthenticated) {
    return (
      <div style={{ minHeight: "100vh", background: "#080B14", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <span style={{ width: 24, height: 24, border: "2px solid rgba(37,99,235,0.3)", borderTopColor: "#2563EB", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite" }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#080B14", color: "#E2E8F0" }}>
      <DashboardNav />
      <main style={{ paddingTop: 64 }}>{children}</main>
    </div>
  );
}
