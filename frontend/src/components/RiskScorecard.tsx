"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Shield, Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

export default function RiskScorecard() {
  const score = 87;
  const isHealthy = score > 80;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col">
      <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-6">Risk Scorecard</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
        
        {/* Compliance Score Card */}
        <Card className="bg-slate-950/50 border-slate-800 shadow-none">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-slate-400 flex items-center gap-2">
              <Shield className="w-4 h-4" /> Compliance Score
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center py-4">
            <div className="relative w-24 h-24 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="10" className="text-slate-800" />
                <motion.circle 
                  cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="10"
                  strokeDasharray="283"
                  initial={{ strokeDashoffset: 283 }}
                  animate={{ strokeDashoffset: 283 - (283 * score) / 100 }}
                  transition={{ duration: 1.5, ease: "easeOut" }}
                  className={isHealthy ? "text-emerald-500" : "text-amber-500"}
                  strokeLinecap="round"
                />
              </svg>
              <span className={`absolute text-2xl font-bold ${isHealthy ? "text-emerald-400" : "text-amber-400"}`}>
                {score}%
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-4 text-center">Low probability of compliance breach</p>
          </CardContent>
        </Card>

        {/* Critical Liabilities */}
        <div className="flex flex-col gap-4">
          <Card className="bg-slate-950/50 border-slate-800 shadow-none flex-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-slate-400 flex items-center justify-between">
                <div className="flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-amber-500" /> Critical Liabilities</div>
                <Badge variant="destructive" className="bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500/20 rounded-sm px-1.5 py-0">2</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5 shrink-0" />
                  <p className="text-xs text-slate-300 leading-relaxed">Indemnification clause lacks liability cap (Section 4.2)</p>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                  <p className="text-xs text-slate-300 leading-relaxed">Auto-renewal without prior written notice (Section 7.1)</p>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
