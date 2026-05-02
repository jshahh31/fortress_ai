"use client";

import { useState } from "react";
import { ChevronRight, Copy, Download, Eye, Check } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

// ── Types ────────────────────────────────────────────────────

export type KimiRowStatus = "critical" | "high" | "medium" | "low";

export interface KimiTableAction {
  label: string;
  icon: "copy" | "download" | "view";
  onClick: () => void;
}

export interface KimiTableRow {
  id: string;
  primary: string;
  secondary?: string;
  status?: KimiRowStatus;
  /** Extra columns for column-based tables */
  cells?: string[];
  /** If provided, renders an expanded detail area */
  expandedContent?: React.ReactNode;
  actions?: KimiTableAction[];
}

export interface KimiTableColumn {
  key: string;
  label: string;
  sticky?: boolean;
}

interface KimiTableProps {
  columns?: KimiTableColumn[];
  rows: KimiTableRow[];
  caption?: string;
  /** If true, primary/secondary are the first two columns rather than a stacked cell */
  columnMode?: boolean;
}

// ── Status config ─────────────────────────────────────────────

const STATUS_CONFIG: Record<
  KimiRowStatus,
  { label: string; badge: string; dot: string; icon: string }
> = {
  critical: {
    label: "Critical",
    badge: "bg-[rgba(234,67,53,0.10)] text-[#EA4335] border-[rgba(234,67,53,0.20)]",
    dot: "bg-[#EA4335] shadow-[0_0_6px_rgba(234,67,53,0.5)]",
    icon: "🔴",
  },
  high: {
    label: "High",
    badge: "bg-[rgba(251,188,4,0.10)] text-[#FBBC04] border-[rgba(251,188,4,0.20)]",
    dot: "bg-[#FBBC04] shadow-[0_0_6px_rgba(251,188,4,0.5)]",
    icon: "🟠",
  },
  medium: {
    label: "Medium",
    badge: "bg-[rgba(245,166,35,0.10)] text-[#F5A623] border-[rgba(245,166,35,0.20)]",
    dot: "bg-[#F5A623] shadow-[0_0_6px_rgba(245,166,35,0.5)]",
    icon: "🟡",
  },
  low: {
    label: "Low",
    badge: "bg-[rgba(52,168,83,0.10)] text-[#34A853] border-[rgba(52,168,83,0.20)]",
    dot: "bg-[#34A853] shadow-[0_0_6px_rgba(52,168,83,0.5)]",
    icon: "🟢",
  },
};

// ── Action button ─────────────────────────────────────────────

function ActionBtn({ action }: { action: KimiTableAction }) {
  const [copied, setCopied] = useState(false);

  const handleClick = () => {
    action.onClick();
    if (action.icon === "copy") {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  const Icon =
    action.icon === "copy"
      ? copied
        ? Check
        : Copy
      : action.icon === "download"
        ? Download
        : Eye;

  return (
    <button
      onClick={(e) => { e.stopPropagation(); handleClick(); }}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#252830] text-[#9AA0A6] text-[11px] font-medium transition-colors duration-150 hover:text-[#E8EAED] border border-white/5"
    >
      <Icon className="w-3 h-3" />
      {copied ? "Copied!" : action.label}
    </button>
  );
}

// ── Row component ─────────────────────────────────────────────

function KimiRow({
  row,
  columns,
  columnMode,
  isLast,
}: {
  row: KimiTableRow;
  columns?: KimiTableColumn[];
  columnMode?: boolean;
  isLast: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const hasExpand = !!row.expandedContent;
  const cfg = row.status ? STATUS_CONFIG[row.status] : null;

  return (
    <>
      <tr
        onClick={hasExpand ? () => setExpanded((v) => !v) : undefined}
        className={`group relative transition-colors duration-200 ${!isLast ? "border-b border-[#2D3139]" : ""
          } ${hasExpand ? "cursor-pointer" : ""} hover:bg-[#252830]`}
      >
        {/* Expand chevron */}
        {hasExpand && (
          <td className="pl-4 pr-0 py-4 w-6 shrink-0">
            <ChevronRight
              className={`w-4 h-4 text-[#9AA0A6] transition-transform duration-200 ${expanded ? "rotate-90" : ""
                }`}
            />
          </td>
        )}

        {/* Column mode: render each cell */}
        {columnMode && row.cells
          ? row.cells.map((cell, ci) => (
            <td
              key={ci}
              className={`px-4 py-4 text-[14px] text-[#E8EAED] leading-snug whitespace-nowrap ${ci === 0 && columns?.[0]?.sticky ? "sticky left-0 bg-[#1A1D23] group-hover:bg-[#252830] transition-colors" : ""
                }`}
            >
              {cell}
            </td>
          ))
          : /* Primary + secondary stacked cell */
          !columnMode && (
            <td
              className={`px-4 py-4 ${hasExpand ? "pl-2" : ""}`}
            >
              <p className="text-[14px] font-medium text-[#E8EAED] leading-snug">
                {row.primary}
              </p>
              {row.secondary && (
                <p className="text-[13px] text-[#9AA0A6] mt-0.5 leading-relaxed">
                  {row.secondary}
                </p>
              )}
            </td>
          )}

        {/* Status badge */}
        {cfg && (
          <td className="px-4 py-4 whitespace-nowrap">
            <span
              className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[12px] font-semibold border ${cfg.badge}`}
              style={{ borderRadius: 4 }}
            >
              <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${cfg.dot}`} />
              {cfg.label}
            </span>
          </td>
        )}

        {/* Hover actions */}
        {row.actions && row.actions.length > 0 && (
          <td className="px-4 py-4 whitespace-nowrap">
            <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              {row.actions.map((a) => (
                <ActionBtn key={a.label} action={a} />
              ))}
            </div>
          </td>
        )}
      </tr>

      {/* Expanded row */}
      {hasExpand && (
        <AnimatePresence>
          {expanded && (
            <motion.tr
              key="expanded"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <td
                colSpan={
                  (columns?.length ?? 1) +
                  (cfg ? 1 : 0) +
                  (row.actions ? 1 : 0) +
                  (hasExpand ? 1 : 0)
                }
                className={`${!isLast ? "border-b border-[#2D3139]" : ""}`}
              >
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: "auto" }}
                  exit={{ height: 0 }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                  className="overflow-hidden"
                >
                  <div className="bg-[#0F1419] px-4 py-4 text-[13px] text-[#9AA0A6] leading-relaxed">
                    {row.expandedContent}
                  </div>
                </motion.div>
              </td>
            </motion.tr>
          )}
        </AnimatePresence>
      )}
    </>
  );
}

// ── Main component ─────────────────────────────────────────────

export default function KimiTable({
  columns,
  rows,
  caption,
  columnMode = false,
}: KimiTableProps) {
  const hasStatus = rows.some((r) => r.status);
  const hasActions = rows.some((r) => r.actions && r.actions.length > 0);
  const hasExpand = rows.some((r) => r.expandedContent);

  return (
    <div
      className="w-full overflow-x-auto rounded-xl"
      style={{
        background: "#1A1D23",
        border: "1px solid #2D3139",
        borderRadius: 12,
      }}
    >
      <table className="w-full border-collapse min-w-full">
        {caption && (
          <caption className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#9AA0A6] text-left px-4 pt-3 pb-1">
            {caption}
          </caption>
        )}

        {/* Header */}
        {columns && columns.length > 0 && (
          <thead>
            <tr className="border-b border-[#2D3139]" style={{ background: "#252830" }}>
              {hasExpand && <th className="w-6 pl-4" />}
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-4 py-3 text-left text-[12px] font-semibold uppercase tracking-wider text-[#9AA0A6] whitespace-nowrap ${col.sticky ? "sticky left-0 bg-[#252830]" : ""
                    }`}
                >
                  {col.label}
                </th>
              ))}
              {hasStatus && <th className="px-4 py-3 text-left text-[12px] font-semibold uppercase tracking-wider text-[#9AA0A6]">Risk</th>}
              {hasActions && <th className="px-4 py-3 w-32" />}
            </tr>
          </thead>
        )}

        {/* Body */}
        <tbody>
          {rows.map((row, i) => (
            <KimiRow
              key={row.id}
              row={row}
              columns={columns}
              columnMode={columnMode}
              isLast={i === rows.length - 1}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
