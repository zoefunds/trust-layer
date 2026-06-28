import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { RiskLevel } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getTrustColor(score: number): string {
  if (score >= 75) return "#10B981";
  if (score >= 50) return "#F59E0B";
  if (score >= 25) return "#EF4444";
  return "#64748B";
}

export function getRiskColor(risk: RiskLevel): string {
  switch (risk) {
    case "low": return "#10B981";
    case "medium": return "#F59E0B";
    case "high": return "#EF4444";
    case "critical": return "#9333EA";
    default: return "#64748B";
  }
}

export function getRiskLabel(risk: RiskLevel): string {
  switch (risk) {
    case "low": return "Low Risk";
    case "medium": return "Medium Risk";
    case "high": return "High Risk";
    case "critical": return "Critical Risk";
  }
}

export function formatScore(score: number): string {
  return score.toFixed(1);
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function truncateAddress(address: string): string {
  if (!address) return "";
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

export function getInitials(email: string): string {
  return email.slice(0, 2).toUpperCase();
}
