"use client";

import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import { MoreVertical, Pencil, Pin, Trash2 } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

interface ChatActionsMenuProps {
  chatId: string;
  chatName: string;
  isPinned?: boolean;
  onRename?: (id: string, newName: string) => void;
  onPin?: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function ChatActionsMenu({
  chatId,
  chatName,
  isPinned = false,
  onRename,
  onPin,
  onDelete,
}: ChatActionsMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [mounted, setMounted] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Click outside to close
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const isActive = isOpen || showDeleteModal;

  return (
    <div className="relative shrink-0" ref={menuRef}>
      <button
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        className={`flex items-center justify-center rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100 ${
          isActive ? "!opacity-100" : ""
        }`}
        style={{
          width: "32px", // Adjusted to fit 20px icon + 6px padding roughly, matching requested size
          height: "32px",
          color: isOpen ? "#E8EAED" : "#9AA0A6",
          backgroundColor: isOpen ? "rgba(255,255,255,0.05)" : "transparent",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.color = "#E8EAED";
        }}
        onMouseLeave={(e) => {
          if (!isOpen) e.currentTarget.style.color = "#9AA0A6";
        }}
        title="More actions"
      >
        <MoreVertical style={{ width: "20px", height: "20px" }} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -5 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -5 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            onClick={(e) => e.stopPropagation()}
            className="absolute z-[60] right-0 top-full mt-1"
            style={{
              width: "200px",
              background: "#1A1D23",
              border: "1px solid #2D3139",
              borderRadius: "12px",
              padding: "8px 0",
              boxShadow: "0 8px 24px rgba(0,0,0,0.3)",
            }}
          >
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsOpen(false);
                onRename?.(chatId, chatName);
              }}
              className="w-full flex items-center px-4 py-2 hover:bg-[#252830] transition-colors"
              style={{ height: "40px", cursor: "pointer" }}
            >
              <Pencil style={{ width: "16px", height: "16px", color: "#9AA0A6" }} />
              <span className="ml-3 text-[13px]" style={{ color: "#E8EAED" }}>
                Edit Chat Name
              </span>
            </button>

            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsOpen(false);
                onPin?.(chatId);
              }}
              className="w-full flex items-center px-4 py-2 hover:bg-[#252830] transition-colors"
              style={{ height: "40px", cursor: "pointer" }}
            >
              <Pin style={{ width: "16px", height: "16px", color: "#9AA0A6", fill: isPinned ? "#9AA0A6" : "transparent" }} />
              <span className="ml-3 text-[13px]" style={{ color: "#E8EAED" }}>
                {isPinned ? "Unpin" : "Pin to Top"}
              </span>
            </button>

            <div style={{ borderTop: "1px solid #2D3139", margin: "8px 0" }} />

            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsOpen(false);
                setShowDeleteModal(true);
              }}
              className="w-full flex items-center px-4 py-2 hover:bg-[#EA4335]/10 transition-colors"
              style={{ height: "40px", cursor: "pointer" }}
            >
              <Trash2 style={{ width: "16px", height: "16px", color: "#EA4335" }} />
              <span className="ml-3 text-[13px]" style={{ color: "#EA4335" }}>
                Delete
              </span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete Confirmation Modal */}
      {mounted && createPortal(
        <AnimatePresence>
          {showDeleteModal && (
            <div className="fixed inset-0 z-[100] flex items-center justify-center">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="absolute inset-0"
                style={{ background: "rgba(0,0,0,0.5)" }}
                onClick={(e) => {
                  e.stopPropagation();
                  setShowDeleteModal(false);
                }}
              />
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="relative z-10 flex flex-col"
                style={{
                  width: "320px",
                  background: "#1A1D23",
                  borderRadius: "16px",
                  padding: "24px",
                }}
                onClick={(e) => e.stopPropagation()}
              >
                <h3 className="font-bold mb-2 text-left" style={{ color: "#E8EAED", fontSize: "16px" }}>
                  Delete Chat?
                </h3>
                <p className="mb-6 leading-relaxed text-left" style={{ color: "#9AA0A6", fontSize: "13px" }}>
                  This will permanently delete this conversation and all attached files.
                </p>
                <div className="flex justify-end gap-3">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowDeleteModal(false);
                    }}
                    className="px-4 py-2 rounded-lg font-medium transition-colors hover:bg-white/5"
                    style={{
                      color: "#9AA0A6",
                      background: "transparent",
                      border: "1px solid #2D3139",
                      fontSize: "13px",
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowDeleteModal(false);
                      onDelete(chatId);
                    }}
                    className="px-4 py-2 rounded-lg font-medium transition-colors hover:brightness-110"
                    style={{
                      color: "#FFFFFF",
                      background: "#EA4335",
                      fontSize: "13px",
                    }}
                  >
                    Delete
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>,
        document.body
      )}
    </div>
  );
}
