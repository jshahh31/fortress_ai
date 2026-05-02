"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { PanelLeft } from "lucide-react";
import Sidebar from "@/components/Sidebar";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import EmptyState from "@/components/EmptyState";
import AttachedFilesPanel from "@/components/AttachedFilesPanel";
import {
  Message,
  Conversation,
  ContractType,
  UserType,
  ContractReport,
  AnalysisStep,
  CONTRACT_TYPE_LABELS,
  AttachedFile,
} from "@/types";

function genId() {
  return Math.random().toString(36).substring(2, 11);
}

// ────────────────────────────────────────────────────────────
// Simulated Contract Report (matches the full product spec)
// ────────────────────────────────────────────────────────────
function buildSimulatedReport(contractType: ContractType): ContractReport {
  return {
    verdict: "NEGOTIATE",
    contractType,
    executiveSummary:
      "This contract contains several provisions that deviate from industry standards. While the core terms are reasonable, three clauses present significant risk that should be addressed before signing. The indemnification clause is uncapped, the auto-renewal terms are aggressive, and the intellectual property assignment language is overly broad. We recommend negotiating these terms before execution.",
    riskMatrix: {
      critical: [
        {
          id: genId(),
          clause: "Indemnification",
          section: "4.2",
          level: "critical",
          description:
            "The indemnification obligation is uncapped and one-sided. The Receiving Party bears unlimited liability for any breach, including indirect and consequential damages. This represents significant and potentially unlimited financial exposure.",
          originalText:
            "The Receiving Party shall indemnify, defend, and hold harmless the Disclosing Party from and against any and all claims, losses, damages, liabilities, and expenses, including reasonable attorney's fees, arising out of or relating to any breach of this Agreement.",
          industryStandard:
            "Standard practice limits indemnification to direct damages with a cap equal to 12 months of fees paid under the agreement. Consequential and indirect damages are typically mutually excluded.",
          suggestion:
            "The Receiving Party's total aggregate liability under this Section shall not exceed the total fees paid by Receiving Party during the twelve (12) months preceding the claim. In no event shall either party be liable for indirect, incidental, or consequential damages.",
        },
      ],
      high: [
        {
          id: genId(),
          clause: "Auto-Renewal & Termination",
          section: "7.1",
          level: "high",
          description:
            "The agreement auto-renews for successive one-year terms with a 90-day written notice requirement to opt out. This is significantly longer than the industry standard 30-day notice period and could result in unintended contract lock-in.",
          originalText:
            "This Agreement shall automatically renew for successive one (1) year terms unless either party provides written notice of non-renewal at least ninety (90) days prior to the expiration of the then-current term.",
          industryStandard:
            "Most agreements of this type require 30 days written notice for non-renewal.",
          suggestion:
            "Replace '90 days' with '30 days' and add a provision for month-to-month conversion after the initial term.",
        },
        {
          id: genId(),
          clause: "Intellectual Property Assignment",
          section: "5.3",
          level: "high",
          description:
            "The IP assignment clause broadly assigns all work product, including pre-existing IP and independently developed materials, to the Disclosing Party. This overreach could strip the Receiving Party of rights to their own background IP.",
          originalText:
            "All work product, inventions, and materials created in connection with this Agreement, including any pre-existing intellectual property incorporated therein, shall be the sole and exclusive property of the Disclosing Party.",
          industryStandard:
            "IP assignments typically apply only to work product created specifically under the agreement, with explicit carve-outs for pre-existing IP and a license-back provision.",
          suggestion:
            "Add: 'Notwithstanding the foregoing, Receiving Party retains all rights to its pre-existing intellectual property. Any pre-existing IP incorporated into work product shall be subject to a perpetual, royalty-free license to the Disclosing Party.'",
        },
      ],
      medium: [
        {
          id: genId(),
          clause: "Confidentiality Duration",
          section: "3.1",
          level: "medium",
          description:
            "Confidentiality obligations survive in perpetuity, which is unusual for this type of agreement. While this protects trade secrets, it creates an indefinite compliance burden.",
          industryStandard:
            "Most NDAs and service agreements set a 2-5 year post-termination confidentiality period, with exceptions for trade secrets.",
          suggestion:
            "Limit confidentiality obligations to three (3) years following termination, except for trade secrets which shall remain confidential for as long as they qualify as such.",
        },
      ],
      low: [
        {
          id: genId(),
          clause: "Governing Law",
          section: "9.1",
          level: "low",
          description:
            "Jurisdiction is set to the State of Delaware. This is a standard and favorable choice for U.S.-based commercial agreements.",
          industryStandard: "Delaware is the most common choice for U.S. commercial contracts.",
        },
        {
          id: genId(),
          clause: "Force Majeure",
          section: "10.2",
          level: "low",
          description:
            "Standard force majeure clause covering acts of God, government action, and natural disasters. No notable concerns.",
          industryStandard: "This clause is standard and balanced.",
        },
      ],
    },
    redFlags: [
      {
        id: genId(),
        title: "Uncapped Indemnification",
        description:
          "One-sided, uncapped indemnification with no mutual obligation creates severe financial risk. This is the highest-priority item to negotiate.",
        section: "4.2",
        severity: "critical",
      },
      {
        id: genId(),
        title: "Overbroad IP Assignment",
        description:
          "Pre-existing intellectual property is swept into the assignment clause. This could result in loss of proprietary tools, frameworks, or methodologies.",
        section: "5.3",
        severity: "high",
      },
    ],
    recommendations: [
      {
        id: genId(),
        forAttorneys:
          "Draft a redline of Section 4.2 proposing a mutual liability cap at 12× monthly fees with a carve-out for willful misconduct. For Section 5.3, add a pre-existing IP schedule and license-back provision. Consider proposing binding arbitration as an alternative to litigation.",
        forIndividuals:
          "This contract has some important issues to fix before you sign. The biggest concern is that you could be held responsible for unlimited costs if something goes wrong (Section 4.2). You should also make sure the contract doesn't accidentally give away rights to your existing work (Section 5.3). Ask the other party to limit your financial risk and clarify what intellectual property you keep.",
      },
      {
        id: genId(),
        forAttorneys:
          "Negotiate Section 7.1 notice period from 90 to 30 days. Consider requesting a mutual termination for convenience with 60-day notice after the initial term. Review insurance coverage to ensure it aligns with remaining indemnification exposure.",
        forIndividuals:
          "The contract auto-renews every year, and you need to give 3 months notice to stop it — that's unusual. Most contracts only need 30 days notice. Ask for a shorter notice period so you don't accidentally get locked in for another year.",
      },
    ],
    appendix: {
      glossary: [
        { term: "Indemnification", definition: "A contractual obligation to compensate another party for losses or damages." },
        { term: "Force Majeure", definition: "An unforeseeable event that prevents a party from fulfilling contractual obligations." },
        { term: "Work Product", definition: "Any output, materials, or deliverables created during the performance of the agreement." },
        { term: "Consequential Damages", definition: "Indirect losses resulting from a breach, such as lost profits or business opportunities." },
      ],
      legalReferences: [
        { title: "UCC § 2-719", citation: "Limitation of Damages — Uniform Commercial Code" },
        { title: "Restatement (Second) of Contracts § 356", citation: "Liquidated Damages and Penalties" },
        { title: "DTSA", citation: "Defend Trade Secrets Act of 2016, 18 U.S.C. §§ 1836-1839" },
      ],
      benchmarks: [
        { metric: "Liability Cap", value: "Uncapped", comparison: "12× monthly fee (avg.)" },
        { metric: "Non-Renewal Notice", value: "90 days", comparison: "30 days (avg.)" },
        { metric: "Confidentiality Period", value: "Perpetual", comparison: "3-5 years (avg.)" },
        { metric: "IP Assignment Scope", value: "All + Pre-existing", comparison: "Work Product only (std.)" },
      ],
    },
  };
}

// ────────────────────────────────────────────────────────────
// Main Page
// ────────────────────────────────────────────────────────────
export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [userType, setUserType] = useState<UserType>("individual");
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeConversation = conversations.find((c) => c.id === activeConversationId);
  const messages = activeConversation?.messages ?? [];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── Helpers ──────────────────────────────────────────────
  const updateConversation = useCallback(
    (id: string, updater: (c: Conversation) => Conversation) => {
      setConversations((prev) => prev.map((c) => (c.id === id ? updater(c) : c)));
    },
    []
  );

  const addMessage = useCallback(
    (convId: string, msg: Message) => {
      updateConversation(convId, (c) => ({
        ...c,
        messages: [...c.messages, msg],
        lastMessage: msg.content.slice(0, 60),
        timestamp: new Date(),
      }));
    },
    [updateConversation]
  );

  const updateMessage = useCallback(
    (convId: string, msgId: string, updates: Partial<Message>) => {
      updateConversation(convId, (c) => ({
        ...c,
        messages: c.messages.map((m) => (m.id === msgId ? { ...m, ...updates } : m)),
      }));
    },
    [updateConversation]
  );

  // ── Create new conversation ─────────────────────────────
  const createNewChat = useCallback(() => {
    const newConv: Conversation = {
      id: genId(), title: "New Analysis", lastMessage: "", timestamp: new Date(), messages: [],
    };
    setConversations((prev) => [newConv, ...prev]);
    setActiveConversationId(newConv.id);
  }, []);

  // ── Global Hotkeys ─────────────────────────────────────────
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        createNewChat();
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "b") {
        e.preventDefault();
        setIsSidebarOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [createNewChat]);

  // ── Run the full analysis pipeline ──────────────────────
  const runAnalysis = useCallback(
    (convId: string, contractType: ContractType, fileName: string) => {
      const steps: AnalysisStep[] = [
        { id: genId(), label: "Parse", description: "Reading document", status: "idle" },
        { id: genId(), label: "Extract", description: "Identifying clauses", status: "idle" },
        { id: genId(), label: "Assess", description: "Evaluating risks", status: "idle" },
        { id: genId(), label: "Report", description: "Generating report", status: "idle" },
      ];

      // Add progress message
      const progressMsgId = genId();
      addMessage(convId, {
        id: progressMsgId,
        role: "assistant",
        content: "",
        timestamp: new Date(),
        analysisSteps: [...steps],
      });

      setIsStreaming(true);
      let stepIndex = 0;

      const interval = setInterval(() => {
        if (stepIndex < steps.length) {
          // Mark current as processing
          steps[stepIndex].status = "processing";
          if (stepIndex > 0) steps[stepIndex - 1].status = "completed";
          updateMessage(convId, progressMsgId, { analysisSteps: [...steps] });
          stepIndex++;
        } else {
          // All done — mark last as completed
          steps[steps.length - 1].status = "completed";
          updateMessage(convId, progressMsgId, { analysisSteps: [...steps] });
          clearInterval(interval);

          // After short delay, add the report message
          setTimeout(() => {
            const report = buildSimulatedReport(contractType);

            addMessage(convId, {
              id: genId(),
              role: "assistant",
              content: "",
              timestamp: new Date(),
              report,
            });

            // Update conversation with verdict
            updateConversation(convId, (c) => ({ ...c, verdict: report.verdict, contractType }));

            // Add a follow-up markdown message
            setTimeout(() => {
              const tableAttorney = `| Clause | Section | Risk | Priority |
|---|---|---|---|
| Indemnification | §4.2 | Critical — uncapped exposure | Negotiate immediately |
| IP Assignment | §5.3 | High — overbroad scope | Add carve-out |
| Auto-Renewal Notice | §7.1 | High — 90-day lock-in | Reduce to 30 days |
| Confidentiality Duration | §3.1 | Medium — perpetual obligation | Limit to 3 years |`;
              const tableIndividual = `| Issue | Severity | Plain-English Summary |
|---|---|---|
| Unlimited liability | Critical | You could owe unlimited money |
| IP rights grab | High | Your existing work may be affected |
| 90-day cancel notice | High | Very hard to exit the contract |
| Perpetual confidentiality | Medium | You must keep secrets forever |`;
              const followUpContent = userType === "attorney"
                ? `The analysis is complete. I've identified **3 critical/high-risk clauses** that require immediate attention in your negotiation strategy.\n\n${tableAttorney}\n\nWould you like me to:\n\n1. Draft redline language for the indemnification cap?\n2. Prepare a negotiation memo for the IP assignment carve-outs?\n3. Generate a comparison with industry-standard terms?\n\nYou can also download this report as **PDF** or **DOCX**.`
                : `Your contract analysis is ready! Here's a quick summary of what was found:\n\n${tableIndividual}\n\n⚠️ **Don't sign yet** — address the top two issues first. Would you like me to explain any clause in plain English?\n\nYou can download this report as **PDF** or **DOCX**.`;

              addMessage(convId, {
                id: genId(),
                role: "assistant",
                content: followUpContent,
                timestamp: new Date(),
              });

              setIsStreaming(false);
            }, 500);
          }, 600);
        }
      }, 1200);
    },
    [addMessage, updateMessage, updateConversation, userType]
  );

  // ── Remove attached file ────────────────────────────────
  const handleRemoveFile = useCallback((id: string) => {
    setAttachedFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  // ── Register a file into the panel ──────────────────────
  const registerFile = useCallback(
    (file: File, msgId: string, thumbnailUrl?: string) => {
      const kb = file.size / 1024;
      const size = kb < 1024 ? `${kb.toFixed(2)} KB` : `${(kb / 1024).toFixed(2)} MB`;
      setAttachedFiles((prev) => [
        {
          id: genId(),
          name: file.name,
          size,
          type: file.type,
          thumbnailUrl,
          uploadedAt: new Date(),
          messageId: msgId,
          source: "upload" as const,
        },
        ...prev,
      ]);
    },
    []
  );

  // ── Handle file upload from EmptyState ──────────────────
  const handleUpload = useCallback(
    (file: File) => {
      let convId = activeConversationId;
      const title = file.name.replace(/\.[^/.]+$/, "").slice(0, 35);

      if (!convId) {
        const newConv: Conversation = {
          id: genId(), title, lastMessage: "", timestamp: new Date(), messages: [],
        };
        setConversations((prev) => [newConv, ...prev]);
        setActiveConversationId(newConv.id);
        convId = newConv.id;
      } else {
        updateConversation(convId, (c) => ({ ...c, title }));
      }

      // Register in files panel
      const msgId = genId();
      if (file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = (ev) => registerFile(file, msgId, ev.target?.result as string);
        reader.readAsDataURL(file);
      } else {
        registerFile(file, msgId);
      }

      // User upload message
      addMessage(convId, {
        id: msgId,
        role: "user",
        content: `Analyze this contract: ${file.name}`,
        timestamp: new Date(),
        attachment: { id: genId(), name: file.name, size: file.size, type: file.type },
      });

      // System detection message
      setTimeout(() => {
        addMessage(convId!, {
          id: genId(),
          role: "assistant",
          content: `I've received **${file.name}**. I've auto-detected this as a **Vendor / Service Agreement**.\n\nStarting analysis as **${userType === "attorney" ? "an attorney" : "an individual"}**. You can change your role using the toggle below the input field.\n\n*Analyzing now...*`,
          timestamp: new Date(),
        });

        // Start pipeline
        setTimeout(() => runAnalysis(convId!, "vendor_agreement", file.name), 1000);
      }, 800);
    },
    [activeConversationId, addMessage, runAnalysis, updateConversation, userType]
  );

  // ── Handle contract type chip click ─────────────────────
  const handleContractTypeHint = useCallback(
    (type: ContractType) => {
      let convId = activeConversationId;
      const title = CONTRACT_TYPE_LABELS[type];

      if (!convId) {
        const newConv: Conversation = {
          id: genId(), title, lastMessage: "", timestamp: new Date(), messages: [], contractType: type,
        };
        setConversations((prev) => [newConv, ...prev]);
        setActiveConversationId(newConv.id);
        convId = newConv.id;
      }

      addMessage(convId, {
        id: genId(),
        role: "user",
        content: `I want to analyze a ${CONTRACT_TYPE_LABELS[type]}.`,
        timestamp: new Date(),
      });

      setTimeout(() => {
        addMessage(convId!, {
          id: genId(),
          role: "assistant",
          content: `Great! Please upload your **${CONTRACT_TYPE_LABELS[type]}** document using the 📎 button below, or drag and drop it into the chat.\n\nI'll analyze it and generate a complete **Contract Risk Assessment Report** with:\n- ✅ Verdict (Sign / Negotiate / Reject)\n- 📊 Risk matrix\n- 📄 Clause-by-clause analysis\n- 🚩 Red flags\n- 💡 Recommendations tailored to your role`,
          timestamp: new Date(),
        });
      }, 600);
    },
    [activeConversationId, addMessage]
  );

  // ── Handle chat message send ────────────────────────────
  const handleSend = useCallback(
    (content: string, file?: File) => {
      // If file is attached, treat as new analysis
      if (file) {
        handleUpload(file);
        return;
      }

      let convId = activeConversationId;
      if (!convId) {
        const newConv: Conversation = {
          id: genId(),
          title: content.slice(0, 35) + (content.length > 35 ? "..." : ""),
          lastMessage: "", timestamp: new Date(), messages: [],
        };
        setConversations((prev) => [newConv, ...prev]);
        setActiveConversationId(newConv.id);
        convId = newConv.id;
      }

      addMessage(convId, {
        id: genId(), role: "user", content, timestamp: new Date(),
      });

      setIsStreaming(true);

      // Check if requesting export
      const lc = content.toLowerCase();
      const wantsPdf = lc.includes("pdf");
      const wantsDocx = lc.includes("docx") || lc.includes("word");

      if (wantsPdf || wantsDocx) {
        const format = wantsPdf ? "PDF" : "DOCX";
        const targetId = convId;
        setTimeout(() => {
          addMessage(targetId, {
            id: genId(),
            role: "assistant",
            content: `Here's your report exported as **${format}**. Click the file below to download.`,
            timestamp: new Date(),
            attachment: {
              id: genId(),
              name: `Fortress_AI_Report.${format.toLowerCase()}`,
              size: 245760,
              type: "download",
            },
          });
          setIsStreaming(false);
        }, 1500);
        return;
      }

      // Generic follow-up response
      const targetId = convId;
      const response = userType === "attorney"
        ? "Based on the analysis, I'd recommend focusing your negotiation on the indemnification cap first — that's the highest-leverage change. Here's a suggested approach:\n\n1. **Lead with the cap**: Propose mutual liability capped at 12× monthly fees\n2. **Package with IP carve-outs**: Frame the pre-existing IP protection as a standard safeguard\n3. **Concede on jurisdiction**: Delaware governance is favorable, so this can be a goodwill concession\n\nWould you like me to draft the specific redline language for any of these?"
        : "Good question! Here's what that means in plain terms:\n\nRight now, the contract says you could owe the other party **unlimited money** if something goes wrong. That's unusual — most contracts have a limit (called a \"cap\").\n\n**What you should do:**\n1. Ask the other party to add a dollar limit on what you could owe\n2. A reasonable limit would be equal to what you've paid them over the past year\n3. Both sides should have the same limits (it should be \"mutual\")\n\nWould you like me to help you write a message to the other party asking for these changes?";

      const assistantMsgId = genId();
      addMessage(targetId, {
        id: assistantMsgId, role: "assistant", content: "", timestamp: new Date(), isStreaming: true,
      });

      let charIdx = 0;
      const interval = setInterval(() => {
        const chunk = Math.floor(Math.random() * 8) + 3;
        charIdx = Math.min(charIdx + chunk, response.length);
        const done = charIdx >= response.length;
        updateMessage(targetId, assistantMsgId, {
          content: response.slice(0, charIdx),
          isStreaming: !done,
        });
        if (done) {
          clearInterval(interval);
          setIsStreaming(false);
        }
      }, 20);
    },
    [activeConversationId, addMessage, handleUpload, updateMessage, userType]
  );

  // ── Handle export request from ReportView ───────────────
  const handleExportRequest = useCallback(
    (format: "pdf" | "docx") => {
      if (!activeConversationId) return;
      const convId = activeConversationId;
      const ext = format === "pdf" ? "pdf" : "docx";
      const fname = `Fortress_AI_Report.${ext}`;

      addMessage(convId, {
        id: genId(),
        role: "assistant",
        content: `Your report has been exported as **${format.toUpperCase()}**. Click below to download.`,
        timestamp: new Date(),
        attachment: {
          id: genId(),
          name: fname,
          size: 245760,
          type: "download",
        },
      });

      // Register in the files panel as AI-generated
      setAttachedFiles((prev) => [
        {
          id: genId(),
          name: fname,
          size: "240 KB",
          type: format === "pdf" ? "application/pdf" : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          uploadedAt: new Date(),
          source: "generated" as const,
        },
        ...prev,
      ]);
    },
    [activeConversationId, addMessage]
  );

  // ── Delete conversation ─────────────────────────────────
  const handleDelete = useCallback(
    (id: string) => {
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) setActiveConversationId(null);
    },
    [activeConversationId]
  );

  const hasMessages = messages.length > 0;
  const showRoleSelector = hasMessages;
  const contractType = activeConversation?.contractType;

  return (
    <div className="flex h-full min-h-screen overflow-hidden">
      {isSidebarOpen && (
        <Sidebar
          conversations={conversations}
          activeConversationId={activeConversationId}
          onNewChat={createNewChat}
          onSelectConversation={setActiveConversationId}
          onDeleteConversation={handleDelete}
        />
      )}

      <main className="flex-1 flex flex-col overflow-hidden relative z-10">
        {/* Floating Toggle Button for Empty State */}
        {!isSidebarOpen && !hasMessages && (
          <div className="absolute top-4 left-6 z-20">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 rounded-lg bg-surface/60 backdrop-blur-xl border border-white/10 text-muted-foreground hover:text-secondary transition-colors shadow-lg"
              title="Toggle Sidebar (⌘B)"
            >
              <PanelLeft className="w-5 h-5" />
            </button>
          </div>
        )}

        {!hasMessages ? (
          <>
            <EmptyState
              onUpload={handleUpload}
              onContractTypeHint={handleContractTypeHint}
            />
            <ChatInput
              onSend={handleSend}
              isStreaming={isStreaming}
              userType={userType}
              onUserTypeChange={setUserType}
              showRoleSelector={false}
            />
          </>
        ) : (
          <>
            {/* Header */}
            <div className="h-14 border-b border-white/10 bg-surface/60 backdrop-blur-xl flex items-center px-4 shrink-0 gap-3">
              <button
                onClick={() => setIsSidebarOpen((prev) => !prev)}
                className="p-1.5 rounded-md hover:bg-white/5 text-muted-foreground transition-colors"
                title="Toggle Sidebar (⌘B)"
              >
                <PanelLeft className="w-5 h-5" />
              </button>
              <h2 className="text-sm font-bold text-secondary truncate">
                {activeConversation?.title}
              </h2>
              {contractType && (
                <span className="ml-3 text-[9px] font-mono text-primary/80 bg-primary/10 px-2 py-0.5 rounded-md border border-primary/15">
                  {CONTRACT_TYPE_LABELS[contractType]}
                </span>
              )}
              <div className="ml-auto flex items-center gap-3">
                {isStreaming && (
                  <span className="flex items-center gap-1.5 text-[10px] font-mono font-bold text-primary uppercase tracking-wider">
                    <span className="w-2 h-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(24,86,255,0.5)]" />
                    Analyzing
                  </span>
                )}
                <AttachedFilesPanel
                  files={attachedFiles}
                  onRemove={handleRemoveFile}
                />
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto">
              <div className="max-w-3xl mx-auto">
                {messages.map((msg) => (
                  <ChatMessage
                    key={msg.id}
                    message={msg}
                    userType={userType}
                    onRequestExport={handleExportRequest}
                  />
                ))}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input */}
            <ChatInput
              onSend={handleSend}
              isStreaming={isStreaming}
              userType={userType}
              onUserTypeChange={setUserType}
              showRoleSelector={showRoleSelector}
              selectedContractType={contractType}
            />
          </>
        )}
      </main>
    </div>
  );
}
