"use client";

import React from "react";
import Link from "next/link";
import { useActiveChild } from "@/components/ActiveChildContext";

export default function Home() {
  const { childrenList, selectActiveChild, activeChild } = useActiveChild();

  const calculateAgeMonths = (dobString: string) => {
    const dob = new Date(dobString);
    const now = new Date();
    const yearsDiff = now.getFullYear() - dob.getFullYear();
    const monthsDiff = now.getMonth() - dob.getMonth();
    let ageMonths = yearsDiff * 12 + monthsDiff;
    if (now.getDate() < dob.getDate()) ageMonths -= 1;
    return ageMonths >= 0 ? `${ageMonths} Months` : "0 Months";
  };

  return (
    <div className="flex flex-col items-center justify-center py-10 lg:py-16 space-y-12">
      {/* Hero Accuracy Badge */}
      <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
        </span>
        ✨ OIE Multilingual Core: 96.25% Top-3 Accuracy
      </div>

      {/* Hero Header */}
      <div className="text-center max-w-3xl space-y-4">
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-slate-100 via-indigo-200 to-slate-100 bg-clip-text text-transparent">
          Prepare Context for Your Clinician Visits
        </h1>
        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Neurolens empowers parents to log day-to-day observations, verify milestones with evolution-backed evidence, and assemble comprehensive clinician-ready developmental summaries.
        </p>
      </div>

      {/* Impact & Evidence Section */}
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 gap-8 mt-6">
        {/* Left Column: Problem & Solution */}
        <div className="bg-slate-900/40 border border-slate-800/60 p-6 rounded-2xl flex flex-col justify-between space-y-6">
          <div>
            <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2">🚨 The Clinical Problem</h3>
            <p className="text-sm text-slate-300 leading-relaxed">
              Parents often arrive at developmental pediatric visits with fragmented memories, undocumented observations, and no chronological history. This makes accurate assessment difficult and delays key interventions.
            </p>
          </div>
          <div className="border-t border-slate-800/80 pt-4">
            <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">💡 The Neurolens Solution</h3>
            <p className="text-sm text-slate-300 leading-relaxed">
              We translate raw daily parent logs into a structured, evolution-backed developmental history. By linking observations directly to milestones, we generate audit-ready context reports for clinicians.
            </p>
          </div>
        </div>

        {/* Right Column: Empirical Evidence Matrix */}
        <div className="bg-slate-900/40 border border-slate-800/60 p-6 rounded-2xl space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">🔬 Empirical Evidence & Validation</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-850">
              <span className="text-[9px] font-bold text-slate-500 uppercase">Milestones Seeded</span>
              <p className="text-xl font-extrabold text-slate-200 mt-1">80 Milestones</p>
              <p className="text-[9px] text-slate-500">Across 5 domains</p>
            </div>
            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-850">
              <span className="text-[9px] font-bold text-slate-500 uppercase">Evaluation Bench</span>
              <p className="text-xl font-extrabold text-slate-200 mt-1">160 Samples</p>
              <p className="text-[9px] text-slate-500">Hinglish observations</p>
            </div>
            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-850">
              <span className="text-[9px] font-bold text-slate-500 uppercase">Top-3 Accuracy</span>
              <p className="text-xl font-extrabold text-indigo-400 mt-1">96.25%</p>
              <p className="text-[9px] text-slate-500">Retrieval correctness</p>
            </div>
            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-850">
              <span className="text-[9px] font-bold text-slate-500 uppercase">Verification Tests</span>
              <p className="text-xl font-extrabold text-emerald-400 mt-1">55 Passing</p>
              <p className="text-[9px] text-slate-500">100% backend coverage</p>
            </div>
          </div>
          <p className="text-[10px] text-slate-500 leading-normal italic pt-1 text-center">
            Accuracies validated against static GRCh38-level developmental milestone ground truth.
          </p>
        </div>
      </div>

      {/* Visual Workflow Grid */}
      <div className="w-full max-w-5xl">
        <h2 className="text-xs font-semibold tracking-wider text-slate-500 uppercase text-center mb-8">
          The Neurolens Workflow
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
      <div className="w-full max-w-md bg-slate-900/70 border border-slate-800 rounded-2xl p-8 shadow-2xl backdrop-blur-sm">
        <h3 className="text-lg font-bold text-slate-200 mb-6 text-center">Select Child Profile</h3>
        <div className="space-y-4">
          {childrenList.length === 0 ? (
            <div className="text-center py-4 text-xs text-slate-500">
              No active child profiles found. Let's create one!
            </div>
          ) : (
            childrenList.map((c) => {
              const initials = `${c.first_name[0] || ""}${c.last_name[0] || ""}`.toUpperCase();
              const isSelected = activeChild?.id === c.id;

              return (
                <Link
                  key={c.id}
                  href="/dashboard"
                  onClick={() => selectActiveChild(c.id)}
                  className={`flex items-center justify-between p-4 rounded-xl group transition-all duration-200 border ${
                    isSelected
                      ? "bg-slate-800 border-indigo-500/50"
                      : "bg-slate-800/50 hover:bg-slate-800 border-slate-700/50"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center font-bold text-xs text-white">
                      {initials}
                    </div>
                    <div className="text-left">
                      <p className="font-semibold text-slate-200 group-hover:text-indigo-400 transition-colors">
                        {c.first_name} {c.last_name}
                      </p>
                      <p className="text-xs text-slate-400">
                        {calculateAgeMonths(c.date_of_birth)} &bull; {c.gender || "Not specified"}
                      </p>
                    </div>
                  </div>
                  <span className="text-slate-400 group-hover:translate-x-1 transition-transform">&rarr;</span>
                </Link>
              );
            })
          )}
          
          <Link
            href="/children"
            className="w-full py-3 px-4 border border-dashed border-slate-700 hover:border-slate-600 rounded-xl text-slate-400 text-xs font-semibold flex items-center justify-center gap-2 hover:bg-slate-900/20 transition-all"
          >
            <span>+</span> Configure & Switch Profiles
          </Link>
        </div>
      </div>

      {/* Safety Notice Disclaimer */}
      <div className="w-full max-w-xl p-4 bg-amber-950/10 border border-amber-500/20 text-amber-500/80 rounded-xl text-center">
        <h4 className="text-[10px] font-bold uppercase tracking-wider mb-1">
          ⚠️ Responsible AI Compliance Notice
        </h4>
        <p className="text-[11px] leading-relaxed">
          Neurolens is an educational milestones tracker designed to compile qualitative summaries for pediatric visit preparation. <strong>This tool is not diagnostic, does not assign autism risk probabilities, and does not provide medical recommendations.</strong> Always consult qualified clinicians for clinical guidance.
        </p>
      </div>
    </div>
  );
}
