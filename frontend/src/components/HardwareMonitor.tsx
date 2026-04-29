"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Cpu, Thermometer, Microchip } from "lucide-react";

export default function HardwareMonitor() {
  const [vram, setVram] = useState(156);
  const [temp, setTemp] = useState(72);

  // Simulate hardware fluctuations
  useEffect(() => {
    const interval = setInterval(() => {
      setVram((prev) => Math.max(140, Math.min(180, prev + (Math.random() * 4 - 2))));
      setTemp((prev) => Math.max(65, Math.min(85, prev + (Math.random() * 2 - 1))));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const vramPercent = (vram / 192) * 100;
  
  const getTempColor = (t: number) => {
    if (t < 70) return "text-emerald-500";
    if (t < 80) return "text-amber-500";
    return "text-red-500";
  };

  return (
    <div className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <Microchip className="w-5 h-5 text-cyan-400" />
        <h3 className="font-semibold text-sm text-slate-200">MI300X Status</h3>
        <span className="ml-auto flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
        </span>
      </div>

      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400 flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5"/> VRAM Usage</span>
          <span className="font-mono text-slate-200">{vram.toFixed(1)} / 192 GB</span>
        </div>
        <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden">
          <motion.div 
            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500"
            initial={{ width: 0 }}
            animate={{ width: `${vramPercent}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between text-xs border-t border-slate-800/50 pt-3">
        <div className="flex flex-col gap-1">
          <span className="text-slate-500 uppercase tracking-wider text-[10px]">Active Core</span>
          <span className="text-slate-300 font-medium">GPU 0 - Qwen 3.6 35B</span>
        </div>
        <div className="flex flex-col gap-1 items-end">
          <span className="text-slate-500 uppercase tracking-wider text-[10px]">Temp</span>
          <span className={`font-mono font-medium flex items-center gap-1 ${getTempColor(temp)}`}>
            {temp.toFixed(0)}°C
          </span>
        </div>
      </div>
    </div>
  );
}
