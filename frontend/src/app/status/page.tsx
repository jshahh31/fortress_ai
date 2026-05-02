"use client";

import { CheckCircle, AlertTriangle, XCircle, Clock } from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";

const SERVICES = [
  { name: "API Gateway", status: "operational" as const, uptime: "99.98%" },
  { name: "Analysis Engine", status: "operational" as const, uptime: "99.95%" },
  { name: "Report Generation", status: "operational" as const, uptime: "99.99%" },
  { name: "Document Parsing", status: "operational" as const, uptime: "99.97%" },
  { name: "Authentication", status: "operational" as const, uptime: "100%" },
];

const INCIDENTS = [
  { date: "Apr 28, 2026", title: "Elevated latency on Analysis Engine", status: "resolved" as const, duration: "23 minutes", description: "Increased processing time due to GPU scheduling queue. Resolved with capacity rebalancing." },
  { date: "Apr 15, 2026", title: "Report generation timeout", status: "resolved" as const, duration: "8 minutes", description: "Brief timeout on PDF export endpoint. Root cause: memory spike during batch processing." },
  { date: "Mar 30, 2026", title: "Scheduled maintenance", status: "resolved" as const, duration: "45 minutes", description: "Planned infrastructure upgrade. All services briefly unavailable during migration window." },
];

const STATUS_CONFIG = {
  operational: { icon: CheckCircle, label: "Operational", class: "text-success", dot: "bg-success shadow-[0_0_8px_rgba(7,202,107,0.5)]" },
  degraded: { icon: AlertTriangle, label: "Degraded", class: "text-warning", dot: "bg-warning shadow-[0_0_8px_rgba(232,149,88,0.5)]" },
  outage: { icon: XCircle, label: "Outage", class: "text-danger", dot: "bg-danger shadow-[0_0_8px_rgba(234,33,67,0.5)]" },
};

export default function StatusPage() {
  const allOperational = SERVICES.every((s) => s.status === "operational");

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      {/* Overall Status */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`rounded-2xl border backdrop-blur-xl p-6 flex items-center gap-4 mb-10 ${
          allOperational ? "verdict-sign" : "verdict-negotiate"
        }`}
      >
        <CheckCircle className="w-8 h-8" />
        <div>
          <h1 className="text-xl font-extrabold">
            {allOperational ? "All Systems Operational" : "Some Systems Degraded"}
          </h1>
          <p className="text-sm opacity-70 mt-0.5">
            Last updated: {new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </p>
        </div>
      </motion.div>

      {/* Services */}
      <div className="space-y-2 mb-14">
        <h2 className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-4">
          Service Status
        </h2>
        {SERVICES.map((service, i) => {
          const config = STATUS_CONFIG[service.status];
          return (
            <motion.div
              key={service.name}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="flex items-center justify-between px-5 py-3.5 rounded-xl border border-white/10 bg-white/[0.02]"
            >
              <div className="flex items-center gap-3">
                <span className={`w-2 h-2 rounded-full ${config.dot}`} />
                <span className="text-sm font-medium text-secondary">{service.name}</span>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-xs font-mono text-muted-foreground">{service.uptime} uptime</span>
                <span className={`text-xs font-semibold ${config.class}`}>{config.label}</span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Incident History */}
      <div>
        <h2 className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-4">
          Incident History
        </h2>
        <div className="space-y-4">
          {INCIDENTS.map((incident) => (
            <div key={incident.title} className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-secondary">{incident.title}</h3>
                <span className="text-[10px] font-mono text-success bg-success/10 px-2 py-0.5 rounded border border-success/20 shrink-0 ml-3">
                  Resolved
                </span>
              </div>
              <p className="text-xs text-muted-foreground mb-2 leading-relaxed">{incident.description}</p>
              <div className="flex items-center gap-4 text-[10px] text-muted-foreground font-mono">
                <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {incident.duration}</span>
                <span>{incident.date}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Admin link */}
      <div className="mt-12 text-center">
        <Link href="/status/dashboard" className="text-xs text-muted-foreground hover:text-primary transition-colors font-mono">
          Developer Dashboard →
        </Link>
      </div>
    </div>
  );
}
