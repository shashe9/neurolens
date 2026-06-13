import React from "react";

export const ResponsibleAINotice: React.FC = () => {
  return (
    <div className="bg-slate-900/40 border border-amber-500/20 rounded-2xl p-4 sm:p-5 flex items-start gap-4 backdrop-blur-sm max-w-4xl mx-auto shadow-md">
      <div className="text-xl sm:text-2xl bg-amber-500/10 text-amber-500 p-2.5 rounded-xl select-none flex-shrink-0 animate-pulse">
        ⚠️
      </div>
      <div className="space-y-1">
        <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400">
          Responsible AI Clinical Disclaimer
        </h4>
        <p className="text-xs text-slate-300 leading-relaxed">
          Neurolens is designed as a tool to support parents and developmental practitioners in logging, organizing, and tracking natural behavioral observations against structured milestone guidelines.
        </p>
        <p className="text-[10px] text-slate-400 leading-relaxed font-semibold mt-1.5">
          This system <span className="text-amber-500 font-bold">does NOT diagnose autism, assign risk scores, or make medical recommendations.</span> Clinical assessments and final developmental diagnoses must always be conducted by qualified healthcare professionals.
        </p>
      </div>
    </div>
  );
};
