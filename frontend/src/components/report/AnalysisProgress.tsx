"use client";

import { motion } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { AnalysisStep } from "@/types";

interface AnalysisProgressProps {
  steps: AnalysisStep[];
}

export default function AnalysisProgress({ steps }: AnalysisProgressProps) {
  const completedCount = steps.filter((s) => s.status === "completed").length;
  const allDone = completedCount === steps.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="my-1 w-full max-w-sm"
      style={{
        background: "#1A1D23",
        border: "1px solid #2D3139",
        borderRadius: 12,
        padding: "14px 16px",
      }}
    >
      {/* Header row */}
      <div className="flex items-center justify-between mb-3">
        <span
          className="text-[11px] font-semibold uppercase tracking-[0.5px]"
          style={{ color: "#9AA0A6" }}
        >
          Analysis Pipeline
        </span>
        {allDone && (
          <motion.span
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.2, type: "spring", stiffness: 300 }}
            className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-semibold rounded"
            style={{
              background: "rgba(52,168,83,0.12)",
              color: "#34A853",
              border: "1px solid rgba(52,168,83,0.25)",
              borderRadius: 4,
            }}
          >
            <Check className="w-3 h-3" /> Complete
          </motion.span>
        )}
      </div>

      {/* Steps */}
      <div className="space-y-2.5">
        {steps.map((step, i) => {
          const isDone = step.status === "completed";
          const isActive = step.status === "processing";
          const isPending = step.status === "idle";

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: i * 0.05 }}
              className="flex items-center gap-3"
            >
              {/* Icon */}
              <div className="relative w-5 h-5 shrink-0 flex items-center justify-center">
                {isDone ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.25, type: "spring", stiffness: 400, delay: 0.05 }}
                  >
                    <Check className="w-4 h-4" style={{ color: "#34A853" }} />
                  </motion.div>
                ) : isActive ? (
                  <Loader2
                    className="w-4 h-4 animate-spin"
                    style={{ color: "#8AB4F8" }}
                  />
                ) : (
                  <div
                    className="w-3.5 h-3.5 rounded-full border-2"
                    style={{ borderColor: "#3C4043" }}
                  />
                )}
              </div>

              {/* Label + description */}
              <div className="flex-1 min-w-0 flex items-center justify-between">
                <span
                  className="text-[13px] font-medium leading-none"
                  style={{
                    color: isDone ? "#E8EAED" : isActive ? "#E8EAED" : "#5F6368",
                  }}
                >
                  {step.label}
                  {step.description && (
                    <span
                      className="ml-1.5 text-[12px]"
                      style={{ color: isPending ? "#3C4043" : "#9AA0A6" }}
                    >
                      — {step.description}
                    </span>
                  )}
                </span>

                {isActive && (
                  <motion.span
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.4, repeat: Infinity }}
                    className="text-[11px] font-mono ml-2 shrink-0"
                    style={{ color: "#8AB4F8" }}
                  >
                    running
                  </motion.span>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Progress bar */}
      <div
        className="mt-4 h-[3px] rounded-full overflow-hidden"
        style={{ background: "#2D3139" }}
      >
        <motion.div
          className="h-full rounded-full"
          style={{ background: allDone ? "#34A853" : "#8AB4F8" }}
          initial={{ width: 0 }}
          animate={{ width: `${(completedCount / steps.length) * 100}%` }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        />
      </div>
    </motion.div>
  );
}
