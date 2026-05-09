"use client";

import { useState } from "react";
import { ChevronDown, Copy, Check } from "lucide-react";
import { RiskItem } from "@/types";
import { motion, AnimatePresence } from "framer-motion";

interface ClauseCardProps {
  item: RiskItem;
  index: number;
}

const RISK_BADGE: Record<string, { label: string; class: string }> = {
  critical: { label: "CRITICAL", class: "bg-danger/20 text-danger border-danger/30" },
  high: { label: "HIGH", class: "bg-warning/20 text-warning border-warning/30" },
  medium: { label: "MEDIUM", class: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" },
  low: { label: "LOW", class: "bg-success/20 text-success border-success/30" },
};

export default function ClauseCard({ item, index }: ClauseCardProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const badge = RISK_BADGE[item.level];

  const handleCopy = () => {
    if (item.suggestion) {
      navigator.clipboard.writeText(item.suggestion);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.05 }}
      className="rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-md overflow-hidden"
    >
      {/* Header — always visible */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-3 px-4 py-3.5 text-left hover:bg-white/5 transition-colors"
      >
        <span className="text-sm font-mono text-primary font-medium shrink-0">
          §{item.section}{item.page && ` • p.${item.page}`}
        </span>
        <span className="text-sm font-semibold text-secondary flex-1">
          {item.clause}
        </span>
        {item.priority && (
          <span className="text-[10px] font-mono text-muted-foreground/60 shrink-0 px-1.5">
            P{item.priority}
          </span>
        )}
        {item.clause_type && (
          <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-muted-foreground border border-white/10 shrink-0">
            {item.clause_type}
          </span>
        )}
        <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border shrink-0 ${badge.class}`}>
          {badge.label}
        </span>
        <ChevronDown
          className={`w-4 h-4 text-muted-foreground transition-transform duration-200 shrink-0 ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {/* Body — expandable */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-4 border-t border-white/5 pt-4">
              {/* Specific Contract Quotes - Exact problematic language */}
              {(item.contract_text || item.originalText) && (
                <div>
                  <p className="text-[10px] font-mono font-bold uppercase text-primary tracking-wider mb-1.5">
                    SPECIFIC CONTRACT LANGUAGE
                  </p>
                  <div className="bg-primary/5 rounded-lg p-3 border border-primary/20">
                    <p className="text-sm text-secondary font-medium leading-relaxed">
                      &ldquo;{item.contract_text || item.originalText}&rdquo;
                    </p>
                  </div>
                </div>
              )}

              {/* Risk description with section reference */}
              <div>
                <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-1.5">
                  {item.section && `SECTION §${item.section}`} RISK ASSESSMENT
                </p>
                <p className="text-sm text-secondary leading-relaxed">
                  {item.description}
                </p>
              </div>

              {/* Risk Justification (Phase 2) */}
              {item.justification && (
                <div>
                  <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-1.5">
                    Risk Justification
                  </p>
                  <p className="text-sm text-secondary/90 leading-relaxed">
                    {item.justification}
                  </p>
                </div>
              )}

              {/* Industry standard */}
              {item.industryStandard && (
                <div>
                  <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-1.5">
                    Industry Standard
                  </p>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {item.industryStandard}
                  </p>
                </div>
              )}

              {/* Suggestion */}
              {item.suggestion && (
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider">
                      Suggested Modification
                    </p>
                    <button
                      onClick={handleCopy}
                      className="flex items-center gap-1 text-[10px] text-primary hover:text-primary/80 transition-colors font-medium"
                    >
                      {copied ? (
                        <><Check className="w-3 h-3" /> Copied</>
                      ) : (
                        <><Copy className="w-3 h-3" /> Copy</>
                      )}
                    </button>
                  </div>
                  <div className="bg-primary/5 rounded-lg p-3 border border-primary/10">
                    <p className="text-sm text-secondary leading-relaxed">
                      {item.suggestion}
                    </p>
                  </div>
                </div>
              )}

              {/* Related Sections (Phase 2) */}
              {item.related_sections && item.related_sections.length > 0 && (
                <div>
                  <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-1.5">
                    Related Sections
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {item.related_sections.map((sec) => (
                      <span
                        key={sec}
                        className="text-xs font-mono px-2 py-1 rounded bg-primary/10 text-primary border border-primary/20"
                      >
                        §{sec}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
