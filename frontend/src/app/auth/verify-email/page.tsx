"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle, Loader2 } from "lucide-react";

export default function VerifyEmailPage() {
  const [countdown, setCountdown] = useState(5);
  const router = useRouter();

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          router.push("/auth/login");
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [router]);

  return (
    <div className="glass-panel rounded-2xl p-8 border-[#1B3A5C]/30 text-center">
      <div className="w-16 h-16 rounded-2xl bg-success/10 border border-success/20 flex items-center justify-center mx-auto mb-6 shadow-[0_0_20px_rgba(7,202,107,0.2)]">
        <CheckCircle className="w-8 h-8 text-success" />
      </div>
      <h1 className="text-2xl font-extrabold text-secondary mb-2">Email verified!</h1>
      <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
        Your account has been verified successfully. You can now sign in and start analyzing contracts.
      </p>
      <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="w-4 h-4 animate-spin text-blue-300" />
        <span>Redirecting to sign in in {countdown}s...</span>
      </div>
    </div>
  );
}
