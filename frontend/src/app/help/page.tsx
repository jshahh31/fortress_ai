"use client";

import { useState } from "react";
import Link from "next/link";
import { Search, Rocket, FileCheck, FileText, Scale, User, CreditCard, HelpCircle, MessageCircle } from "lucide-react";
import { motion } from "framer-motion";
import { HELP_DATA } from "@/lib/help-data";

const ICON_MAP: Record<string, typeof Rocket> = {
  Rocket, FileCheck, FileText, Scale, User, CreditCard, HelpCircle, MessageCircle,
};

export default function HelpPage() {
  const [search, setSearch] = useState("");

  const filtered = search.trim()
    ? HELP_DATA.filter(
        (c) =>
          c.title.toLowerCase().includes(search.toLowerCase()) ||
          c.articles.some(
            (a) =>
              a.title.toLowerCase().includes(search.toLowerCase()) ||
              a.body.toLowerCase().includes(search.toLowerCase())
          )
      )
    : HELP_DATA;

  return (
    <div className="py-16">
      {/* Hero */}
      <div className="text-center px-6 mb-14">
        <h1 className="text-3xl md:text-4xl font-extrabold text-secondary mb-4">
          Help Center
        </h1>
        <p className="text-muted-foreground text-base max-w-md mx-auto mb-8">
          Find answers, learn features, and get the most from Fortress AI.
        </p>

        {/* Search */}
        <div className="max-w-lg mx-auto relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search articles..."
            className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-4 py-3.5 text-sm text-secondary placeholder:text-muted-foreground focus:outline-none focus:border-primary/40 focus:shadow-[0_0_15px_rgba(24,86,255,0.1)] transition-all"
          />
        </div>
      </div>

      {/* Category Grid */}
      <div className="max-w-5xl mx-auto px-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {filtered.map((category, i) => {
          const Icon = ICON_MAP[category.icon] || HelpCircle;
          return (
            <motion.div
              key={category.slug}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
            >
              <Link
                href={`/help/${category.slug}`}
                className="glass-panel glass-panel-hover rounded-xl p-5 block h-full group"
              >
                <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center mb-3 group-hover:bg-primary/20 transition-colors">
                  <Icon className="w-5 h-5 text-primary" />
                </div>
                <h3 className="text-sm font-bold text-secondary mb-1">{category.title}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">
                  {category.description}
                </p>
                <p className="text-[10px] font-mono text-primary/70 mt-3">
                  {category.articles.length} article{category.articles.length !== 1 ? "s" : ""}
                </p>
              </Link>
            </motion.div>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16">
          <p className="text-muted-foreground text-sm">No results found for &ldquo;{search}&rdquo;</p>
        </div>
      )}
    </div>
  );
}
