"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown, AlertTriangle, BookOpen, Scale, FileText } from "lucide-react";
import { ContractReport, RiskItem, UserType } from "@/types";
import VerdictBanner from "./VerdictBanner";
import RiskMatrix from "./RiskMatrix";
import ClauseCard from "./ClauseCard";
import KimiInlineTable from "@/components/ui/KimiInlineTable";

interface ReportViewProps {
  report: ContractReport;
  userType?: UserType;
  onRequestExport?: (format: 'pdf' | 'docx') => void;
}

function Section({
  title,
  icon: Icon,
  children,
  defaultOpen = true,
}: {
  title: string;
  icon: typeof AlertTriangle;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.02] backdrop-blur-md overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-3 px-5 py-3.5 text-left hover:bg-white/5 transition-colors"
      >
        <Icon className="w-4 h-4 text-primary shrink-0" />
        <span className="text-xs font-mono font-bold uppercase tracking-wider text-secondary flex-1">
          {title}
        </span>
        <ChevronDown
          className={`w-4 h-4 text-muted-foreground transition-transform duration-200 ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>
      {isOpen && <div className="px-5 pb-5 pt-1">{children}</div>}
    </div>
  );
}

export default function ReportView({ report, userType = "individual", onRequestExport }: ReportViewProps) {
  // Collect all risk items for clause-by-clause view
  const allClauses: RiskItem[] = [
    ...report.riskMatrix.critical,
    ...report.riskMatrix.high,
    ...report.riskMatrix.medium,
    ...report.riskMatrix.low,
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="space-y-4 w-full"
    >
      {/* 1. Verdict */}
      <VerdictBanner verdict={report.verdict} />

      {/* 2. Executive Summary */}
      <Section title="Executive Summary" icon={BookOpen}>
        <p className="text-sm text-secondary leading-relaxed">{report.executiveSummary}</p>
      </Section>

      {/* 3. Risk Matrix */}
      <Section title="Risk Matrix" icon={AlertTriangle}>
        <RiskMatrix matrix={report.riskMatrix} />
      </Section>

      {/* 3.5. Analysis Coverage (Phase 2) */}
      {report.validation?.coverage && (
        <Section title="Analysis Coverage" icon={Scale}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-xs text-muted-foreground mb-1">Sections Analyzed</p>
              <p className="text-2xl font-bold text-secondary">
                {report.validation.coverage.analyzed_sections}/{report.validation.coverage.total_sections}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {report.validation.coverage.section_coverage_pct}% coverage
              </p>
            </div>
            
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-xs text-muted-foreground mb-1">Key Clauses</p>
              <p className="text-2xl font-bold text-secondary">
                {report.validation.coverage.covered_key_sections}/{report.validation.coverage.key_clause_sections}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {report.validation.coverage.key_clause_coverage_pct}% covered
              </p>
            </div>
          </div>
          
          {/* Missing Key Clauses */}
          {report.validation.coverage.missing_key_clauses && report.validation.coverage.missing_key_clauses.length > 0 && (
            <div className="mt-4">
              <p className="text-xs font-mono font-bold uppercase text-muted-foreground tracking-wider mb-2">
                Key Clauses Not Analyzed
              </p>
              <div className="space-y-2">
                {report.validation.coverage.missing_key_clauses.slice(0, 5).map((clause) => (
                  <div key={clause.section} className="flex items-center gap-2 text-xs text-muted-foreground p-2 rounded bg-white/5">
                    <span className="font-mono">§{clause.section}</span>
                    <span>•</span>
                    <span className="flex-1">{clause.title}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 border border-white/10">
                      {clause.type}
                    </span>
                    <span className="ml-auto">p.{clause.page}</span>
                  </div>
                ))}
                {report.validation.coverage.missing_key_clauses.length > 5 && (
                  <p className="text-xs text-muted-foreground/60 italic">
                    ... and {report.validation.coverage.missing_key_clauses.length - 5} more
                  </p>
                )}
              </div>
            </div>
          )}
        </Section>
      )}

      {/* 4. Clause-by-Clause Analysis */}
      <Section title="Clause-by-Clause Analysis" icon={FileText}>
        <div className="space-y-2">
          {allClauses.map((item, i) => (
            <ClauseCard key={item.id} item={item} index={i} />
          ))}
        </div>
      </Section>

      {/* 5. Red Flags */}
      {report.redFlags.length > 0 && (
        <Section title="Red Flags" icon={AlertTriangle} defaultOpen={true}>
          <div className="space-y-3">
            {report.redFlags.map((flag) => (
              <div
                key={flag.id}
                className="flex items-start gap-3 p-3 rounded-lg bg-danger/5 border border-danger/10"
              >
                <span className="w-2 h-2 rounded-full bg-danger mt-1.5 shrink-0 shadow-[0_0_6px_rgba(234,33,67,0.5)]" />
                <div>
                  <p className="text-sm font-semibold text-secondary">
                    {flag.title} <span className="text-muted-foreground font-normal">— §{flag.section}</span>
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                    {flag.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* 6. Recommendations */}
      {report.recommendations.length > 0 && (
        <Section title="Recommendations" icon={Scale}>
          <div className="space-y-3">
            {report.recommendations.map((rec) => (
              <div key={rec.id} className="rounded-lg border border-white/5 overflow-hidden">
                <div className="p-3 bg-white/[0.02]">
                  <p className="text-[10px] font-mono font-bold uppercase text-primary tracking-wider mb-1">
                    {userType === "attorney" ? "For Attorneys" : "For Individuals"}
                  </p>
                  <p className="text-sm text-secondary leading-relaxed">
                    {userType === "attorney" ? rec.forAttorneys : rec.forIndividuals}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* 7. Appendix */}
      <Section title="Appendix" icon={BookOpen} defaultOpen={false}>
        <div className="space-y-4">
          {/* Glossary */}
          {report.appendix.glossary.length > 0 && (
            <div>
              <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-2">
                Defined Terms
              </p>
              <div className="space-y-1.5">
                {report.appendix.glossary.map((g, i) => (
                  <div key={i} className="flex gap-2 text-xs">
                    <span className="font-semibold text-secondary shrink-0">{g.term}:</span>
                    <span className="text-muted-foreground">{g.definition}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* References */}
          {report.appendix.legalReferences.length > 0 && (
            <div>
              <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-2">
                Legal References
              </p>
              <ul className="space-y-1">
                {report.appendix.legalReferences.map((r, i) => (
                  <li key={i} className="text-xs text-muted-foreground">
                    <span className="text-secondary font-medium">{r.title}</span> — {r.citation}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Benchmarks */}
          {report.appendix.benchmarks.length > 0 && (
            <div>
              <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-2">
                Contract Benchmarks
              </p>
              <KimiInlineTable
                columns={[
                  { key: "metric", label: "Metric" },
                  { key: "value", label: "This Contract" },
                  { key: "comparison", label: "Industry Avg." },
                ]}
                rows={report.appendix.benchmarks.map((b, i) => ({
                  id: String(i),
                  cells: [b.metric, b.value, b.comparison],
                  copyValue: `${b.metric}: ${b.value} (industry: ${b.comparison})`,
                }))}
                delay={0}
              />
            </div>
          )}

          {/* Section Evidence & Quotes */}
          {report.appendix.evidence && report.appendix.evidence.length > 0 && (
            <div>
              <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-2">
                Section Evidence & Exact Quotes
              </p>
              <div className="space-y-2">
                {report.appendix.evidence.map((ev, i) => (
                  <div key={i} className="text-xs p-2 rounded bg-white/5 border border-white/10">
                    <p className="text-secondary font-semibold mb-1">
                      §{ev.section}{ev.page && ` • p.${ev.page}`}{ev.title ? ` • ${ev.title}` : ""}
                    </p>
                    <p className="text-muted-foreground italic">&ldquo;{ev.quote}&rdquo;</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* RAG Sources */}
          {report.appendix.sources && report.appendix.sources.length > 0 && (
            <div>
              <p className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mb-2">
                RAG SOURCES & REFERENCES
              </p>
              <div className="space-y-2">
                {report.appendix.sources.map((source, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs p-2 rounded bg-white/5">
                    <span className="font-mono text-primary/80 w-8 shrink-0">
                      {source.type === 'legal' ? '📜' :
                       source.type === 'industry' ? '📊' :
                       source.type === 'academic' ? '🎓' : '🔗'}
                    </span>
                    <div className="flex-1">
                      <p className="font-medium text-secondary">{source.title}</p>
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary/80 text-[10px] hover:underline break-all"
                      >
                        {source.url.replace(/^https?:\/\//, '')}
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </Section>

      {/* Download prompt */}
      {onRequestExport && (
        <div className="flex items-center gap-2 pt-2">
          <p className="text-xs text-muted-foreground">Export report:</p>
          <button
            onClick={() => onRequestExport("pdf")}
            className="glass-button-secondary text-xs px-3 py-1.5 rounded-lg font-semibold"
          >
            📄 PDF
          </button>
          <button
            onClick={() => onRequestExport("docx")}
            className="glass-button-secondary text-xs px-3 py-1.5 rounded-lg font-semibold"
          >
            📝 DOCX
          </button>
        </div>
      )}
    </motion.div>
  );
}
