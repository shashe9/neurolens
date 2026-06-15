"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useActiveChild } from "./ActiveChildContext";

export const HeaderChildProfile: React.FC = () => {
  const { activeChild, childrenList, selectActiveChild, loading, logout } = useActiveChild();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center gap-4 animate-pulse">
        <div className="text-right hidden sm:block">
          <div className="h-3 w-20 bg-slate-800 rounded mb-1"></div>
          <div className="h-4 w-28 bg-slate-800 rounded"></div>
        </div>
        <div className="h-8 w-8 rounded-full bg-slate-800"></div>
      </div>
    );
  }

  if (!activeChild) {
    return (
      <div className="flex items-center gap-4">
        <div className="text-right hidden sm:block">
          <p className="text-xs text-slate-405">No active profile</p>
        </div>
        <Link
          href="/children"
          className="h-8 px-3 rounded-lg bg-slate-100 hover:bg-slate-205 flex items-center justify-center text-xs font-semibold text-slate-900 shadow transition-colors"
        >
          Set Profile
        </Link>
      </div>
    );
  }

  const dob = new Date(activeChild.date_of_birth);
  const now = new Date();
  const yearsDiff = now.getFullYear() - dob.getFullYear();
  const monthsDiff = now.getMonth() - dob.getMonth();
  let ageMonths = yearsDiff * 12 + monthsDiff;
  if (now.getDate() < dob.getDate()) {
    ageMonths -= 1;
  }
  const ageDisplay = ageMonths >= 0 ? `${ageMonths} Months` : "Newborn";

  const initials = `${activeChild.first_name[0] || ""}${activeChild.last_name[0] || ""}`.toUpperCase();
  const otherChildren = childrenList.filter((c) => c.id !== activeChild.id);

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Profile Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-4 hover:opacity-90 active:scale-[0.98] transition-all text-left focus:outline-none cursor-pointer"
      >
        <div className="text-right hidden sm:block">
          <p className="text-[9px] text-slate-500 font-bold tracking-wider uppercase">Active Profile</p>
          <p className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
            {activeChild.first_name} {activeChild.last_name}
            <span className="text-[10px] text-slate-500 font-normal">({ageDisplay})</span>
            <span className="text-[8px] text-slate-500 select-none">▼</span>
          </p>
        </div>
        <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center font-bold text-xs text-slate-200 select-none">
          {initials}
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2.5 w-60 rounded-xl bg-slate-900 border border-slate-800 p-2.5 shadow-2xl backdrop-blur-md z-50 space-y-2.5 animate-fadeIn">
          {otherChildren.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-[8px] font-bold text-slate-550 uppercase tracking-wider px-2">Switch Profile</p>
              <div className="max-h-36 overflow-y-auto space-y-1">
                {otherChildren.map((c) => {
                  const chInitials = `${c.first_name[0] || ""}${c.last_name[0] || ""}`.toUpperCase();
                  return (
                    <button
                      key={c.id}
                      onClick={() => {
                        selectActiveChild(c.id);
                        setIsOpen(false);
                      }}
                      className="w-full flex items-center gap-2.5 p-1.5 hover:bg-slate-850 rounded-lg text-left transition-colors text-xs text-slate-350 hover:text-slate-200"
                    >
                      <div className="h-6 w-6 rounded-full bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-500">
                        {chInitials}
                      </div>
                      <span className="truncate">{c.first_name} {c.last_name}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {otherChildren.length > 0 && <div className="h-px bg-slate-850"></div>}

          <div className="space-y-1">
            <Link
              href="/children"
              onClick={() => setIsOpen(false)}
              className="w-full flex items-center gap-2 p-1.5 hover:bg-slate-850 rounded-lg text-left transition-colors text-xs text-slate-350 hover:text-slate-200"
            >
              Manage Profiles
            </Link>
            <Link
              href="/children"
              onClick={() => setIsOpen(false)}
              className="w-full flex items-center gap-2 p-1.5 hover:bg-slate-850 rounded-lg text-left transition-colors text-xs text-slate-350 hover:text-slate-200 font-semibold"
            >
              Add New Child
            </Link>
            <button
              onClick={() => {
                setIsOpen(false);
                logout();
              }}
              className="w-full flex items-center gap-2 p-1.5 hover:bg-rose-950/20 rounded-lg text-left transition-colors text-xs text-rose-455 hover:text-rose-350 font-semibold border-t border-slate-850 mt-1 pt-2 cursor-pointer"
            >
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
