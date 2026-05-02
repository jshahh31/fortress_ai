"use client";

import { motion } from "framer-motion";
import { AlertTriangle, AlertCircle, Info, CheckCircle } from "lucide-react";
import { RiskMatrix as RiskMatrixType, RiskLevel } from "@/types";

interface RiskMatrixProps {
  matrix: RiskMatrixType;
}

const QUADRANTS: {
  level: RiskLevel;
  label: string;
  icon: typeof AlertTriangle;
  cardClass: string;
  textClass: string;
  dotClass: string;
}[] = [
  { level: "critical", label: "Critical", icon: AlertTriangle, cardClass: "risk-critical", textClass: "risk-text-critical", dotClass: "risk-dot-critical" },
  { level: "high", label: "High", icon: AlertCircle, cardClass: "risk-high", textClass: "risk-text-high", dotClass: "risk-dot-high" },
  { level: "medium", label: "Medium", icon: Info, cardClass: "risk-medium", textClass: "risk-text-medium", dotClass: "risk-dot-medium" },
  { level: "low", label: "Low", icon: CheckCircle, cardClass: "risk-low", textClass: "risk-text-low", dotClass: "risk-dot-low" },
];

export default function RiskMatrix({ matrix }: RiskMatrixProps) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {QUADRANTS.map((q, i) => {
        const items = matrix[q.level];
        const Icon = q.icon;
        return (
          <motion.div
            key={q.level}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.08 }}
            className={`rounded-xl border backdrop-blur-md p-4 ${q.cardClass}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Icon className={`w-4 h-4 ${q.textClass}`} />
                <span className={`text-xs font-bold uppercase tracking-wider ${q.textClass}`}>
                  {q.label}
                </span>
              </div>
              <span className={`text-lg font-extrabold ${q.textClass}`}>
                {items.length}
              </span>
            </div>
            {items.length > 0 ? (
              <ul className="space-y-1.5">
                {items.slice(0, 3).map((item) => (
                  <li key={item.id} className="flex items-start gap-2">
                    <span className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${q.dotClass}`} />
                    <span className="text-xs text-secondary/80 leading-relaxed line-clamp-1">
                      {item.clause} — §{item.section}
                    </span>
                  </li>
                ))}
                {items.length > 3 && (
                  <li className="text-[10px] text-muted-foreground pl-3.5">
                    +{items.length - 3} more
                  </li>
                )}
              </ul>
            ) : (
              <p className="text-[11px] text-muted-foreground italic">None identified</p>
            )}
          </motion.div>
        );
      })}
    </div>
  );
}
