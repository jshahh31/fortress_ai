"use client";

import { motion } from "framer-motion";
import { FileSearch, BookOpen, ShieldAlert, FileText, Check, Loader2, X } from "lucide-react";
import { AgentNode } from "@/types";

interface AgentPipelineProps {
  nodes: AgentNode[];
}

export default function AgentPipeline({ nodes }: AgentPipelineProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h2 className="text-sm font-semibold text-slate-300 mb-6 uppercase tracking-wider">Multi-Agent Pipeline</h2>
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center relative">
        {/* Background dashed line */}
        <div className="absolute top-6 left-8 right-8 h-[2px] border-t-2 border-dashed border-slate-700 hidden md:block z-0" />

        {nodes.map((node, index) => {
          const Icon = getIcon(node.icon);
          const isActive = node.status === "processing";
          const isDone = node.status === "completed";
          const isError = node.status === "error";

          return (
            <div key={node.id} className="relative z-10 flex flex-col items-center gap-3 group w-full md:w-auto mt-6 md:mt-0">
              
              {/* Connecting line for mobile */}
              {index !== 0 && (
                <div className="absolute -top-6 left-1/2 w-[2px] h-6 border-l-2 border-dashed border-slate-700 md:hidden" />
              )}

              {/* Status Circle */}
              <div className="relative">
                <motion.div
                  layoutId={`ring-${node.id}`}
                  className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-colors duration-300 ${
                    isDone ? "bg-emerald-500/20 border-emerald-500 text-emerald-400" :
                    isError ? "bg-red-500/20 border-red-500 text-red-400" :
                    isActive ? "bg-slate-800 border-cyan-400 text-cyan-400" :
                    "bg-slate-900 border-slate-700 text-slate-500"
                  }`}
                >
                  {isDone ? <Check className="w-5 h-5" /> : 
                   isError ? <X className="w-5 h-5" /> : 
                   isActive ? <Loader2 className="w-5 h-5 animate-spin" /> : 
                   <Icon className="w-5 h-5" />}
                </motion.div>

                {isActive && (
                  <span className="absolute inset-0 rounded-full animate-ping border border-cyan-400 opacity-50" />
                )}
              </div>

              {/* Info Text */}
              <div className="text-center">
                <h4 className={`text-sm font-semibold ${isDone ? "text-emerald-400" : isActive ? "text-cyan-400" : "text-slate-300"}`}>
                  {node.name}
                </h4>
                <p className="text-[11px] text-slate-500 font-mono mt-1">{node.model}</p>
                {node.gpu_id && isActive && (
                  <span className="inline-block mt-1.5 px-2 py-0.5 rounded-sm bg-slate-800 text-cyan-400 text-[10px] border border-cyan-900/50">
                    {node.gpu_id}
                  </span>
                )}
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
}

function getIcon(name: string) {
  switch (name) {
    case "FileSearch": return FileSearch;
    case "BookOpen": return BookOpen;
    case "ShieldAlert": return ShieldAlert;
    case "FileText": return FileText;
    default: return FileSearch;
  }
}
