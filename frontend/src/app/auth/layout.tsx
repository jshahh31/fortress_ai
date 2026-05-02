import { ShieldCheck } from "lucide-react";
import Link from "next/link";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-[#0a0e1a] -z-20" />
      <div className="absolute top-[-200px] right-[-200px] w-[600px] h-[600px] bg-[#1B3A5C]/30 rounded-full blur-[180px] -z-10" />
      <div className="absolute bottom-[-200px] left-[-200px] w-[500px] h-[500px] bg-primary/15 rounded-full blur-[160px] -z-10" />

      <div className="w-full max-w-md">
        {/* Logo */}
        <Link href="/" className="flex items-center justify-center gap-2.5 mb-10">
          <div className="w-9 h-9 rounded-lg bg-[#1B3A5C]/30 border border-[#1B3A5C]/40 flex items-center justify-center shadow-[0_0_15px_rgba(27,58,92,0.3)]">
            <ShieldCheck className="w-5 h-5 text-blue-300" />
          </div>
          <span className="font-bold text-xl tracking-wide text-secondary">FORTRESS AI</span>
        </Link>

        {children}
      </div>
    </div>
  );
}
