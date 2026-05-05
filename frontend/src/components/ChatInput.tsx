"use client";

import { useState, useRef } from "react";
import { Send, Paperclip, X, FileText, Loader2, Scale, User as UserIcon } from "lucide-react";
import { UserType, ContractType, CONTRACT_TYPE_LABELS } from "@/types";

interface ChatInputProps {
  onSend: (message: string, file?: File) => void;
  isStreaming: boolean;
  showRoleSelector?: boolean;
  userType: UserType;
  onUserTypeChange: (type: UserType) => void;
  selectedContractType?: ContractType;
  onStop?: () => void;
}

export default function ChatInput({
  onSend,
  isStreaming,
  showRoleSelector = false,
  userType,
  onUserTypeChange,
  selectedContractType,
  onStop,
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed && !attachedFile) return;
    if (isStreaming) return;

    onSend(trimmed || "Analyze the attached document.", attachedFile || undefined);
    setInput("");
    setAttachedFile(null);

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setAttachedFile(file);
    e.target.value = "";
  };

  const handleTextareaInput = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
    }
  };

  const canSend = (input.trim().length > 0 || attachedFile) && !isStreaming;

  return (
    <div className="px-4 md:px-8 pb-6 pt-2">
      <div className="max-w-3xl mx-auto">
        {/* User role toggle */}
        {showRoleSelector && (
          <div className="mb-3 flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold uppercase text-muted-foreground tracking-wider mr-1">
              I am:
            </span>
            <button
              onClick={() => onUserTypeChange("attorney")}
              className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border transition-all ${
                userType === "attorney"
                  ? "bg-primary/15 border-primary/30 text-primary"
                  : "bg-white/5 border-white/10 text-muted-foreground hover:text-secondary"
              }`}
            >
              <Scale className="w-3.5 h-3.5" /> Attorney
            </button>
            <button
              onClick={() => onUserTypeChange("individual")}
              className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border transition-all ${
                userType === "individual"
                  ? "bg-primary/15 border-primary/30 text-primary"
                  : "bg-white/5 border-white/10 text-muted-foreground hover:text-secondary"
              }`}
            >
              <UserIcon className="w-3.5 h-3.5" /> Individual
            </button>
            {selectedContractType && (
              <span className="ml-auto text-[10px] font-mono text-muted-foreground bg-white/5 px-2 py-1 rounded-md border border-white/10">
                {CONTRACT_TYPE_LABELS[selectedContractType]}
              </span>
            )}
          </div>
        )}

        {/* Attached file preview */}
        {attachedFile && (
          <div className="mb-3 flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-sm w-fit">
            <FileText className="w-4 h-4 text-primary shrink-0" />
            <span className="text-secondary font-medium truncate max-w-[250px]">
              {attachedFile.name}
            </span>
            <span className="text-[11px] text-muted-foreground">
              ({(attachedFile.size / 1024 / 1024).toFixed(1)} MB)
            </span>
            <button
              onClick={() => setAttachedFile(null)}
              className="p-1 rounded-md hover:bg-danger/10 text-muted-foreground hover:text-danger transition-colors ml-1"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Stop Generating Button */}
        {isStreaming && onStop && (
          <div className="flex justify-center mb-3">
            <button
              onClick={onStop}
              className="flex items-center gap-2 px-4 py-2 bg-surface/80 backdrop-blur border border-white/20 text-sm font-medium text-secondary rounded-full shadow-lg hover:bg-white/10 active:scale-95 transition-all"
            >
              <div className="w-2.5 h-2.5 bg-danger rounded-[2px]" />
              Stop generating
            </button>
          </div>
        )}

        {/* Input Container */}
        <div className="relative flex items-end gap-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl px-4 py-3 shadow-[0_8px_30px_rgba(0,0,0,0.3)] focus-within:border-primary/40 focus-within:shadow-[0_8px_30px_rgba(24,86,255,0.1)] transition-all duration-300">
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isStreaming}
            className="shrink-0 p-2 rounded-xl hover:bg-white/10 text-muted-foreground hover:text-secondary transition-colors disabled:opacity-30"
            aria-label="Attach a document"
          >
            <Paperclip className="w-5 h-5" />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.webp,.heic"
            onChange={handleFileChange}
            className="hidden"
          />

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onInput={handleTextareaInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask about a legal document..."
            rows={1}
            disabled={isStreaming}
            className="flex-1 bg-transparent text-secondary placeholder:text-muted-foreground text-sm leading-relaxed resize-none outline-none py-1.5 max-h-40 disabled:opacity-50"
          />

          <button
            onClick={handleSubmit}
            disabled={!canSend}
            className={`shrink-0 p-2.5 rounded-xl transition-all duration-200 ${
              canSend
                ? "bg-primary text-white shadow-lg shadow-primary/20 hover:bg-primary/90 active:scale-95"
                : "bg-white/5 text-muted-foreground cursor-not-allowed"
            }`}
            aria-label="Send message"
          >
            {isStreaming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>

        <p className="text-[10px] text-muted-foreground text-center mt-2 font-mono">
          Fortress AI can make mistakes. Always verify legal advice with a qualified professional.
        </p>
      </div>
    </div>
  );
}
