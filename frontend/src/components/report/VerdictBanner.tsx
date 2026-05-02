"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Handshake, XCircle, Scale } from "lucide-react";
import { ReportVerdict } from "@/types";

interface VerdictBannerProps {
  verdict: ReportVerdict;
}

const VERDICT_CONFIG: Record<
  ReportVerdict,
  { label: string; sublabel: string; icon: typeof CheckCircle2; className: string }
> = {
  SIGN: {
    label: "SIGN",
    sublabel: "This contract is generally fair and standard. Safe to proceed.",
    icon: CheckCircle2,
    className: "verdict-sign",
  },
  NEGOTIATE: {
    label: "NEGOTIATE",
    sublabel: "Significant concerns identified. Negotiate terms before signing.",
    icon: Handshake,
    className: "verdict-negotiate",
  },
  REJECT: {
    label: "REJECT",
    sublabel: "Critical risks found. Do not sign in current form.",
    icon: XCircle,
    className: "verdict-reject",
  },
  SEEK_COUNSEL: {
    label: "SEEK COUNSEL",
    sublabel: "Complex provisions require professional legal review.",
    icon: Scale,
    className: "verdict-counsel",
  },
};

export default function VerdictBanner({ verdict }: VerdictBannerProps) {
  const config = VERDICT_CONFIG[verdict];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className={`rounded-2xl border backdrop-blur-xl p-6 flex items-center gap-5 ${config.className}`}
    >
      <div className="shrink-0 w-14 h-14 rounded-2xl bg-white/10 border border-white/10 flex items-center justify-center">
        <Icon className="w-7 h-7" />
      </div>
      <div>
        <p className="text-xs font-mono font-bold uppercase tracking-wider opacity-70 mb-1">
          Verdict
        </p>
        <h2 className="text-2xl font-extrabold tracking-tight">{config.label}</h2>
        <p className="text-sm opacity-70 mt-1 leading-relaxed">{config.sublabel}</p>
      </div>
    </motion.div>
  );
}
