"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/stores/auth";
import { truncateAddress, getInitials } from "@/lib/utils";
import { LayoutDashboard, Search, LogOut, Copy, Wallet } from "lucide-react";
import { toast } from "sonner";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/investigations", label: "Investigations", icon: Search },
];

export default function DashboardNav() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  const copyWallet = () => {
    if (user?.wallet_address) {
      navigator.clipboard.writeText(user.wallet_address);
      toast.success("Wallet address copied");
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-[#1C2333] bg-[#080B14]/90 backdrop-blur-xl h-16">
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <Image src="/icon.png" alt="TrustLayer" width={28} height={28} />
            <span className="font-bold text-sm tracking-tight hidden sm:block">TrustLayer</span>
          </Link>
          <div className="flex items-center gap-1">
            {NAV_LINKS.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                  pathname === href
                    ? "bg-[#2563EB]/10 text-[#60A5FA]"
                    : "text-[#64748B] hover:text-white hover:bg-[#1C2333]/50"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:block">{label}</span>
              </Link>
            ))}
          </div>
        </div>

        {user && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2.5 rounded-xl border border-[#1C2333] bg-[#0D1117] px-3 py-2 hover:border-[#2563EB]/40 transition-colors">
                <div className="w-7 h-7 rounded-full bg-[#2563EB]/20 border border-[#2563EB]/30 flex items-center justify-center text-xs font-bold text-[#60A5FA]">
                  {getInitials(user.email)}
                </div>
                <div className="hidden sm:block text-left">
                  <div className="text-xs text-[#E2E8F0] font-medium">{user.email.split("@")[0]}</div>
                  <div className="text-xs text-[#64748B] font-mono">{truncateAddress(user.wallet_address)}</div>
                </div>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-64 bg-[#0D1117] border-[#1C2333] text-[#E2E8F0]">
              <div className="px-3 py-2">
                <div className="text-sm font-medium">{user.email}</div>
                <div className="text-xs text-[#64748B] font-mono mt-0.5">{truncateAddress(user.wallet_address)}</div>
              </div>
              <DropdownMenuSeparator className="bg-[#1C2333]" />
              <DropdownMenuItem onClick={copyWallet} className="gap-2 text-[#94A3B8] hover:text-white cursor-pointer">
                <Copy className="w-4 h-4" /> Copy wallet address
              </DropdownMenuItem>
              <DropdownMenuItem asChild className="gap-2 text-[#94A3B8] hover:text-white cursor-pointer">
                <Link href="/dashboard?export=wallet">
                  <Wallet className="w-4 h-4" /> Export private key
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-[#1C2333]" />
              <DropdownMenuItem onClick={logout} className="gap-2 text-[#EF4444] hover:text-[#EF4444] cursor-pointer">
                <LogOut className="w-4 h-4" /> Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </nav>
  );
}
