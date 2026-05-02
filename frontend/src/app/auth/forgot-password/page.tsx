"use client";

import { useState } from "react";
import Link from "next/link";
import { Mail, Loader2, CheckCircle } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setSent(true);
    }, 1200);
  };

  if (sent) {
    return (
      <div className="glass-panel rounded-2xl p-8 border-[#1B3A5C]/30 text-center">
        <div className="w-14 h-14 rounded-2xl bg-success/10 border border-success/20 flex items-center justify-center mx-auto mb-5">
          <CheckCircle className="w-7 h-7 text-success" />
        </div>
        <h1 className="text-2xl font-extrabold text-secondary mb-2">Check your email</h1>
        <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
          We&apos;ve sent a password reset link to <span className="text-secondary font-medium">{email}</span>.
          Please check your inbox and follow the instructions.
        </p>
        <Link href="/auth/login" className="text-sm text-blue-300 hover:text-blue-200 font-semibold transition-colors">
          ← Back to Sign In
        </Link>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl p-8 border-[#1B3A5C]/30">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-extrabold text-secondary mb-1">Forgot password?</h1>
        <p className="text-sm text-muted-foreground">Enter your email and we&apos;ll send you a reset link</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider block mb-1.5">Email</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required
              className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-sm text-secondary placeholder:text-muted-foreground focus:outline-none focus:border-[#1B3A5C]/60 transition-all" />
          </div>
        </div>

        <button type="submit" disabled={loading || !email}
          className="w-full bg-[#1B3A5C] hover:bg-[#234a72] text-white font-bold text-sm py-3 rounded-xl border border-[#1B3A5C]/60 shadow-lg shadow-[#1B3A5C]/20 transition-all disabled:opacity-40 flex items-center justify-center gap-2">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
          {loading ? "Sending..." : "Send Reset Link"}
        </button>
      </form>

      <p className="text-center text-xs text-muted-foreground mt-6">
        <Link href="/auth/login" className="text-blue-300 hover:text-blue-200 font-semibold transition-colors">
          ← Back to Sign In
        </Link>
      </p>
    </div>
  );
}
