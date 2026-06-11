import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center py-10 lg:py-16">
      {/* Hero Header */}
      <div className="text-center max-w-3xl space-y-6">
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-slate-100 via-indigo-200 to-slate-100 bg-clip-text text-transparent">
          Prepare Context for Your Clinician Visits
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Neurolens empowers parents to log day-to-day observations, verify milestones with evolution-backed evidence, and assemble comprehensive clinician-ready developmental summaries.
        </p>
      </div>

      {/* Visual Workflow Grid */}
      <div className="mt-16 w-full max-w-5xl">
        <h2 className="text-xs font-semibold tracking-wider text-slate-500 uppercase text-center mb-8">
          The Neurolens Workflow Flow
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-slate-900/40 border border-slate-800/60 rounded-xl p-5 text-center flex flex-col items-center justify-between">
            <span className="text-2xl">👦</span>
            <p className="text-sm font-semibold text-slate-200 mt-2">Child Profile</p>
            <p className="text-xs text-slate-500 mt-1">Demographics & ranges</p>
          </div>
          <div className="bg-slate-900/40 border border-slate-800/60 rounded-xl p-5 text-center flex flex-col items-center justify-between">
            <span className="text-2xl">📝</span>
            <p className="text-sm font-semibold text-slate-200 mt-2">Observations</p>
            <p className="text-xs text-slate-500 mt-1">General, milestones, concerns</p>
          </div>
          <div className="bg-slate-900/40 border border-slate-800/60 rounded-xl p-5 text-center flex flex-col items-center justify-between">
            <span className="text-2xl">📊</span>
            <p className="text-sm font-semibold text-slate-200 mt-2">Milestones</p>
            <p className="text-xs text-slate-500 mt-1">Domain progression checks</p>
          </div>
          <div className="bg-slate-900/40 border border-slate-800/60 rounded-xl p-5 text-center flex flex-col items-center justify-between">
            <span className="text-2xl">📅</span>
            <p className="text-sm font-semibold text-slate-200 mt-2">Visit Prep</p>
            <p className="text-xs text-slate-500 mt-1">Priorities & main concerns</p>
          </div>
          <div className="bg-slate-900/40 border border-slate-800/60 rounded-xl p-5 text-center flex flex-col items-center justify-between bg-gradient-to-tr from-indigo-950/40 to-violet-950/40 border-indigo-500/20">
            <span className="text-2xl">📄</span>
            <p className="text-sm font-semibold text-indigo-300 mt-2">Clinician Report</p>
            <p className="text-xs text-indigo-400/70 mt-1">Assembled JSON snapshot</p>
          </div>
        </div>
      </div>

      {/* Profile Selector */}
      <div className="mt-16 w-full max-w-md bg-slate-900/70 border border-slate-800 rounded-2xl p-8 shadow-2xl backdrop-blur-sm">
        <h3 className="text-lg font-bold text-slate-200 mb-6 text-center">Select Child Profile</h3>
        <div className="space-y-4">
          <Link href="/dashboard" className="flex items-center justify-between p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 rounded-xl group transition-all duration-200">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center font-bold text-xs text-white">
                LC
              </div>
              <div className="text-left">
                <p className="font-semibold text-slate-200 group-hover:text-indigo-400 transition-colors">Leo Carter</p>
                <p className="text-xs text-slate-400">24 Months &bull; Male</p>
              </div>
            </div>
            <span className="text-slate-400 group-hover:translate-x-1 transition-transform">&rarr;</span>
          </Link>
          
          <button disabled className="w-full py-3 px-4 border border-dashed border-slate-700 hover:border-slate-600 rounded-xl text-slate-500 text-xs font-semibold flex items-center justify-center gap-2 cursor-not-allowed">
            <span>+</span> Add Another Child Profile (Locked in V1 Sandbox)
          </button>
        </div>
      </div>
    </div>
  );
}
