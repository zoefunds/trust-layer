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
      <div className="min-h-screen bg-[#080B14] flex items-center justify-center">
        <span className="w-6 h-6 border-2 border-[#2563EB]/30 border-t-[#2563EB] rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#080B14]">
      <DashboardNav />
      <main className="pt-16">{children}</main>
    </div>
  );
}
