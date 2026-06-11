"use client";

export default function VisitPrep() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Configuration Column */}
      <div className="lg:col-span-2 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Prepare Clinical Visit Context</h1>
          <p className="text-xs text-slate-400 mt-1">Specify clinical details and primary concerns. This context acts as the preamble of the clinician report.</p>
        </div>

        <form className="bg-slate-900/40 border border-slate-800 p-6 sm:p-8 rounded-2xl space-y-6" onSubmit={(e) => e.preventDefault()}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Visit Date */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Visit Date</label>
              <input type="date" defaultValue="2026-06-25" className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors" />
            </div>

            {/* Clinician Name */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Clinician Name</label>
              <input type="text" defaultValue="Dr. Evelyn Marcus" className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors" />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Visit Priority */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Visit Priority</label>
              <select defaultValue="consultation" className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors">
                <option value="routine">Routine Checkup</option>
                <option value="consultation">Consultation / Assessment</option>
                <option value="urgent">Urgent Review</option>
              </select>
            </div>

            {/* Concern Level */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Concern Level</label>
              <select defaultValue="medium" className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors">
                <option value="low">🟢 Low Concern</option>
                <option value="medium">🟡 Medium Concern</option>
                <option value="high">🔴 High Concern</option>
              </select>
            </div>
          </div>

          {/* Primary Concern Note */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Primary Concern Note</label>
            <textarea defaultValue="Primary focus of this visit is to discuss communication progress. Leo has achieved solid motor milestones, but we are noticing inconsistency in his response to verbal requests and name calls. We would love advice on social attention exercises." rows={6} className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-sm text-slate-100 outline-none transition-colors resize-none"></textarea>
          </div>

          {/* Submit Action */}
          <button type="submit" className="w-full py-3 bg-gradient-to-r from-indigo-500 to-violet-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-500/20 hover:brightness-110 active:scale-95 transition-all">
            Save Visit Context
          </button>
        </form>
      </div>

      {/* Overview Column */}
      <div className="lg:col-span-1 space-y-6">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Report Compilation Summary</h2>
          <p className="text-xs text-slate-400 mt-1">Review the status of developmental evidence segments compiled for the report.</p>
        </div>

        <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl space-y-4">
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Target Child</h3>
            <p className="text-sm font-semibold text-slate-200">Leo Carter (24 Months)</p>
          </div>

          <div className="h-px bg-slate-800"></div>

          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Available Evidence</h3>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-center justify-between">
                <span>General Observations:</span>
                <span className="font-bold text-slate-200">5 logged</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Specific Concerns:</span>
                <span className="font-bold text-red-400">3 logged</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Milestones Assessed:</span>
                <span className="font-bold text-indigo-400">4 logged</span>
              </li>
            </ul>
          </div>

          <div className="h-px bg-slate-800"></div>

          <div className="pt-2">
            <p className="text-[11px] text-slate-400 italic leading-relaxed">
              Once you save this visit context, you can navigate to the report generation page to output the official snapshot document.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
