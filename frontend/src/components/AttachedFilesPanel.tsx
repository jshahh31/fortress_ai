"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Paperclip,
  FileText,
  Download,
  X,
  Link2,
  ImageIcon,
} from "lucide-react";
import { AttachedFile } from "@/types";

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatBytes(raw: string | number): string {
  if (typeof raw === "string") return raw;
  if (raw < 1024) return `${raw} B`;
  if (raw < 1024 * 1024) return `${(raw / 1024).toFixed(2)} KB`;
  return `${(raw / 1024 / 1024).toFixed(2)} MB`;
}

function isImageType(mime: string) {
  return /^image\//.test(mime);
}

function fileTypeLabel(mime: string) {
  if (mime.includes("pdf")) return "PDF";
  if (mime.includes("word") || mime.includes("docx")) return "DOC";
  if (mime.includes("text")) return "TXT";
  return mime.split("/")[1]?.toUpperCase().slice(0, 4) ?? "FILE";
}

// ── Thumbnail ─────────────────────────────────────────────────────────────────

function FileThumbnail({ file }: { file: AttachedFile }) {
  if (isImageType(file.type) && file.thumbnailUrl) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={file.thumbnailUrl}
        alt={file.name}
        className="w-10 h-10 rounded-md object-cover shrink-0"
        style={{ background: "#0F1419" }}
      />
    );
  }

  const isImg = isImageType(file.type);
  return (
    <div
      className="w-10 h-10 rounded-md shrink-0 flex flex-col items-center justify-center gap-0.5"
      style={{ background: "#0F1419", borderRadius: 6 }}
    >
      {isImg ? (
        <ImageIcon className="w-4 h-4" style={{ color: "#5F6368" }} />
      ) : (
        <>
          <FileText className="w-4 h-4" style={{ color: "#5F6368" }} />
          <span className="text-[8px] font-bold" style={{ color: "#5F6368" }}>
            {fileTypeLabel(file.type)}
          </span>
        </>
      )}
    </div>
  );
}

// ── FileRow ───────────────────────────────────────────────────────────────────

function FileRow({
  file,
  onRemove,
  isLast,
}: {
  file: AttachedFile;
  onRemove: (id: string) => void;
  isLast: boolean;
}) {
  const [hovered, setHovered] = useState(false);

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (file.thumbnailUrl) {
      const a = document.createElement("a");
      a.href = file.thumbnailUrl;
      a.download = file.name;
      a.click();
    }
  };

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="flex items-center gap-3 px-2 transition-colors duration-150 rounded-lg"
      style={{
        paddingTop: 10,
        paddingBottom: 10,
        borderBottom: isLast ? "none" : "1px solid #2D3139",
        background: hovered ? "#252830" : "transparent",
        cursor: "default",
      }}
    >
      {/* Thumbnail */}
      <FileThumbnail file={file} />

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 min-w-0">
          <p
            className="text-[13px] font-medium truncate"
            style={{ color: "#E8EAED" }}
          >
            {file.name}
          </p>
          {file.source === "shared" && (
            <Link2 className="w-3 h-3 shrink-0" style={{ color: "#5F6368" }} />
          )}
          {file.source === "generated" && (
            <span
              className="text-[9px] font-bold px-1 py-0.5 rounded shrink-0"
              style={{
                background: "rgba(138,180,248,0.1)",
                color: "#8AB4F8",
                border: "1px solid rgba(138,180,248,0.2)",
              }}
            >
              AI
            </span>
          )}
        </div>
        <p className="text-[11px] mt-0.5" style={{ color: "#5F6368" }}>
          {formatBytes(file.size)}
        </p>
      </div>

      {/* Actions — visible on hover */}
      <div
        className="flex items-center gap-1 transition-opacity duration-150 shrink-0"
        style={{ opacity: hovered ? 1 : 0 }}
      >
        {file.thumbnailUrl && (
          <button
            onClick={handleDownload}
            aria-label="Download file"
            className="p-1.5 rounded-md transition-colors duration-150"
            style={{ color: "#9AA0A6" }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.color = "#E8EAED")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.color = "#9AA0A6")
            }
          >
            <Download className="w-3.5 h-3.5" />
          </button>
        )}
        <button
          onClick={(e) => { e.stopPropagation(); onRemove(file.id); }}
          aria-label="Remove file"
          className="p-1.5 rounded-md transition-colors duration-150"
          style={{ color: "#9AA0A6" }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.color = "#EA4335")
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.color = "#9AA0A6")
          }
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}

// ── Empty state ───────────────────────────────────────────────────────────────

function EmptyFiles() {
  return (
    <div className="flex flex-col items-center justify-center py-8 gap-2">
      <Paperclip className="w-8 h-8" style={{ color: "#5F6368" }} />
      <p className="text-[13px]" style={{ color: "#9AA0A6" }}>
        No files attached
      </p>
      <p className="text-[12px]" style={{ color: "#5F6368" }}>
        Upload files to see them here
      </p>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

interface AttachedFilesPanelProps {
  files: AttachedFile[];
  onRemove: (id: string) => void;
}

export default function AttachedFilesPanel({
  files,
  onRemove,
}: AttachedFilesPanelProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const count = files.length;

  // Close on outside click or ESC
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    const onClick = (e: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onClick);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("mousedown", onClick);
    };
  }, [open]);

  const toggle = useCallback(() => setOpen((v) => !v), []);

  return (
    <div ref={containerRef} className="relative">
      {/* Trigger button */}
      <button
        onClick={toggle}
        aria-label={`${count} attached file${count !== 1 ? "s" : ""}`}
        aria-expanded={open}
        className="relative flex items-center justify-center rounded-lg transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8AB4F8]"
        style={{
          width: 36,
          height: 36,
          color: open ? "#E8EAED" : "#9AA0A6",
          background: open ? "#252830" : "transparent",
        }}
        onMouseEnter={(e) => {
          if (!open) (e.currentTarget as HTMLElement).style.color = "#E8EAED";
        }}
        onMouseLeave={(e) => {
          if (!open) (e.currentTarget as HTMLElement).style.color = "#9AA0A6";
        }}
      >
        <Paperclip className="w-5 h-5" />

        {/* Badge */}
        <AnimatePresence>
          {count > 0 && (
            <motion.span
              key="badge"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 18 }}
              className="absolute -top-1.5 -right-1.5 min-w-[16px] h-4 px-1 flex items-center justify-center text-[10px] font-semibold rounded-full"
              style={{
                background: "#2D3139",
                color: "#E8EAED",
                border: "1px solid rgba(255,255,255,0.08)",
              }}
            >
              {count > 99 ? "99+" : count}
            </motion.span>
          )}
        </AnimatePresence>
      </button>

      {/* Panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            key="panel"
            initial={{ opacity: 0, y: -6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.97 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="absolute right-0 top-[calc(100%+8px)] z-50"
            style={{
              width: 280,
              background: "#1A1D23",
              border: "1px solid #2D3139",
              borderRadius: 12,
              boxShadow: "0 8px 24px rgba(0,0,0,0.3)",
            }}
          >
            {/* Panel header */}
            <div
              className="px-3 pt-3 pb-3 flex items-center justify-between"
              style={{ borderBottom: "1px solid #2D3139" }}
            >
              <span
                className="text-[14px] font-semibold"
                style={{ color: "#E8EAED" }}
              >
                {count > 0 ? `${count} File${count !== 1 ? "s" : ""}` : "Attached Files"}
              </span>
              <button
                onClick={() => setOpen(false)}
                className="p-1 rounded transition-colors duration-150"
                style={{ color: "#5F6368" }}
                onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLElement).style.color = "#9AA0A6")
                }
                onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLElement).style.color = "#5F6368")
                }
                aria-label="Close files panel"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* File list */}
            <div
              className="overflow-y-auto px-1"
              style={{ maxHeight: 400, paddingTop: 4, paddingBottom: 8 }}
            >
              {count === 0 ? (
                <EmptyFiles />
              ) : (
                files.map((file, i) => (
                  <FileRow
                    key={file.id}
                    file={file}
                    onRemove={onRemove}
                    isLast={i === files.length - 1}
                  />
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
