"use client";

import {
  ShieldCheck,
  MessageSquarePlus,
  Clock,
  Settings,
  FileText,
  PanelLeft,
} from "lucide-react";
import { Conversation, CONTRACT_TYPE_LABELS } from "@/types";
import ChatActionsMenu from "./ChatActionsMenu";

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onRenameConversation?: (id: string, name: string) => void;
  onPinConversation?: (id: string) => void;
  onToggleSidebar?: () => void;
}

const VERDICT_DOT: Record<string, string> = {
  SIGN: "bg-success shadow-[0_0_6px_rgba(7,202,107,0.5)]",
  NEGOTIATE: "bg-warning shadow-[0_0_6px_rgba(232,149,88,0.5)]",
  REJECT: "bg-danger shadow-[0_0_6px_rgba(234,33,67,0.5)]",
  SEEK_COUNSEL: "bg-primary shadow-[0_0_6px_rgba(24,86,255,0.5)]",
};

export default function Sidebar({
  conversations,
  activeConversationId,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
  onRenameConversation,
  onPinConversation,
  onToggleSidebar,
}: SidebarProps) {
  return (
    <aside className="w-72 border-r border-white/10 bg-surface/80 backdrop-blur-2xl flex flex-col hidden md:flex z-20 shadow-[4px_0_24px_rgba(0,0,0,0.2)]">
      {/* Brand */}
      <div className="h-16 flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center mr-3 border border-primary/20 shadow-[0_0_10px_rgba(24,86,255,0.15)]">
            <ShieldCheck className="w-5 h-5 text-primary" />
          </div>
          <span className="font-bold text-lg tracking-wide text-secondary">
            FORTRESS AI
          </span>
        </div>
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="p-1.5 rounded-md hover:bg-white/5 text-muted-foreground transition-colors"
            title="Hide Sidebar (⌘B)"
          >
            <PanelLeft className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* New Analysis Button */}
      <div className="px-4 pt-4 pb-2 shrink-0">
        <button
          onClick={onNewChat}
          className="w-full glass-panel glass-panel-hover rounded-xl px-4 py-2 flex items-center justify-between text-sm font-semibold text-muted-foreground hover:text-secondary transition-all"
        >
          <div className="flex items-center gap-2.5">
            <MessageSquarePlus className="w-4 h-4 text-primary" />
            New Analysis
          </div>
          <kbd className="hidden md:inline-flex items-center gap-1 px-2 py-1 text-[11px] font-mono font-bold rounded-md bg-white/10 text-muted-foreground border border-white/10">
            <span className="text-[13px] leading-none mt-[1px]">⌘</span>K
          </kbd>
        </button>
      </div>

      {/* Conversation History */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-1">
        {conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
            <Clock className="w-5 h-5 mb-2 opacity-50" />
            <p className="text-xs font-medium">No analyses yet</p>
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeConversationId;
            const verdictDot = conv.verdict ? VERDICT_DOT[conv.verdict] : null;
            return (
              <div
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                className={`w-full cursor-pointer text-left flex items-start gap-3 px-3 py-3 rounded-xl transition-all duration-200 group relative ${
                  isActive
                    ? "bg-white/10 border border-white/20 shadow-sm"
                    : "border border-transparent hover:bg-white/5"
                }`}
              >
                <FileText
                  className={`w-4 h-4 mt-0.5 shrink-0 ${
                    isActive ? "text-primary" : "text-muted-foreground"
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    {verdictDot && (
                      <span className={`w-2 h-2 rounded-full shrink-0 ${verdictDot}`} />
                    )}
                    <p
                      className={`text-sm font-medium truncate ${
                        isActive ? "text-secondary" : "text-muted-foreground"
                      }`}
                    >
                      {conv.title}
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    {conv.contractType && (
                      <span className="text-[9px] font-mono text-primary/70 bg-primary/10 px-1.5 py-0.5 rounded border border-primary/15">
                        {CONTRACT_TYPE_LABELS[conv.contractType]}
                      </span>
                    )}
                  </div>
                </div>
                <ChatActionsMenu
                  chatId={conv.id}
                  chatName={conv.title}
                  isPinned={conv.isPinned}
                  onDelete={onDeleteConversation}
                  onRename={onRenameConversation}
                  onPin={onPinConversation}
                />
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-white/10 shrink-0">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-xs font-bold text-primary">
            FA
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-secondary truncate">Fortress AI</p>
            <p className="text-[10px] text-muted-foreground">Contract Risk Assessment</p>
          </div>
          <button className="p-1.5 rounded-lg hover:bg-white/5 text-muted-foreground transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
