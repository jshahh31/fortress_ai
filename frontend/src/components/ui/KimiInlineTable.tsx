"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Copy, Check, Download } from "lucide-react";

// ── Status config ──────────────────────────────────────────────────────────────

export type InlineRowStatus = "critical" | "high" | "medium" | "low";

const STATUS: Record<InlineRowStatus, { label: string; badge: string; dot: string; icon: string }> = {
  critical: {
    label: "Critical",
    badge: "text-[#EA4335]",
    dot: "bg-[#EA4335]",
    icon: "❌",
  },
  high: {
    label: "High",
    badge: "text-[#FBBC04]",
    dot: "bg-[#FBBC04]",
    icon: "⚠️",
  },
  medium: {
    label: "Medium",
    badge: "text-[#F5A623]",
    dot: "bg-[#F5A623]",
    icon: "🔔",
  },
  low: {
    label: "Low",
    badge: "text-[#34A853]",
    dot: "bg-[#34A853]",
    icon: "✅",
  },
};

// ── Types ─────────────────────────────────────────────────────────────────────

export interface InlineTableColumn {
  label: string;
  key: string;
}

export interface InlineTableRow {
  id: string;
  cells: string[];
  status?: InlineRowStatus;
}

interface KimiInlineTableProps {
  title?: string;
  columns: InlineTableColumn[];
  rows: InlineTableRow[];
  delay?: number;
}

// ── Main ──────────────────────────────────────────────────────────────────────

export default function KimiInlineTable({
  title = "Table",
  columns,
  rows,
  delay = 0,
}: KimiInlineTableProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyCSV = () => {
    const header = columns.map(c => c.label).join(",");
    const body = rows.map(r => r.cells.map(c => `"${c.replace(/"/g, '""')}"`).join(",")).join("\n");
    const csv = `${header}\n${body}`;
    
    navigator.clipboard.writeText(csv);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadExcel = () => {
    const header = columns.map(c => c.label).join(",");
    const body = rows.map(r => r.cells.map(c => `"${c.replace(/"/g, '""')}"`).join(",")).join("\n");
    const csv = `${header}\n${body}`;
    
    // Add BOM for UTF-8 Excel compatibility
    const blob = new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8;" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    
    link.href = url;
    link.download = `${title.toLowerCase().replace(/\s+/g, "_")}.csv`;
    
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    setTimeout(() => {
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }, 100);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: delay / 1000 }}
      className="my-5 w-full border border-white/10 rounded-[12px] overflow-hidden font-sans"
    >
      {/* Header Row */}
      <div className="flex items-center justify-between px-3 py-3 border-b border-white/10 bg-[#292929]">
        <span className="text-xs font-bold text-[#E89558]">
          {title}
        </span>
        <div className="flex items-center gap-3">
          <button 
            onClick={handleCopyCSV}
            className="text-muted-foreground hover:text-secondary transition-colors"
            title="Copy as CSV"
          >
            {copied ? <Check className="w-4 h-4 text-success" /> : <Copy className="w-4 h-4" />}
          </button>
          <button 
            onClick={handleDownloadExcel}
            className="text-muted-foreground hover:text-secondary transition-colors" 
            title="Download for Excel"
          >
            <Download className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              {columns.map((col, i) => (
                <th
                  key={col.key}
                  className={`px-3 py-2 text-[11px] font-bold text-secondary border-b border-white/10 ${
                    i > 0 ? "border-l border-white/10" : ""
                  } text-left uppercase tracking-wider`}
                >
                  {col.label}
                </th>
              ))}

            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={row.id} className={i === rows.length - 1 ? "" : "border-b border-white/10"}>
                {row.cells.map((cell, ci) => (
                  <td
                    key={ci}
                    className={`px-3 py-2 text-[12px] text-secondary ${
                      ci > 0 ? "border-l border-white/10" : ""
                    } text-left`}
                  >
                    {cell}
                  </td>
                ))}

              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
