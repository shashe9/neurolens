"use client";

import React from "react";
import { useActiveChild } from "./ActiveChildContext";

export const HeaderChildProfile: React.FC = () => {
  const { activeChild, loading } = useActiveChild();

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
          <p className="text-xs text-slate-400">No active profile</p>
        </div>
        <div className="h-8 w-8 rounded-full bg-slate-800 flex items-center justify-center text-xs text-slate-500 font-bold">
          --
        </div>
      </div>
    );
  }

  // Calculate age in months
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

  return (
    <div className="flex items-center gap-4">
      <div className="text-right hidden sm:block">
        <p className="text-xs text-slate-400">Active child profile:</p>
        <p className="text-sm font-semibold text-slate-200">
          {activeChild.first_name} {activeChild.last_name} ({ageDisplay})
        </p>
      </div>
      <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center font-bold text-xs shadow-lg shadow-indigo-500/20 text-white select-none">
        {initials}
      </div>
    </div>
  );
};
