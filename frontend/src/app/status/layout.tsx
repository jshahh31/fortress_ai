import { ShieldCheck } from "lucide-react";
import Link from "next/link";

export default function StatusLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen">
      {/* Minimal header */}
      <header className="h-14 border-b border-white/10 bg-surface/60 backdrop-blur-xl">
        <div className="max-w-5xl mx-auto h-full px-6 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-md bg-primary/10 border border-primary/20 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4 text-primary" />
            </div>
            <span className="font-bold text-sm tracking-wide text-secondary">FORTRESS AI</span>
            <span className="text-[10px] font-mono text-muted-foreground ml-2 bg-white/5 px-2 py-0.5 rounded border border-white/10">STATUS</span>
          </Link>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}
