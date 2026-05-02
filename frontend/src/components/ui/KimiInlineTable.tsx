"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, Copy, Check } from "lucide-react";

// ── Status config ──────────────────────────────────────────────────────────────

export type InlineRowStatus = "critical" | "high" | "medium" | "low";

const STATUS: Record<InlineRowStatus, { label: string; badge: string; dot: string }> = {
  critical: {
    label: "Critical",
    badge: "bg-[rgba(234,67,53,0.10)] text-[#EA4335] border-[rgba(234,67,53,0.25)]",
    dot: "bg-[#EA4335] shadow-[0_0_5px_rgba(234,67,53,0.6)]",
  },
  high: {
    label: "High",
    badge: "bg-[rgba(251,188,4,0.10)] text-[#FBBC04] border-[rgba(251,188,4,0.25)]",
    dot: "bg-[#FBBC04] shadow-[0_0_5px_rgba(251,188,4,0.6)]",
  },
  medium: {
    label: "Medium",
    badge: "bg-[rgba(245,166,35,0.10)] text-[#F5A623] border-[rgba(245,166,35,0.25)]",
    dot: "bg-[#F5A623] shadow-[0_0_5px_rgba(245,166,35,0.6)]",
  },
  low: {
    label: "Low",
    badge: "bg-[rgba(52,168,83,0.10)] text-[#34A853] border-[rgba(52,168,83,0.25)]",
    dot: "bg-[#34A853] shadow-[0_0_5px_rgba(52,168,83,0.6)]",
  },
};

// ── Types ─────────────────────────────────────────────────────────────────────

export interface InlineTableColumn {
  label: string;
  key: string;
  /** Only shown on md+ screens */
  hideOnMobile?: boolean;
}

export interface InlineTableRow {
  id: string;
  cells: string[];
  status?: InlineRowStatus;
  /** Renders a collapsible detail block below the row */
  detail?: React.ReactNode;
  copyValue?: string;
}

interface KimiInlineTableProps {
  title?: string;
  columns: InlineTableColumn[];
  rows: InlineTableRow[];
  /** Fade-in delay in ms (for sequential appearance after text) */
  delay?: number;
}

// ── Row ───────────────────────────────────────────────────────────────────────

function InlineRow({
  row,
  columns,
  isLast,
}: {
  row: InlineTableRow;
  columns: InlineTableColumn[];
  isLast: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const cfg = row.status ? STATUS[row.status] : null;
  const hasDetail = !!row.detail;

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (row.copyValue) {
      navigator.clipboard.writeText(row.copyValue);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  return (
    <>
      <tr
        onClick={hasDetail ? () => setOpen((v) => !v) : undefined}
        className={`group transition-colors duration-150 ${hasDetail ? "cursor-pointer" : ""} hover:bg-[#252830] ${!isLast || open ? "border-b border-[#2D3139]" : ""}`}
      >
        {/* Expand chevron */}
        {hasDetail && (
          <td className="pl-3 pr-0 py-3 w-5">
            <ChevronRight
              className={`w-3.5 h-3.5 text-[#5F6368] transition-transform duration-200 ${open ? "rotate-90" : ""}`}
            />
          </td>
        )}

        {/* Data cells */}
        {row.cells.map((cell, ci) => (
          <td
            key={ci}
            className={`px-3 py-3 text-[13px] leading-snug ${ci === 0 ? "text-[#E8EAED] font-medium" : "text-[#9AA0A6]"} ${columns[ci]?.hideOnMobile ? "hidden sm:table-cell" : ""}`}
          >
            {cell}
          </td>
        ))}

        {/* Status badge */}
        {cfg && (
          <td className="px-3 py-3 whitespace-nowrap">
            <span
              className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-[11px] font-semibold border ${cfg.badge}`}
              style={{ borderRadius: 4 }}
            >
              <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${cfg.dot}`} />
              {cfg.label}
            </span>
          </td>
        )}

        {/* Hover actions */}
        <td className="px-3 py-3 whitespace-nowrap">
          <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
            {row.copyValue && (
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] bg-[#252830] text-[#9AA0A6] hover:text-[#E8EAED] border border-white/5 transition-colors"
              >
                {copied ? <Check className="w-3 h-3 text-[#34A853]" /> : <Copy className="w-3 h-3" />}
                {copied ? "Copied" : "Copy"}
              </button>
            )}
          </div>
        </td>
      </tr>

      {/* Expandable detail */}
      <AnimatePresence>
        {open && hasDetail && (
          <tr key="detail">
            <td
              colSpan={row.cells.length + (cfg ? 1 : 0) + (hasDetail ? 1 : 0) + 1}
              className={`${!isLast ? "border-b border-[#2D3139]" : ""}`}
            >
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
                className="overflow-hidden"
              >
                <div
                  className="px-4 py-3 text-[13px] text-[#9AA0A6] leading-relaxed"
                  style={{ background: "#0F1419" }}
                >
                  {row.detail}
                </div>
              </motion.div>
            </td>
          </tr>
        )}
      </AnimatePresence>
    </>
  );
}

// ── Main ──────────────────────────────────────────────────────────────────────

export default function KimiInlineTable({
  title,
  columns,
  rows,
  delay = 0,
}: KimiInlineTableProps) {
  const hasStatus = rows.some((r) => r.status);

  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: delay / 1000 }}
      className="my-3 w-full overflow-x-auto"
      style={{
        background: "#1A1D23",
        border: "1px solid #2D3139",
        borderRadius: 12,
      }}
    >
      {/* Table title */}
      {title && (
        <div
          className="px-4 pt-3 pb-2 text-[12px] font-semibold uppercase tracking-[0.5px] text-[#E8EAED]"
          style={{ borderBottom: "1px solid #2D3139" }}
        >
          {title}
        </div>
      )}

      <table className="w-full border-collapse text-left">
        {/* Header */}
        <thead>
          <tr style={{ background: !title ? "#252830" : "transparent", borderBottom: "1px solid #2D3139" }}>
            {/* spacer for expand chevron */}
            {rows.some((r) => r.detail) && <th className="w-5 pl-3" />}
            {columns.map((col) => (
              <th
                key={col.key}
                className={`px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-[#9AA0A6] whitespace-nowrap ${col.hideOnMobile ? "hidden sm:table-cell" : ""}`}
              >
                {col.label}
              </th>
            ))}
            {hasStatus && (
              <th className="px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-[#9AA0A6]">
                Risk
              </th>
            )}
            {/* actions spacer */}
            <th className="w-16" />
          </tr>
        </thead>

        {/* Body */}
        <tbody>
          {rows.map((row, i) => (
            <InlineRow
              key={row.id}
              row={row}
              columns={columns}
              isLast={i === rows.length - 1}
            />
          ))}
        </tbody>
      </table>
    </motion.div>
  );
}
