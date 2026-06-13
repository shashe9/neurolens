"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { HeaderChildProfile } from "./HeaderChildProfile";
import { useActiveChild } from "./ActiveChildContext";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const { token } = useActiveChild();

  // Hide the navbar entirely on the login page
  if (pathname === "/login") {
    return null;
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent hover:opacity-95 transition-opacity">
            <span>neurolens</span>
            <span className="text-xs px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/25">V1</span>
          </Link>
          
          {token && (
            <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
              <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
              <Link href="/observations" className="hover:text-white transition-colors">Log Observation</Link>
              <Link href="/milestones" className="hover:text-white transition-colors">Review Milestones</Link>
              <Link href="/visit" className="hover:text-white transition-colors">Prepare Visit</Link>
              <Link href="/report" className="hover:text-white transition-colors">Generate Report</Link>
              <Link href="/judge" className="hover:text-indigo-300 text-indigo-400 transition-colors">⚖️ Judge Portal</Link>

            </nav>
          )}
        </div>
        
        {token && <HeaderChildProfile />}
      </div>
    </header>
  );
};
