"use client";

import { useState, useEffect, useRef } from "react";
import { Terminal } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function AuditFeed() {
  const [logs, setLogs] = useState<string[]>([
    "Initializing Fortress AI Multi-Agent Pipeline...",
    "System ready. Awaiting document...",
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // Simulate a stream starting
  const simulateStream = () => {
    if (isProcessing) return;
    setIsProcessing(true);
    
    const mockChunks = [
      "\n[GPU 0 — Qwen 72B] Extraction Node Triggered...",
      "Found 14 clauses. Extracting entities...",
      "Done.",
      "\n[GPU 1 — Gemma 4] Research Node Triggered...",
      "Querying Qdrant index (legal_documents) via bge-m3...",
      "Found 3 relevant precedents.",
      "\n[GPU 0 — Qwen 72B] Risk Analysis...",
      "Evaluating indemnification liabilities...",
      "Warning: Uncapped liability detected in Section 4.2.",
      "\n[GPU 1 — Gemma 4] Compiling Final Report...\n",
      "## AUDIT SUMMARY\n",
      "The provided Master Service Agreement exposes the company to significant financial risk due to an uncapped indemnification clause (Section 4.2). ",
      "It is highly recommended to negotiate a cap equal to 12 months of service fees. ",
      "Additionally, the auto-renewal clause (7.1) requires a 90-day manual opt-out. Setup internal trackers.",
      "\n--- AUDIT COMPLETE ---"
    ];

    let i = 0;
    setLogs((prev) => [...prev, "--- STARTING NEW AUDIT ---"]);
    
    const interval = setInterval(() => {
      if (i < mockChunks.length) {
        setLogs((prev) => [...prev, mockChunks[i]]);
        i++;
      } else {
        clearInterval(interval);
        setIsProcessing(false);
      }
    }, 600); // ms per chunk
  };

  return (
    <div className="bg-[#0c0e14] border border-slate-800 rounded-xl flex flex-col h-[400px] overflow-hidden relative group">
      
      {/* Terminal Header */}
      <div className="h-10 bg-slate-900 border-b border-slate-800 flex items-center px-4 shrink-0">
        <Terminal className="w-4 h-4 text-slate-500 mr-2" />
        <span className="text-xs font-mono text-slate-400">audit_feed.log</span>
        <div className="ml-auto flex items-center gap-2">
          {isProcessing && <span className="flex w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />}
          <span className="text-[10px] text-slate-500 font-mono uppercase">
            {isProcessing ? "Streaming" : "Idle"}
          </span>
        </div>
      </div>

      {/* Terminal Body */}
      <ScrollArea className="flex-1 p-4">
        <div className="font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
          {logs.map((log, i) => {
            const isGpuLog = log.includes("[GPU");
            const isQwen = log.includes("Qwen");
            
            return (
              <div key={i} className={`mb-1 ${isGpuLog ? (isQwen ? "text-cyan-400" : "text-purple-400") : ""}`}>
                {log}
              </div>
            );
          })}
          {isProcessing && (
            <span className="inline-block w-2 h-3 bg-slate-400 animate-pulse ml-1 align-middle" />
          )}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Hidden button to trigger simulation for the demo */}
      <button 
        onClick={simulateStream}
        disabled={isProcessing}
        className="absolute bottom-4 right-4 bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1.5 rounded text-slate-300 transition-colors opacity-0 group-hover:opacity-100"
      >
        Simulate SSE Stream
      </button>

    </div>
  );
}
