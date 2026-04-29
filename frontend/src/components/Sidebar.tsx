"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, LayoutDashboard, Database, FileText, Settings } from "lucide-react";
import HardwareMonitor from "./HardwareMonitor";

const NAV_ITEMS = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Vault", href: "/vault", icon: Database },
  { name: "Audit Reports", href: "/reports", icon: FileText },
  { name: "Settings", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-72 border-r border-slate-800 bg-slate-900/80 backdrop-blur-xl flex flex-col hidden md:flex">
      {/* Brand */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800">
        <ShieldCheck className="w-6 h-6 text-emerald-500 mr-3" />
        <span className="font-bold text-lg tracking-wide bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
          FORTRESS AI
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-6 px-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group ${
                isActive 
                  ? "bg-slate-800/50 text-slate-100" 
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/30"
              }`}
            >
              {isActive && (
                <div className="absolute left-0 w-1 h-8 bg-emerald-500 rounded-r-full shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
              )}
              <Icon className={`w-5 h-5 ${isActive ? "text-emerald-500" : "group-hover:text-slate-300"}`} />
              <span className="font-medium text-sm">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Hardware Widget at bottom */}
      <div className="p-4 mt-auto">
        <HardwareMonitor />
      </div>
    </aside>
  );
}
