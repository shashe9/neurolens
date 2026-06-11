"use client";

export default function Observations() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Form Column */}
      <div className="lg:col-span-1">
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl space-y-6 sticky top-24">
          <div>
            <h2 className="text-xl font-bold text-slate-100">Log Observation</h2>
            <p className="text-xs text-slate-400 mt-1">This log directly feeds the evidentiary sections of the final clinician report.</p>
          </div>

          <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
            {/* Observer */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Observer Name</label>
              <input type="text" defaultValue="Mom (Sarah)" className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-sm text-slate-100 outline-none transition-colors" />
            </div>

            {/* Entry Type */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Entry Type</label>
              <select className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors">
                <option value="general_observation">📋 General Observation</option>
                <option value="concern">⚠️ Concern</option>
                <option value="milestone_observation">📊 Milestone Observation</option>
              </select>
            </div>

            {/* Developmental Domain */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Developmental Domain</label>
              <select className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors">
                <option value="1">Communication</option>
                <option value="2">Gross Motor</option>
                <option value="3">Fine Motor</option>
                <option value="4">Social Emotional</option>
                <option value="5">Cognitive</option>
                <option value="6">Behavioral Patterns</option>
              </select>
            </div>

            {/* Body */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Observation Details</label>
              <textarea placeholder="Describe the behavior, actions, or words in details..." rows={4} className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-sm text-slate-100 outline-none transition-colors resize-none"></textarea>
            </div>

            {/* Context Note */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Context / Environment (Optional)</label>
              <input type="text" placeholder="e.g. at the park, during lunchtime..." className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-sm text-slate-100 outline-none transition-colors" />
            </div>

            {/* Regression Toggle */}
            <div className="flex items-center gap-2 pt-2">
              <input type="checkbox" id="regression" className="h-4 w-4 bg-slate-950 border-slate-800 rounded focus:ring-indigo-500 accent-indigo-500" />
              <label htmlFor="regression" className="text-xs font-semibold text-slate-300">Is this a regression of a previously achieved skill?</label>
            </div>

            {/* Submit */}
            <button type="submit" className="w-full py-3 bg-gradient-to-r from-indigo-500 to-violet-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-500/25 hover:brightness-110 active:scale-95 transition-all mt-4">
              Add to Report Evidence
            </button>
          </form>
        </div>
      </div>

      {/* Logs Feed Column */}
      <div className="lg:col-span-2 space-y-6">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Evidence Logs</h2>
          <p className="text-xs text-slate-400 mt-1">Review qualitative data that will be exported in the clinician report snapshot.</p>
        </div>

        <div className="space-y-4">
          {/* Card 1 - Concern */}
          <div className="p-5 bg-slate-900/40 border border-red-500/20 rounded-2xl space-y-3 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold tracking-wider text-red-400 uppercase bg-red-500/10 px-2.5 py-0.5 rounded-full border border-red-500/20">
                Concern
              </span>
              <span className="text-xs text-slate-500">June 11, 2026 at 4:12 PM</span>
            </div>
            <p className="text-sm text-slate-200">
              "Not responding to name call, even when sitting nearby and with minimal background noise. Appeared fully locked onto stacking blocks."
            </p>
            <div className="flex flex-wrap gap-2 text-[10px] text-slate-400">
              <span className="bg-slate-850 px-2 py-1 rounded">Domain: Communication</span>
              <span className="bg-slate-850 px-2 py-1 rounded">Context: Stacking blocks in living room</span>
              <span className="bg-red-950/20 text-red-400 px-2 py-1 rounded border border-red-500/15">Regression: No</span>
            </div>
          </div>

          {/* Card 2 - Milestone Observation */}
          <div className="p-5 bg-slate-900/40 border border-emerald-500/20 rounded-2xl space-y-3 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold tracking-wider text-emerald-400 uppercase bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                Milestone Observation
              </span>
              <span className="text-xs text-slate-500">June 10, 2026 at 2:30 PM</span>
            </div>
            <p className="text-sm text-slate-200">
              "Leo pointed directly to the teddy bear on the top shelf to show me what he wanted, making eye contact immediately after pointing."
            </p>
            <div className="flex flex-wrap gap-2 text-[10px] text-slate-400">
              <span className="bg-slate-850 px-2 py-1 rounded">Domain: Social Emotional</span>
              <span className="bg-slate-850 px-2 py-1 rounded">Linked Milestone: Points to show someone what he wants</span>
              <span className="bg-slate-850 px-2 py-1 rounded">Context: Playroom before nap</span>
            </div>
          </div>

          {/* Card 3 - General Observation */}
          <div className="p-5 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-3 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-slate-500"></div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold tracking-wider text-slate-300 uppercase bg-slate-800 px-2.5 py-0.5 rounded-full border border-slate-700">
                General Observation
              </span>
              <span className="text-xs text-slate-500">June 08, 2026 at 11:15 AM</span>
            </div>
            <p className="text-sm text-slate-200">
              "Walked down the steps holding onto the railing, placing both feet on each step before moving to the next. Did not require hand holding."
            </p>
            <div className="flex flex-wrap gap-2 text-[10px] text-slate-400">
              <span className="bg-slate-850 px-2 py-1 rounded">Domain: Gross Motor</span>
              <span className="bg-slate-850 px-2 py-1 rounded">Context: Leaving upstairs apartment</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
