"use client";

import { useState } from "react";
import {
  ShieldCheck,
  Upload,
  FileSearch,
  Scale,
  Briefcase,
  Handshake,
  FileSignature,
  ScrollText,
  Building2,
  FileCheck,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ContractType, CONTRACT_TYPE_LABELS } from "@/types";

interface EmptyStateProps {
  onUpload: (file: File) => void;
  onContractTypeHint: (type: ContractType) => void;
}

const CONTRACT_CHIPS: { type: ContractType; icon: typeof FileSearch; tier: string }[] = [
  { type: "residential_lease", icon: Building2, tier: "Individual" },
  { type: "employment_agreement", icon: Briefcase, tier: "Individual" },
  { type: "freelance_agreement", icon: Handshake, tier: "Individual" },
  { type: "nda_personal", icon: ScrollText, tier: "Individual" },
  { type: "partnership_agreement", icon: Handshake, tier: "Business" },
  { type: "vendor_agreement", icon: FileSignature, tier: "Business" },
  { type: "nda_business", icon: ScrollText, tier: "Business" },
  { type: "consulting_agreement", icon: Scale, tier: "Business" },
];

export default function EmptyState({ onUpload, onContractTypeHint }: EmptyStateProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) onUpload(file);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onUpload(file);
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 relative">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-8"
      >
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 mb-6 shadow-[0_0_30px_rgba(24,86,255,0.15)]">
          <ShieldCheck className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-3xl md:text-4xl font-extrabold text-secondary tracking-tight mb-3">
          Contract Risk Assessment
        </h1>
        <p className="text-muted-foreground text-base max-w-lg mx-auto leading-relaxed">
          Upload any contract. Get a professional risk report with verdict, clause analysis, and actionable recommendations — in seconds.
        </p>
      </motion.div>

      {/* Upload Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="w-full max-w-xl mb-8"
      >
        <label
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`relative flex flex-col items-center justify-center gap-4 p-12 rounded-[32px] border-2 border-dashed transition-all duration-500 cursor-pointer group overflow-hidden ${
            isDragging
              ? "border-primary bg-primary/5 scale-[1.02] shadow-[0_0_40px_rgba(24,86,255,0.15)]"
              : "border-white/10 bg-white/[0.03] backdrop-blur-md hover:border-primary/40 hover:bg-white/[0.06]"
          }`}
        >
          {/* Pulsating background for dragging */}
          <AnimatePresence>
            {isDragging && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 pointer-events-none"
              >
                <motion.div
                  animate={{ 
                    scale: [1, 1.1, 1],
                    opacity: [0.1, 0.2, 0.1]
                  }}
                  transition={{ repeat: Infinity, duration: 2 }}
                  className="absolute inset-0 bg-primary/20 blur-3xl"
                />
              </motion.div>
            )}
          </AnimatePresence>

          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-500 shadow-xl ${
            isDragging 
              ? "bg-primary text-white scale-110 rotate-3 shadow-primary/20" 
              : "bg-white/5 border border-white/10 text-muted-foreground group-hover:bg-primary/10 group-hover:border-primary/20 group-hover:text-primary"
          }`}>
            {isDragging ? (
              <FileCheck className="w-8 h-8 animate-bounce" />
            ) : (
              <Upload className="w-7 h-7" />
            )}
          </div>

          <div className="text-center relative z-10">
            <p className={`text-lg font-bold transition-colors duration-300 ${
              isDragging ? "text-primary" : "text-secondary"
            }`}>
              {isDragging ? "Drop to Analyze" : "Drop your contract here"}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {isDragging 
                ? "Release to start the risk assessment" 
                : <span>or <span className="text-primary hover:underline">browse files</span></span>
              }
            </p>
            {!isDragging && (
              <p className="text-[10px] text-muted-foreground/60 mt-4 font-mono uppercase tracking-widest">
                PDF • DOCX • TXT • IMAGES
              </p>
            )}
          </div>
          
          <input
            type="file"
            accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.webp,.heic"
            onChange={handleFileSelect}
            className="hidden"
          />
        </label>
      </motion.div>

      {/* Contract Type Chips */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="max-w-2xl w-full"
      >
        <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider text-center mb-3">
          Or select a contract type to start
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {CONTRACT_CHIPS.map((chip) => {
            const Icon = chip.icon;
            return (
              <button
                key={chip.type}
                onClick={() => onContractTypeHint(chip.type)}
                className="glass-panel glass-panel-hover rounded-lg px-3.5 py-2 flex items-center gap-2 text-xs font-medium text-muted-foreground hover:text-secondary transition-all"
              >
                <Icon className="w-3.5 h-3.5 text-primary" />
                {CONTRACT_TYPE_LABELS[chip.type]}
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Decorative blurs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/15 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute bottom-1/3 right-1/4 w-72 h-72 bg-success/8 rounded-full blur-[100px] pointer-events-none -z-10" />
    </div>
  );
}
