"use client";

import React from "react";
import { usePathname } from "next/navigation";

export const Footer: React.FC = () => {
  const pathname = usePathname();

  // Hide footer on the login page
  if (pathname === "/login") {
    return null;
  }

  return (
    <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p>&copy; {new Date().getFullYear()} Neurolens. All rights reserved.</p>
        <p className="text-slate-600">This platform provides developmental context tracking and clinician preparation. It does not perform autism screening or diagnostics.</p>
      </div>
    </footer>
  );
};
