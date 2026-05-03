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
  AnalysisStep,
  CONTRACT_TYPE_LABELS,
  AttachedFile,
} from "@/types";
import { conversationsApi, chatApi } from "@/lib/api";

function genId() {
  return Math.random().toString(36).substring(2, 11);
}

// ── Convert API conversation → frontend Conversation ─────────
function apiConvToLocal(api: import("@/lib/api").ApiConversation): Conversation {
  return {
    id: api.id,
    title: api.title,
    lastMessage: api.lastMessage,
    timestamp: new Date(api.timestamp),
    messages: (api.messages ?? []).map(apiMsgToLocal),
    contractType: api.contractType as ContractType | undefined,
    userType: api.userType as UserType | undefined,
    verdict: api.verdict as Conversation["verdict"],
    isPinned: api.isPinned,
  };
}

function apiMsgToLocal(m: import("@/lib/api").ApiMessage): Message {
  return {
    id: m.id,
    role: m.role as Message["role"],
    content: m.content,
    timestamp: new Date(m.timestamp),
    attachment: m.attachment
      ? { id: m.attachment.id, name: m.attachment.name, size: m.attachment.size, type: m.attachment.type }
      : undefined,
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

  // ── Scroll to bottom on new messages ───────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── Load conversations from backend on mount ────────────────
  useEffect(() => {
    conversationsApi.list().then((list) => {
      setConversations(list.map(apiConvToLocal));
    }).catch(console.error);
  }, []);

  // ── Local helpers ───────────────────────────────────────────
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

  // ── Select a conversation — load messages from backend ──────
  const handleSelectConversation = useCallback(
    async (id: string) => {
      setActiveConversationId(id);
      // If we already have messages locally, no need to refetch
      const existing = conversations.find((c) => c.id === id);
      if (existing && existing.messages.length > 0) return;

      try {
        const full = await conversationsApi.get(id);
        setConversations((prev) =>
          prev.map((c) => (c.id === id ? apiConvToLocal(full) : c))
        );
      } catch (err) {
        console.error("Failed to load conversation:", err);
      }
    },
    [conversations]
  );

  // ── Create new conversation ─────────────────────────────────
  const createNewChat = useCallback(async () => {
    try {
      const api = await conversationsApi.create({ title: "New Analysis" });
      const conv = apiConvToLocal(api);
      setConversations((prev) => [conv, ...prev]);
      setActiveConversationId(conv.id);
    } catch {
      // Fallback: local-only conversation
      const newConv: Conversation = {
        id: genId(), title: "New Analysis", lastMessage: "", timestamp: new Date(), messages: [],
      };
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversationId(newConv.id);
    }
  }, []);

  // ── Global hotkeys ─────────────────────────────────────────
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") { e.preventDefault(); createNewChat(); }
      if ((e.metaKey || e.ctrlKey) && e.key === "b") { e.preventDefault(); setIsSidebarOpen((p) => !p); }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [createNewChat]);

  // ── Run the full audit pipeline (SSE) ───────────────────────
  const runAnalysis = useCallback(
    async (convId: string, contractType: ContractType, _fileName: string) => {
      const steps: AnalysisStep[] = [
        { id: "parsing",    label: "Document Parsing",  description: "Analyzing document structure",        status: "idle" },
        { id: "extraction", label: "Clause Extraction", description: "Identifying key clauses",             status: "idle" },
        { id: "risk",       label: "Risk Analysis",     description: "Evaluating risk levels",              status: "idle" },
        { id: "report",     label: "Report Generation", description: "Synthesizing assessment report",      status: "idle" },
      ];

      const progressMsgId = genId();
      addMessage(convId, {
        id: progressMsgId, role: "assistant", content: "", timestamp: new Date(),
        analysisSteps: [...steps],
      });

      setIsStreaming(true);
      const reportMsgId = genId();
      let reportContent = "";

      try {
        for await (const event of chatApi.audit({
          message: "Please analyze this contract.",
          conversation_id: convId,
          user_type: userType,
          contract_type: contractType,
        })) {
          const ev = event.event as string;
          const data = event.data as Record<string, unknown>;

          if (ev === "steps_init") {
            // Backend sent canonical step list — use it
            const backendSteps = data.steps as Array<{id: string; label: string; description: string}>;
            const fresh = backendSteps.map((s) => ({ ...s, status: "idle" as const }));
            updateMessage(convId, progressMsgId, { analysisSteps: fresh });
          } else if (ev === "step_update") {
            const stepId = data.step_id as string;
            const status = data.status as AnalysisStep["status"];
            updateMessage(convId, progressMsgId, {
              analysisSteps: steps.map((s) => s.id === stepId ? { ...s, status } : s),
            });
            // Keep local steps in sync for next iteration
            const idx = steps.findIndex((s) => s.id === stepId);
            if (idx !== -1) steps[idx].status = status;
          } else if (ev === "content_chunk") {
            const chunk = data.chunk as string;
            reportContent += chunk;
            // Add or update the report message (streamed markdown)
            const existing = activeConversation?.messages.find((m) => m.id === reportMsgId);
            if (!existing) {
              addMessage(convId, {
                id: reportMsgId, role: "assistant", content: reportContent,
                timestamp: new Date(), isStreaming: true,
              });
            } else {
              updateMessage(convId, reportMsgId, { content: reportContent, isStreaming: true });
            }
          } else if (ev === "done") {
            updateMessage(convId, reportMsgId, { isStreaming: false });
            updateConversation(convId, (c) => ({ ...c, contractType }));
          } else if (ev === "error") {
            const errMsg = data.message as string;
            addMessage(convId, {
              id: genId(), role: "assistant",
              content: `⚠️ Analysis error: ${errMsg}`,
              timestamp: new Date(),
            });
          }
        }
      } catch (err) {
        addMessage(convId, {
          id: genId(), role: "assistant",
          content: `⚠️ Failed to connect to analysis service. Please ensure the backend is running.\n\n\`\`\`\n${err}\n\`\`\``,
          timestamp: new Date(),
        });
      } finally {
        setIsStreaming(false);
      }
    },
    [addMessage, updateMessage, updateConversation, userType, activeConversation]
  );

  // ── Handle pending analysis (from Benchmarks page) ──────────
  useEffect(() => {
    const pending = localStorage.getItem("fortress_pending_analysis");
    if (pending) {
      localStorage.removeItem("fortress_pending_analysis");
      const { title, content } = JSON.parse(pending);
      
      const startPending = async () => {
        try {
          const api = await conversationsApi.create({ title });
          const conv = apiConvToLocal(api);
          setConversations((prev) => [conv, ...prev]);
          setActiveConversationId(conv.id);
          
          // Add user message
          addMessage(conv.id, {
            id: genId(), role: "user", content: `Analyze this CUAD contract: ${title}\n\n${content.slice(0, 500)}...`,
            timestamp: new Date()
          });

          // In a real app, we'd upload this content or send it as a special message
          // For now, let's just trigger the analysis on the backend (mocked for demo)
          setTimeout(() => runAnalysis(conv.id, "vendor_agreement", title), 1000);
        } catch (err) {
          console.error("Failed to start pending analysis:", err);
        }
      };
      startPending();
    }
  }, [createNewChat, addMessage, runAnalysis]);

  // ── Remove attached file ────────────────────────────────────
  const handleRemoveFile = useCallback((id: string) => {
    setAttachedFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  // ── Register a file into the panel ─────────────────────────
  const registerFile = useCallback(
    (file: File, msgId: string, thumbnailUrl?: string) => {
      const kb = file.size / 1024;
      const size = kb < 1024 ? `${kb.toFixed(2)} KB` : `${(kb / 1024).toFixed(2)} MB`;
      setAttachedFiles((prev) => [
        {
          id: genId(), name: file.name, size, type: file.type,
          thumbnailUrl, uploadedAt: new Date(), messageId: msgId, source: "upload" as const,
        },
        ...prev,
      ]);
    },
    []
  );

  // ── Handle file upload ──────────────────────────────────────
  const handleUpload = useCallback(
    async (file: File) => {
      // Ensure we have a conversation
      let convId = activeConversationId;
      const title = file.name.replace(/\.[^/.]+$/, "").slice(0, 35);

      if (!convId) {
        try {
          const api = await conversationsApi.create({ title });
          const conv = apiConvToLocal(api);
          setConversations((prev) => [conv, ...prev]);
          setActiveConversationId(conv.id);
          convId = conv.id;
        } catch {
          const newConv: Conversation = {
            id: genId(), title, lastMessage: "", timestamp: new Date(), messages: [],
          };
          setConversations((prev) => [newConv, ...prev]);
          setActiveConversationId(newConv.id);
          convId = newConv.id;
        }
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

      // User message
      addMessage(convId, {
        id: msgId, role: "user",
        content: `Analyze this contract: ${file.name}`,
        timestamp: new Date(),
        attachment: { id: genId(), name: file.name, size: file.size, type: file.type },
      });

      // Upload to backend
      try {
        await chatApi.upload(file, convId);
      } catch (err) {
        console.warn("File upload to backend failed, continuing locally:", err);
      }

      // Detection message + run pipeline
      setTimeout(() => {
        addMessage(convId!, {
          id: genId(), role: "assistant",
          content: `I've received **${file.name}**.\n\nStarting analysis as **${userType === "attorney" ? "an attorney" : "an individual"}**...\n\n*Analyzing now...*`,
          timestamp: new Date(),
        });
        setTimeout(() => runAnalysis(convId!, "vendor_agreement", file.name), 800);
      }, 600);
    },
    [activeConversationId, addMessage, runAnalysis, updateConversation, userType, registerFile]
  );

  // ── Handle contract type chip click ────────────────────────
  const handleContractTypeHint = useCallback(
    async (type: ContractType) => {
      let convId = activeConversationId;
      const title = CONTRACT_TYPE_LABELS[type];

      if (!convId) {
        try {
          const api = await conversationsApi.create({ title, contract_type: type });
          const conv = apiConvToLocal(api);
          setConversations((prev) => [conv, ...prev]);
          setActiveConversationId(conv.id);
          convId = conv.id;
        } catch {
          const newConv: Conversation = {
            id: genId(), title, lastMessage: "", timestamp: new Date(),
            messages: [], contractType: type,
          };
          setConversations((prev) => [newConv, ...prev]);
          setActiveConversationId(newConv.id);
          convId = newConv.id;
        }
      }

      addMessage(convId, {
        id: genId(), role: "user",
        content: `I want to analyze a ${CONTRACT_TYPE_LABELS[type]}.`,
        timestamp: new Date(),
      });

      // Send to backend for a real response
      try {
        const resp = await chatApi.send({
          message: `I want to analyze a ${CONTRACT_TYPE_LABELS[type]}.`,
          conversation_id: convId,
          user_type: userType,
          contract_type: type,
        });
        addMessage(convId, apiMsgToLocal(resp.message));
      } catch {
        // Fallback local message
        setTimeout(() => {
          addMessage(convId!, {
            id: genId(), role: "assistant",
            content: `Great! Please upload your **${CONTRACT_TYPE_LABELS[type]}** document using the 📎 button below, or drag and drop it into the chat.\n\nI'll analyze it and generate a complete **Contract Risk Assessment Report** with:\n- ✅ Verdict (Sign / Negotiate / Reject)\n- 📊 Risk matrix\n- 📄 Clause-by-clause analysis\n- 🚩 Red flags\n- 💡 Recommendations tailored to your role`,
            timestamp: new Date(),
          });
        }, 600);
      }
    },
    [activeConversationId, addMessage, userType]
  );

  // ── Handle chat message send (SSE streaming) ────────────────
  const handleSend = useCallback(
    async (content: string, file?: File) => {
      if (file) { handleUpload(file); return; }

      let convId = activeConversationId;
      if (!convId) {
        try {
          const api = await conversationsApi.create({
            title: content.slice(0, 50) || "New Analysis",
          });
          const conv = apiConvToLocal(api);
          setConversations((prev) => [conv, ...prev]);
          setActiveConversationId(conv.id);
          convId = conv.id;
        } catch {
          const newConv: Conversation = {
            id: genId(),
            title: content.slice(0, 35) + (content.length > 35 ? "..." : ""),
            lastMessage: "", timestamp: new Date(), messages: [],
          };
          setConversations((prev) => [newConv, ...prev]);
          setActiveConversationId(newConv.id);
          convId = newConv.id;
        }
      }

      // Add user message locally
      addMessage(convId, {
        id: genId(), role: "user", content, timestamp: new Date(),
      });

      setIsStreaming(true);
      const assistantMsgId = genId();
      let accumulated = "";

      try {
        let started = false;

        for await (const event of chatApi.stream({
          message: content,
          conversation_id: convId,
          user_type: userType,
          contract_type: activeConversation?.contractType,
        })) {
          const ev = event.event as string;

          if (ev === "start") {
            addMessage(convId!, {
              id: assistantMsgId, role: "assistant",
              content: "", timestamp: new Date(), isStreaming: true,
            });
            started = true;
          } else if (ev === "chunk") {
            if (!started) {
              addMessage(convId!, {
                id: assistantMsgId, role: "assistant",
                content: "", timestamp: new Date(), isStreaming: true,
              });
              started = true;
            }
            accumulated += (event.content as string) ?? "";
            updateMessage(convId!, assistantMsgId, {
              content: accumulated,
              isStreaming: true,
            });
          } else if (ev === "done") {
            updateMessage(convId!, assistantMsgId, { isStreaming: false });
          } else if (ev === "error") {
            updateMessage(convId!, assistantMsgId, {
              content: `⚠️ ${event.message as string}`,
              isStreaming: false,
            });
          }
        }
      } catch (err) {
        addMessage(convId!, {
          id: genId(), role: "assistant",
          content: `⚠️ Connection error. Is the backend running?\n\n\`${err}\``,
          timestamp: new Date(),
        });
      } finally {
        setIsStreaming(false);
      }
    },
    [
      activeConversationId, addMessage, handleUpload, updateMessage,
      userType, activeConversation,
    ]
  );

  // ── Handle export request ───────────────────────────────────
  const handleExportRequest = useCallback(
    (format: "pdf" | "docx") => {
      if (!activeConversationId) return;
      const ext = format;
      const fname = `Fortress_AI_Report.${ext}`;
      addMessage(activeConversationId, {
        id: genId(), role: "assistant",
        content: `Your report has been exported as **${format.toUpperCase()}**. Click below to download.`,
        timestamp: new Date(),
        attachment: { id: genId(), name: fname, size: 245760, type: "download" },
      });
      setAttachedFiles((prev) => [
        {
          id: genId(), name: fname, size: "240 KB",
          type: format === "pdf" ? "application/pdf" : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          uploadedAt: new Date(), source: "generated" as const,
        },
        ...prev,
      ]);
    },
    [activeConversationId, addMessage]
  );

  // ── Delete conversation ─────────────────────────────────────
  const handleDelete = useCallback(
    async (id: string) => {
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) setActiveConversationId(null);
      try {
        await conversationsApi.delete(id);
      } catch (err) {
        console.warn("Backend delete failed:", err);
      }
    },
    [activeConversationId]
  );

  // ── Rename conversation ─────────────────────────────────────
  const handleRename = useCallback(
    async (id: string, currentName: string) => {
      const newName = prompt("Edit Chat Name", currentName);
      if (!newName?.trim()) return;
      updateConversation(id, (c) => ({ ...c, title: newName.trim() }));
      try {
        await conversationsApi.update(id, { title: newName.trim() });
      } catch (err) {
        console.warn("Backend rename failed:", err);
      }
    },
    [updateConversation]
  );

  // ── Pin/Unpin conversation ──────────────────────────────────
  const handlePin = useCallback(
    async (id: string) => {
      const conv = conversations.find((c) => c.id === id);
      const newPinned = !conv?.isPinned;
      updateConversation(id, (c) => ({ ...c, isPinned: newPinned }));
      try {
        await conversationsApi.update(id, { is_pinned: newPinned });
      } catch (err) {
        console.warn("Backend pin failed:", err);
      }
    },
    [conversations, updateConversation]
  );

  const hasMessages = messages.length > 0;
  const contractType = activeConversation?.contractType;

  const sortedConversations = [...conversations].sort((a, b) => {
    if (a.isPinned && !b.isPinned) return -1;
    if (!a.isPinned && b.isPinned) return 1;
    return b.timestamp.getTime() - a.timestamp.getTime();
  });

  return (
    <div className="flex h-full min-h-screen overflow-hidden">
      {isSidebarOpen && (
        <Sidebar
          conversations={sortedConversations}
          activeConversationId={activeConversationId}
          onNewChat={createNewChat}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDelete}
          onRenameConversation={handleRename}
          onPinConversation={handlePin}
          onToggleSidebar={() => setIsSidebarOpen(false)}
        />
      )}

      <main className="flex-1 flex flex-col overflow-hidden relative z-10">
        {/* Floating toggle for empty state */}
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
            <EmptyState onUpload={handleUpload} onContractTypeHint={handleContractTypeHint} />
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
              {!isSidebarOpen && (
                <button
                  onClick={() => setIsSidebarOpen(true)}
                  className="p-1.5 rounded-md hover:bg-white/5 text-muted-foreground transition-colors"
                  title="Show Sidebar (⌘B)"
                >
                  <PanelLeft className="w-5 h-5" />
                </button>
              )}
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
                <AttachedFilesPanel files={attachedFiles} onRemove={handleRemoveFile} />
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
              showRoleSelector={hasMessages}
              selectedContractType={contractType}
            />
          </>
        )}
      </main>
    </div>
  );
}
