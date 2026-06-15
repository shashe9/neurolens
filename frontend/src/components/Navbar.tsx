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

  const isActive = (path: string) => pathname === path;

  const linkClass = (path: string) => 
    `transition-colors py-1 text-sm font-semibold border-b-2 ${
      isActive(path)
        ? "text-indigo-600 border-indigo-600 font-bold"
        : "text-slate-200 hover:text-indigo-600 border-transparent hover:border-indigo-200 font-semibold"
    }`;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-white/95 backdrop-blur-md shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8 w-full md:w-auto">
          <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight text-slate-50 hover:opacity-95 transition-opacity">
            <span>neurolens</span>
            <span className="text-sm font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-100">Companion</span>
          </Link>
          
          {token && (
            <nav className="hidden md:flex items-center gap-6 text-sm">
              {/* Main Section */}
              <div className="flex items-center gap-5 border-r border-slate-750 pr-5">
                <Link href="/dashboard" className={linkClass("/dashboard")}>Home</Link>
                <Link href="/observations" className={linkClass("/observations")}>Journal</Link>
                <Link href="/milestones" className={linkClass("/milestones")}>Growth Journey</Link>
                <Link href="/learn" className={linkClass("/learn")}>Learn</Link>
              </div>
              
              {/* Secondary Section */}
              <div className="flex items-center gap-5">
                <Link href="/visit" className={linkClass("/visit")}>Visit Prep</Link>
                <Link href="/report" className={linkClass("/report")}>Reports</Link>
              </div>
            </nav>
          )}
        </div>
        
        {token && <HeaderChildProfile />}
      </div>
    </header>
  );
};
