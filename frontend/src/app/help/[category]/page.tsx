"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ChevronDown, ArrowLeft } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { HELP_DATA } from "@/lib/help-data";

export default function HelpCategoryPage() {
  const params = useParams();
  const slug = params.category as string;
  const category = HELP_DATA.find((c) => c.slug === slug);
  const [openId, setOpenId] = useState<string | null>(null);

  if (!category) {
    return (
      <div className="py-24 text-center">
        <h1 className="text-2xl font-extrabold text-secondary mb-2">Category not found</h1>
        <Link href="/help" className="text-sm text-primary hover:text-primary/80 transition-colors">← Back to Help Center</Link>
      </div>
    );
  }

  return (
    <div className="py-16 max-w-3xl mx-auto px-6">
      <Link href="/help" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-secondary mb-8 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Help Center
      </Link>

      <h1 className="text-2xl md:text-3xl font-extrabold text-secondary mb-2">{category.title}</h1>
      <p className="text-sm text-muted-foreground mb-10">{category.description}</p>

      <div className="space-y-3">
        {category.articles.map((article) => {
          const isOpen = openId === article.id;
          return (
            <div key={article.id} className="rounded-xl border border-white/10 bg-white/[0.02] backdrop-blur-md overflow-hidden">
              <button onClick={() => setOpenId(isOpen ? null : article.id)}
                className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-white/5 transition-colors">
                <span className="text-sm font-semibold text-secondary pr-4">{article.title}</span>
                <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform duration-200 shrink-0 ${isOpen ? "rotate-180" : ""}`} />
              </button>
              <AnimatePresence>
                {isOpen && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }} className="overflow-hidden">
                    <div className="px-5 pb-5 pt-1 border-t border-white/5">
                      <div className="prose prose-invert prose-sm max-w-none [&>p]:mb-3 [&_strong]:text-secondary [&_code]:bg-white/10 [&_code]:px-1 [&_code]:rounded">
                        <ReactMarkdown>{article.body}</ReactMarkdown>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </div>
  );
}
