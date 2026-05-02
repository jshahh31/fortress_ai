"use client";

/**
 * Custom ReactMarkdown component overrides.
 * Drop these into any <ReactMarkdown components={mdComponents}> to get
 * Kimi-style table rendering inside chat bubbles.
 */

import type { Components } from "react-markdown";
import KimiInlineTable, { InlineTableColumn, InlineTableRow } from "@/components/ui/KimiInlineTable";
import type { InlineRowStatus } from "@/components/ui/KimiInlineTable";
import React from "react";

// ── Helpers ────────────────────────────────────────────────────────────────────

function genId() {
  return Math.random().toString(36).substring(2, 9);
}

const RISK_KEYWORDS: Record<InlineRowStatus, string[]> = {
  critical: ["critical", "uncapped", "unlimited", "severe"],
  high: ["high", "significant", "overbroad", "aggressive"],
  medium: ["medium", "moderate", "unusual", "concern"],
  low: ["low", "standard", "acceptable", "minor"],
};

function inferStatus(text: string): InlineRowStatus | undefined {
  const lower = text.toLowerCase();
  for (const [level, kws] of Object.entries(RISK_KEYWORDS) as [InlineRowStatus, string[]][]) {
    if (kws.some((kw) => lower.includes(kw))) return level;
  }
  return undefined;
}

function getTextContent(node: React.ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(getTextContent).join("");
  if (React.isValidElement(node)) return getTextContent((node.props as { children?: React.ReactNode }).children);
  return "";
}

// ── Table context ──────────────────────────────────────────────────────────────
// We collect thead/tbody data via a shared object built during render.

// ReactMarkdown renders table → thead → tbody → tr → th/td sequentially,
// so we use a mutable accumulator captured by closure per table render.

type TableAccumulator = {
  headers: string[];
  rows: { cells: string[]; raw: string }[];
};

// ── Markdown components ────────────────────────────────────────────────────────

export function buildMdComponents(delay = 200): Components {
  return {
    // ── TABLE ──────────────────────────────────────────────────────────────────
    table({ children }) {
      const acc: TableAccumulator = { headers: [], rows: [] };

      // Walk children to extract thead/tbody
      React.Children.forEach(children, (section) => {
        if (!React.isValidElement(section)) return;
        const sectionEl = section as React.ReactElement<{ children?: React.ReactNode }>;

        React.Children.forEach(sectionEl.props.children, (row) => {
          if (!React.isValidElement(row)) return;
          const rowEl = row as React.ReactElement<{ children?: React.ReactNode }>;
          const cells: string[] = [];

          React.Children.forEach(rowEl.props.children, (cell) => {
            cells.push(getTextContent((cell as React.ReactElement<{ children?: React.ReactNode }>)?.props?.children ?? ""));
          });

          // Detect if this came from thead by checking the parent type
          const type = (sectionEl.type as string | { displayName?: string; name?: string })?.toString?.() ?? "";
          if (type.includes("head") || (acc.headers.length === 0 && acc.rows.length === 0)) {
            if (acc.headers.length === 0) {
              acc.headers = cells;
            } else {
              acc.rows.push({ cells, raw: cells.join(" ") });
            }
          } else {
            acc.rows.push({ cells, raw: cells.join(" ") });
          }
        });
      });

      // Build KimiInlineTable props
      const columns: InlineTableColumn[] = acc.headers.map((h, i) => ({
        key: String(i),
        label: h,
        hideOnMobile: i > 1,
      }));

      const rows: InlineTableRow[] = acc.rows.map((r) => ({
        id: genId(),
        cells: r.cells,
        status: inferStatus(r.raw),
        copyValue: r.raw,
      }));

      if (columns.length === 0 || rows.length === 0) {
        // Fallback to plain table if parsing fails
        return (
          <div className="overflow-x-auto my-3">
            <table className="w-full text-sm border-collapse">{children}</table>
          </div>
        );
      }

      return <KimiInlineTable columns={columns} rows={rows} delay={delay} />;
    },

    // ── Suppress default thead/tbody/tr/th/td when inside our table override
    // (they won't be called since we intercept at `table` level)

    // ── CODE ───────────────────────────────────────────────────────────────────
    code({ children, className }) {
      const isBlock = className?.includes("language-");
      if (isBlock) {
        return (
          <pre className="my-2 bg-black/30 border border-white/10 rounded-lg p-3 overflow-x-auto">
            <code className="text-[12px] font-mono text-[#E8EAED]">{children}</code>
          </pre>
        );
      }
      return (
        <code className="bg-white/10 text-[#8AB4F8] text-[12px] font-mono px-1.5 py-0.5 rounded">
          {children}
        </code>
      );
    },

    // ── BLOCKQUOTE ─────────────────────────────────────────────────────────────
    blockquote({ children }) {
      return (
        <blockquote className="border-l-2 border-[#8AB4F8] pl-3 my-2 text-[#9AA0A6] italic">
          {children}
        </blockquote>
      );
    },
  };
}

/** Ready-to-use component map for chat assistant bubbles */
export const CHAT_MD_COMPONENTS = buildMdComponents(200);
