"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Eye, EyeOff, Loader2, CheckCircle } from "lucide-react";

export default function ResetPasswordPage() {
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const match = password === confirm;
  const canSubmit = password.length >= 8 && confirm && match && !loading;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setSuccess(true);
      setTimeout(() => router.push("/auth/login"), 2000);
    }, 1200);
  };

  if (success) {
    return (
      <div className="glass-panel rounded-2xl p-8 border-[#1B3A5C]/30 text-center">
        <div className="w-14 h-14 rounded-2xl bg-success/10 border border-success/20 flex items-center justify-center mx-auto mb-5">
          <CheckCircle className="w-7 h-7 text-success" />
        </div>
        <h1 className="text-2xl font-extrabold text-secondary mb-2">Password reset!</h1>
        <p className="text-sm text-muted-foreground">Redirecting you to sign in...</p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl p-8 border-[#1B3A5C]/30">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-extrabold text-secondary mb-1">Reset password</h1>
        <p className="text-sm text-muted-foreground">Enter your new password below</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider block mb-1.5">New Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type={showPass ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Min. 8 characters" required
              className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-12 py-3 text-sm text-secondary placeholder:text-muted-foreground focus:outline-none focus:border-[#1B3A5C]/60 transition-all" />
            <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-secondary transition-colors">
              {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <div>
          <label className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider block mb-1.5">Confirm Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type={showPass ? "text" : "password"} value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="Repeat password" required
              className={`w-full bg-white/5 border rounded-xl pl-10 pr-4 py-3 text-sm text-secondary placeholder:text-muted-foreground focus:outline-none transition-all ${
                confirm && !match ? "border-danger/50" : "border-white/10 focus:border-[#1B3A5C]/60"
              }`} />
          </div>
          {confirm && !match && <p className="text-[10px] text-danger mt-1 font-medium">Passwords do not match</p>}
        </div>

        <button type="submit" disabled={!canSubmit}
          className="w-full bg-[#1B3A5C] hover:bg-[#234a72] text-white font-bold text-sm py-3 rounded-xl border border-[#1B3A5C]/60 shadow-lg shadow-[#1B3A5C]/20 transition-all disabled:opacity-40 flex items-center justify-center gap-2">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
          {loading ? "Resetting..." : "Reset Password"}
        </button>
      </form>
    </div>
  );
}
