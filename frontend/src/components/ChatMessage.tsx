"use client";

import { motion } from "framer-motion";
import { Bot, User, FileText, Loader2, Download, Copy, ThumbsUp, ThumbsDown, Check } from "lucide-react";
import { useState } from "react";
import { Message } from "@/types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import ReportView from "@/components/report/ReportView";
import AnalysisProgress from "@/components/report/AnalysisProgress";
import { CHAT_MD_COMPONENTS } from "@/lib/mdComponents";

interface ChatMessageProps {
  message: Message;
  userType?: "attorney" | "individual";
  onRequestExport?: (format: "pdf" | "docx") => void;
}

export default function ChatMessage({ message, userType, onRequestExport }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  const isSystem = message.role === "system";
  const hasReport = !!message.report;
  const hasAnalysis = !!message.analysisSteps;
  const [copied, setCopied] = useState(false);

  // System messages (confirmations, etc.)
  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="flex justify-center py-3 px-4 md:px-8"
      >
        <div className="max-w-md text-center px-4 py-2 rounded-full border text-xs text-muted-foreground">
          {message.content}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`flex gap-4 py-5 px-4 md:px-8 group ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {/* Avatar — Assistant */}
      {isAssistant && (
        <div className="shrink-0 w-8 h-8 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center shadow-[0_0_10px_rgba(24,86,255,0.15)] mt-1">
          <Bot className="w-4 h-4 text-primary" />
        </div>
      )}

      {/* Content */}
      <div className={`min-w-0 ${isUser ? "max-w-[75%]" : "max-w-[85%] flex-1"}`}>
        {/* Attachment badge */}
        {message.attachment && (
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-medium text-muted-foreground">
            {message.attachment.type === 'download' ? (
              <Download className="w-3.5 h-3.5 text-success" />
            ) : (
              <FileText className="w-3.5 h-3.5 text-primary" />
            )}
            <span className="truncate max-w-[250px]">{message.attachment.name}</span>
            {message.attachment.size > 0 && (
              <span className="text-[10px] opacity-60">
                {(message.attachment.size / 1024 / 1024).toFixed(1)} MB
              </span>
            )}
          </div>
        )}

        {/* Analysis progress */}
        {hasAnalysis && !hasReport && (
          <AnalysisProgress steps={message.analysisSteps!} />
        )}

        {/* Report view */}
        {hasReport && (
          <ReportView
            report={message.report!}
            userType={userType}
            onRequestExport={onRequestExport}
          />
        )}

        {/* Regular text bubble */}
        {!hasReport && !hasAnalysis && (
          <div
            className={`rounded-2xl px-5 py-3 text-sm leading-relaxed ${
              isUser
                ? "bg-[#292929] text-white border border-white/10 shadow-sm rounded-br-md"
                : "text-secondary rounded-bl-md"
            }`}
          >
            {message.isStreaming && !message.content ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-xs font-medium">Analyzing document...</span>
              </div>
            ) : isAssistant ? (
              <div className="prose prose-invert prose-sm max-w-none [&>p]:mb-2 [&>p:last-child]:mb-0 [&>ul]:mt-1 [&>ol]:mt-1 [&_strong]:text-secondary [&_a]:text-[#8AB4F8] [&_h1]:text-base [&_h2]:text-sm [&_h3]:text-sm">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={CHAT_MD_COMPONENTS}>{message.content}</ReactMarkdown>
                {message.isStreaming && (
                  <span className="inline-block w-2 h-4 bg-primary animate-pulse ml-1 align-middle rounded-sm" />
                )}
              </div>
            ) : (
              <p>{message.content}</p>
            )}
          </div>
        )}

        {/* Message Actions (Assistant only) */}
        {isAssistant && !message.isStreaming && (
          <div className="flex items-center gap-1 ml-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <button
              onClick={() => {
                navigator.clipboard.writeText(message.content || "");
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              }}
              className="px-1.5 rounded-md text-muted-foreground hover:text-secondary hover:bg-white/5 transition-all"
              title="Copy message"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-success" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
            <button
              className="p-1.5 rounded-md text-muted-foreground hover:text-secondary hover:bg-white/5 transition-all"
              title="Helpful"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>
            <button
              className="p-1.5 rounded-md text-muted-foreground hover:text-secondary hover:bg-white/5 transition-all"
              title="Not helpful"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Timestamp */}
        {!hasAnalysis && (
          <p className={`text-[10px] text-muted-foreground ml-4.5 font-mono ${isUser ? "text-right" : "text-left"}`}>
            {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </p>
        )}
      </div>

      {/* Avatar — User */}
      {isUser && (
        <div className="shrink-0 w-8 h-8 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center mt-1">
          <User className="w-4 h-4 text-secondary" />
        </div>
      )}
    </motion.div>
  );
}
