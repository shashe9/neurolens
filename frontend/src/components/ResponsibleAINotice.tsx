import React from "react";
import { ShieldAlert } from "lucide-react";

export const ResponsibleAINotice: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex items-start gap-4 max-w-4xl mx-auto shadow-sm">
      <ShieldAlert className="h-6 w-6 text-amber-600 shrink-0 mt-0.5" />
      <div className="space-y-2 text-left">
        <h4 className="text-sm font-bold uppercase tracking-wider text-slate-100">
          A Gentle Note
        </h4>
        <p className="text-base text-slate-400 leading-relaxed">
          Neurolens is a developmental journal to help you notice patterns and prepare for pediatric visits. It is not diagnostic, does not evaluate autism risk, and does not provide clinical assessments. Always consult a qualified pediatrician.
        </p>
      </div>
    </div>
  );
};
