import Link from "next/link";

export default function Dashboard() {
  return (
    <div className="space-y-10">
      {/* Profile Overview Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
        <div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/25">Active Record</span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 mt-2">Leo Carter</h1>
          <p className="text-sm text-slate-400 mt-1">24 Months (DOB: June 15, 2024) &bull; Male</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link href="/observations" className="px-5 py-3 bg-gradient-to-r from-indigo-500 to-violet-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-500/20 hover:brightness-110 active:scale-95 transition-all">
            ✍️ Log Observation
          </Link>
          <Link href="/report" className="px-5 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm rounded-xl border border-slate-700 transition-all">
            📄 Assemble Report
          </Link>
        </div>
      </div>

      {/* Aggregate Report Quality Progress Indicator */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Child Core Data Status */}
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between h-40">
          <div>
            <h3 className="text-xs font-semibold tracking-wider text-slate-400 uppercase">Child Profile Details</h3>
            <p className="text-2xl font-bold text-slate-100 mt-2">Complete</p>
          </div>
          <p className="text-xs text-emerald-400 flex items-center gap-1">
            <span>&bull;</span> Essential demographics and age ranges verified
          </p>
        </div>

        {/* Observation Status */}
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between h-40">
          <div>
            <h3 className="text-xs font-semibold tracking-wider text-slate-400 uppercase">Observations Logged</h3>
            <p className="text-2xl font-bold text-slate-100 mt-2">12 Items</p>
          </div>
          <p className="text-xs text-indigo-400 flex items-center gap-1">
            <span>&bull;</span> 3 Concerns, 9 Milestones documented
          </p>
        </div>

        {/* Clinical Visit Preparation */}
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between h-40">
          <div>
            <h3 className="text-xs font-semibold tracking-wider text-slate-400 uppercase">Visit Prep Status</h3>
            <p className="text-2xl font-bold text-slate-100 mt-2">Needs Setup</p>
          </div>
          <Link href="/visit" className="text-xs text-violet-400 hover:underline flex items-center gap-1">
            Configure visit priorities & concern level &rarr;
          </Link>
        </div>
      </div>

      {/* Main Page Layout Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Columns - Platform Flow Quick Actions */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-lg font-bold text-slate-200">Clinician Report Context Assembly</h2>
          
          <div className="space-y-4">
            {/* Step 1 CTA */}
            <div className="p-5 bg-slate-900/40 border border-slate-800 hover:border-slate-700/80 rounded-2xl flex items-start gap-4 transition-colors">
              <span className="text-2xl bg-indigo-500/10 text-indigo-400 p-3 rounded-xl">📝</span>
              <div>
                <h3 className="font-semibold text-slate-200">1. Log Day-to-Day Observations</h3>
                <p className="text-xs text-slate-400 mt-1">Capture natural behavioral observations, tagging regressions or specific developmental domains. Feed qualitative evidence directly into the report.</p>
                <Link href="/observations" className="text-xs text-indigo-400 font-semibold hover:underline mt-2 inline-block">Go to Observations &rarr;</Link>
              </div>
            </div>

            {/* Step 2 CTA */}
            <div className="p-5 bg-slate-900/40 border border-slate-800 hover:border-slate-700/80 rounded-2xl flex items-start gap-4 transition-colors">
              <span className="text-2xl bg-violet-500/10 text-violet-400 p-3 rounded-xl">📊</span>
              <div>
                <h3 className="font-semibold text-slate-200">2. Review & Track Milestones</h3>
                <p className="text-xs text-slate-400 mt-1">Compare behaviors against evidence-based age ranges (e.g. 18-24m). Mark items as Achieved or In Progress to populate the developmental matrix.</p>
                <Link href="/milestones" className="text-xs text-violet-400 font-semibold hover:underline mt-2 inline-block">Review Milestones &rarr;</Link>
              </div>
            </div>

            {/* Step 3 CTA */}
            <div className="p-5 bg-slate-900/40 border border-slate-800 hover:border-slate-700/80 rounded-2xl flex items-start gap-4 transition-colors">
              <span className="text-2xl bg-slate-800 text-slate-300 p-3 rounded-xl">📅</span>
              <div>
                <h3 className="font-semibold text-slate-200">3. Set Clinical Visit Priorities</h3>
                <p className="text-xs text-slate-400 mt-1">Specify date, clinician name, priority, concern level, and primary notes to clarify the goals of the forthcoming consultation.</p>
                <Link href="/visit" className="text-xs text-slate-400 font-semibold hover:underline mt-2 inline-block">Configure Visit Context &rarr;</Link>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Recent Observations Preview & Aggregate Quality Review */}
        <div className="space-y-6">
          <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-sm font-bold text-slate-200 tracking-wide uppercase">Report Evidence Feed</h2>
            <div className="divide-y divide-slate-800/80 space-y-4">
              <div className="pt-2">
                <span className="text-[10px] uppercase font-bold text-red-400 px-1.5 py-0.5 rounded bg-red-400/10">Concern</span>
                <p className="text-xs text-slate-200 mt-1">"Not responding to name call, even when sitting nearby and with minimal background noise."</p>
                <p className="text-[10px] text-slate-500 mt-1">Logged by Mom &bull; Communication domain</p>
              </div>
              <div className="pt-4">
                <span className="text-[10px] uppercase font-bold text-emerald-400 px-1.5 py-0.5 rounded bg-emerald-400/10">Milestone</span>
                <p className="text-xs text-slate-200 mt-1">"Points to show someone what he wants (e.g. points to a toy on a shelf)."</p>
                <p className="text-[10px] text-slate-500 mt-1">Logged by Mom &bull; Fine Motor domain</p>
              </div>
              <div className="pt-4">
                <span className="text-[10px] uppercase font-bold text-slate-400 px-1.5 py-0.5 rounded bg-slate-800">General</span>
                <p className="text-xs text-slate-200 mt-1">"Played with stack blocks for 15 minutes. Very persistent in stacking them 4-high."</p>
                <p className="text-[10px] text-slate-500 mt-1">Logged by Dad &bull; Cognitive domain</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
