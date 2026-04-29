"use client";

import { useState } from "react";
import { UploadCloud, Lock, UnlockKeyhole, FileIcon, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function VaultUpload({ onUpload }: { onUpload?: (file: File) => void }) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "application/pdf") {
        setFile(droppedFile);
        onUpload?.(droppedFile);
      }
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">The Vault</h2>
        <span className="text-[10px] text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20 font-mono">SECURE UPLOAD</span>
      </div>

      <div 
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative flex-1 flex flex-col items-center justify-center border-2 border-dashed rounded-lg transition-all duration-300 ${
          isDragging ? "border-emerald-500 bg-emerald-500/5" : "border-slate-700 bg-slate-900/50 hover:border-slate-600"
        }`}
      >
        <AnimatePresence mode="wait">
          {!file ? (
            <motion.div 
              key="empty"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center pointer-events-none"
            >
              <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-4">
                {isDragging ? (
                  <UnlockKeyhole className="w-8 h-8 text-emerald-400" />
                ) : (
                  <Lock className="w-8 h-8 text-slate-400" />
                )}
              </div>
              <p className="text-slate-300 font-medium">Drag & Drop Legal PDF</p>
              <p className="text-slate-500 text-xs mt-2">End-to-end encrypted before processing</p>
            </motion.div>
          ) : (
            <motion.div
              key="filled"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center p-6 w-full max-w-sm"
            >
              <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-4">
                <FileIcon className="w-8 h-8 text-emerald-400" />
              </div>
              <p className="text-slate-200 font-medium truncate w-full text-center">{file.name}</p>
              <p className="text-slate-500 text-xs mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              
              <button 
                onClick={() => setFile(null)}
                className="mt-6 flex items-center gap-2 text-xs text-slate-400 hover:text-red-400 transition-colors"
              >
                <X className="w-3 h-3" /> Remove File
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {isDragging && (
          <div className="absolute inset-0 rounded-lg pointer-events-none shadow-[inset_0_0_20px_rgba(16,185,129,0.2)]" />
        )}
      </div>
    </div>
  );
}
