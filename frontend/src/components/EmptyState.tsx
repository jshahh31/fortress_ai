"use client";

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
} from "lucide-react";
import { motion } from "framer-motion";
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
  const handleDragOver = (e: React.DragEvent) => e.preventDefault();

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
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
          onDrop={handleDrop}
          className="flex flex-col items-center justify-center gap-3 p-10 rounded-2xl border-2 border-dashed border-white/10 bg-white/[0.03] backdrop-blur-md cursor-pointer hover:border-primary/40 hover:bg-white/[0.06] transition-all duration-300 group"
        >
          <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:bg-primary/10 group-hover:border-primary/20 transition-colors shadow-lg">
            <Upload className="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors" />
          </div>
          <div className="text-center">
            <p className="text-sm font-semibold text-secondary">
              Drop your contract here, or <span className="text-primary">browse</span>
            </p>
            <p className="text-xs text-muted-foreground mt-1">PDF, DOCX, TXT, or Photo — up to 25 MB</p>
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
