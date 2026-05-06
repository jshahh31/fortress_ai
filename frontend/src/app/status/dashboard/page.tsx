"use client";

import { motion } from "framer-motion";
import { Activity, Users, DollarSign, BarChart3, Brain, Shield, Server, ArrowLeft } from "lucide-react";
import Link from "next/link";

const METRICS = [
  {
    category: "System Health",
    icon: Activity,
    items: [
      { label: "CPU Usage", value: "34%", status: "good" },
      { label: "Memory", value: "61%", status: "good" },
      { label: "GPU Utilization", value: "78%", status: "warn" },
      { label: "Disk I/O", value: "12%", status: "good" },
    ],
  },
  {
    category: "User Metrics",
    icon: Users,
    items: [
      { label: "Total Users", value: "2,847", status: "good" },
      { label: "DAU", value: "412", status: "good" },
      { label: "MAU", value: "1,893", status: "good" },
      { label: "Attorneys", value: "38%", status: "good" },
    ],
  },
  {
    category: "Revenue",
    icon: DollarSign,
    items: [
      { label: "MRR", value: "$14,200", status: "good" },
      { label: "Churn", value: "2.1%", status: "good" },
      { label: "LTV", value: "$680", status: "good" },
      { label: "ARPU", value: "$22", status: "good" },
    ],
  },
  {
    category: "Usage",
    icon: BarChart3,
    items: [
      { label: "Reports Today", value: "187", status: "good" },
      { label: "Avg Process Time", value: "4.2s", status: "good" },
      { label: "Queue Depth", value: "3", status: "good" },
      { label: "Peak Hour", value: "2PM EST", status: "good" },
    ],
  },
  {
    category: "AI Performance",
    icon: Brain,
    items: [
      { label: "Accuracy", value: "94.7%", status: "good" },
      { label: "Avg Latency", value: "3.8s", status: "good" },
      { label: "Token Usage/Day", value: "1.2M", status: "warn" },
      { label: "Model Version", value: "v3.6", status: "good" },
    ],
  },
  {
    category: "Security",
    icon: Shield,
    items: [
      { label: "Failed Logins (24h)", value: "12", status: "good" },
      { label: "Blocked IPs", value: "3", status: "good" },
      { label: "Rate Limits Hit", value: "7", status: "good" },
      { label: "Suspicious", value: "0", status: "good" },
    ],
  },
];

const STATUS_COLORS = {
  good: "text-success",
  warn: "text-warning",
  bad: "text-danger",
};

export default function DashboardPage() {
  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <Link
        href="/status"
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-secondary mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> System Status
      </Link>

      <div className="flex items-center gap-3 mb-10">
        <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
          <Server className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h1 className="text-xl font-extrabold text-secondary">Developer Dashboard</h1>
          <p className="text-xs text-muted-foreground">Real-time system metrics — Admin only</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {METRICS.map((section, i) => {
          const Icon = section.icon;
          return (
            <motion.div
              key={section.category}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.06 }}
              className="glass-panel rounded-xl p-5"
            >
              <div className="flex items-center gap-2 mb-4">
                <Icon className="w-4 h-4 text-primary" />
                <h3 className="text-[10px] font-mono font-bold uppercase tracking-wider text-muted-foreground">
                  {section.category}
                </h3>
              </div>
              <div className="space-y-3">
                {section.items.map((item) => (
                  <div key={item.label} className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">{item.label}</span>
                    <span className={`text-sm font-bold ${STATUS_COLORS[item.status as keyof typeof STATUS_COLORS]}`}>
                      {item.value}
                    </span>
                  </div>
                ))}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
