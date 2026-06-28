import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TrustLayer — Web3 Consensus Verification",
  description: "Multi-validator AI consensus platform for Web3 due diligence. Investigate any protocol with evidence-backed trust scores powered by GenLayer.",
  icons: { icon: "/icon.png", apple: "/icon.png" },
  openGraph: {
    title: "TrustLayer — Web3 Consensus Verification",
    description: "Multi-validator AI consensus for Web3 due diligence.",
    images: ["/icon.png"],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        {children}
        <Toaster
          theme="dark"
          toastOptions={{
            style: { background: "#0D1117", border: "1px solid #1C2333", color: "#E2E8F0" },
          }}
        />
      </body>
    </html>
  );
}
