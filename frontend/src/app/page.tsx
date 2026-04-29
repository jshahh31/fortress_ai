"use client";

import { useState } from "react";
import AgentPipeline from "@/components/AgentPipeline";
import VaultUpload from "@/components/VaultUpload";
import RiskScorecard from "@/components/RiskScorecard";
import AuditFeed from "@/components/AuditFeed";
import { AgentNode } from "@/types";

const INITIAL_NODES: AgentNode[] = [
  { id: "ext", name: "Extraction", model: "Qwen 3.6 35B", status: "idle", icon: "FileSearch" },
  { id: "res", name: "Research", model: "Gemma 4 4B", status: "idle", icon: "BookOpen" },
  { id: "rsk", name: "Risk Analysis", model: "Qwen 3.6 35B", status: "idle", icon: "ShieldAlert" },
  { id: "rep", name: "Final Report", model: "Gemma 4 4B", status: "idle", icon: "FileText" },
];

export default function Dashboard() {
  const [nodes, setNodes] = useState<AgentNode[]>(INITIAL_NODES);
  
  // This function would normally call your FastAPI backend
  const handleFileUpload = (file: File) => {
    console.log("Uploading file to vault:", file.name);
    
    // Simulate pipeline starting
    let currentStep = 0;
    
    const runPipeline = () => {
      setNodes((prev) => 
        prev.map((n, i) => {
          if (i < currentStep) return { ...n, status: "completed" };
          if (i === currentStep) return { 
            ...n, 
            status: "processing", 
            gpu_id: n.model.includes("Qwen") ? "GPU 0" : "GPU 1" 
          };
          return { ...n, status: "idle", gpu_id: undefined };
        })
      );

      currentStep++;

      if (currentStep <= INITIAL_NODES.length) {
        setTimeout(runPipeline, 2500); // simulate 2.5s per step
      } else {
        setNodes((prev) => prev.map(n => ({ ...n, status: "completed" })));
      }
    };

    runPipeline();
  };

  return (
    <div className="p-6 md:p-8 space-y-6 max-w-7xl mx-auto h-full flex flex-col">
      <header className="mb-2">
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Command Center</h1>
        <p className="text-slate-500 text-sm mt-1">Monitor active audits and multi-agent pipeline status.</p>
      </header>

      {/* Top Row: Pipeline */}
      <AgentPipeline nodes={nodes} />

      {/* Middle Row: Upload & Scorecard */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-64">
        <div className="lg:col-span-4 h-full">
          <VaultUpload onUpload={handleFileUpload} />
        </div>
        <div className="lg:col-span-8 h-full">
          <RiskScorecard />
        </div>
      </div>

      {/* Bottom Row: Streaming Terminal */}
      <div className="flex-1 min-h-0 pt-2">
        <AuditFeed />
      </div>
    </div>
  );
}
