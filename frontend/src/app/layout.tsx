import type { Metadata } from "next";
import { Inter_Tight } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const interTight = Inter_Tight({
  variable: "--font-inter-tight",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Fortress AI | Legal Audit",
  description: "Private Multi-Agent Legal Audit System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`dark ${interTight.variable} h-full antialiased`}
    >
      <body className="flex h-full min-h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-slate-950/50">
          {children}
        </main>
      </body>
    </html>
  );
}
