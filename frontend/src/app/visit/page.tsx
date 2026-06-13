"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useActiveChild } from "@/components/ActiveChildContext";

interface Visit {
  id: string;
  child_id: string;
  visit_date: string;
  clinician_name: string;
  visit_priority: "routine" | "consultation" | "urgent";
  concern_level: "low" | "medium" | "high";
  concern_note: string;
  created_at: string;
}

interface Stats {
  total_count: number;
  by_domain: { [key: string]: number };
  by_type: { [key: string]: number };
  active_concern_count: number;
}

export default function VisitPrep() {
  const { activeChild, loading: contextLoading, fetchWithAuth } = useActiveChild();

  const [stats, setStats] = useState<Stats | null>(null);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Form fields
  const [visitDate, setVisitDate] = useState(() => {
    // Default to two weeks from now
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().split("T")[0];
  });
  const [clinicianName, setClinicianName] = useState("");
  const [visitPriority, setVisitPriority] = useState<"routine" | "consultation" | "urgent">("consultation");
  const [concernLevel, setConcernLevel] = useState<"low" | "medium" | "high">("medium");
  const [concernNote, setConcernNote] = useState("");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const loadPageData = useCallback(async () => {
    if (!activeChild) return;
    setLoadingData(true);
    try {
      // Fetch stats
      const statsRes = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/observations/stats`);
      const statsData = statsRes.ok ? await statsRes.json() : null;
      setStats(statsData);

      // Fetch visits
      const visitsRes = await fetchWithAuth(`${apiUrl}/visits/children/${activeChild.id}`);
      const visitsData = visitsRes.ok ? await visitsRes.json() : [];
      setVisits(visitsData);
    } catch (err) {
      console.error("Error loading visit data:", err);
    } finally {
      setLoadingData(false);
    }
  }, [activeChild, apiUrl, fetchWithAuth]);

  useEffect(() => {
    loadPageData();
  }, [loadPageData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeChild) return;

    if (!clinicianName.trim() || !concernNote.trim()) {
      alert("Please fill out clinician name and concern notes.");
      return;
    }

    try {
      const payload = {
        child_id: activeChild.id,
        visit_date: visitDate,
        clinician_name: clinicianName.trim(),
        visit_priority: visitPriority,
        concern_level: concernLevel,
        concern_note: concernNote.trim(),
      };

      const res = await fetchWithAuth(`${apiUrl}/visits`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to save visit context.");
      }

      setSubmitSuccess(true);
      setClinicianName("");
      setConcernNote("");
      
      // Auto dismiss success alert
      setTimeout(() => setSubmitSuccess(false), 5000);

      // Refresh list
      loadPageData();
    } catch (err: any) {
      alert(err.message || "Failed to save visit context.");
    }
  };

  if (contextLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (!activeChild) {
    return (
      <div className="bg-slate-900/40 border border-slate-800 p-8 rounded-2xl text-center max-w-lg mx-auto mt-12 space-y-4">
        <h2 className="text-xl font-bold text-slate-200">No Child Profile Selected</h2>
        <p className="text-sm text-slate-400">Please make sure the seed script has been run and you are connected to the backend API.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Configuration Column */}
      <div className="lg:col-span-2 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
            Prepare Clinical Visit Context
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Specify clinical details and primary concerns. This context acts as the preamble of the clinician report.
          </p>
        </div>

        {submitSuccess && (
          <div className="p-4 bg-emerald-500/10 border border-emerald-500/35 text-emerald-400 text-xs rounded-xl flex items-center gap-2 animate-fadeIn">
            <span>✅</span> Visit preparation context saved successfully! You can now use it when generating reports.
          </div>
        )}

        <form className="bg-slate-900/40 border border-slate-800 p-6 sm:p-8 rounded-2xl space-y-6 backdrop-blur-sm" onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Visit Date */}
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Visit Date</label>
              <input
                type="date"
                value={visitDate}
                onChange={(e) => setVisitDate(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors"
              />
            </div>

            {/* Clinician Name */}
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Clinician Name</label>
              <input
                type="text"
                placeholder="e.g. Dr. Evelyn Marcus"
                value={clinicianName}
                onChange={(e) => setClinicianName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Visit Priority */}
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Visit Priority</label>
              <select
                value={visitPriority}
                onChange={(e) => setVisitPriority(e.target.value as any)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors"
              >
                <option value="routine">Routine Checkup</option>
                <option value="consultation">Consultation / Assessment</option>
                <option value="urgent">Urgent Review</option>
              </select>
            </div>

            {/* Concern Level */}
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Concern Level</label>
              <select
                value={concernLevel}
                onChange={(e) => setConcernLevel(e.target.value as any)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors"
              >
                <option value="low">🟢 Low Concern</option>
                <option value="medium">🟡 Medium Concern</option>
                <option value="high">🔴 High Concern</option>
              </select>
            </div>
          </div>

          {/* Primary Concern Note */}
          <div>
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Primary Concern Note</label>
            <textarea
              placeholder={`State the primary clinical focus of this visit. e.g. "We want to focus on communication progress and response to name calls. Motor skills seem fully appropriate."`}
              rows={6}
              value={concernNote}
              onChange={(e) => setConcernNote(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-sm text-slate-100 outline-none transition-colors resize-none"
            ></textarea>
          </div>

          {/* Submit Action */}
          <button
            type="submit"
            className="w-full py-3 bg-gradient-to-r from-indigo-500 to-violet-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-500/20 hover:brightness-110 active:scale-[0.98] transition-all"
          >
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

        <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl space-y-4 backdrop-blur-sm">
          <div className="space-y-2">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Target Child</h3>
            <p className="text-sm font-semibold text-slate-200">
              {activeChild.first_name} {activeChild.last_name}
            </p>
          </div>

          <div className="h-px bg-slate-800"></div>

          <div className="space-y-2">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Available Evidence</h3>
            {loadingData ? (
              <div className="space-y-2 py-2">
                <div className="h-3 bg-slate-800 rounded animate-pulse w-full"></div>
                <div className="h-3 bg-slate-800 rounded animate-pulse w-2/3"></div>
              </div>
            ) : (
              <ul className="space-y-2 text-xs text-slate-300">
                <li className="flex items-center justify-between">
                  <span>General Observations:</span>
                  <span className="font-bold text-slate-200">{stats?.by_type?.general || 0} logged</span>
                </li>
                <li className="flex items-center justify-between">
                  <span>Specific Concerns:</span>
                  <span className={`font-bold ${stats?.active_concern_count ? 'text-red-400' : 'text-slate-400'}`}>
                    {stats?.active_concern_count || 0} logged
                  </span>
                </li>
                <li className="flex items-center justify-between">
                  <span>Milestones Assessed:</span>
                  <span className="font-bold text-indigo-400">{stats?.by_type?.milestone || 0} logged</span>
                </li>
                <li className="pt-2 border-t border-slate-800/40 flex items-center justify-between font-semibold">
                  <span>Total Active Logs:</span>
                  <span className="text-slate-100">{stats?.total_count || 0}</span>
                </li>
              </ul>
            )}
          </div>

          <div className="h-px bg-slate-800"></div>

          <div className="pt-2">
            <p className="text-[11px] text-slate-400 italic leading-relaxed">
              Once you save this visit context, you can navigate to the report generation page to output the official snapshot document.
            </p>
          </div>
        </div>

        {/* Existing Visit Configs */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-200">Scheduled Visit Contexts</h3>
          {loadingData ? (
            <div className="h-20 bg-slate-900/40 border border-slate-850 rounded-2xl animate-pulse"></div>
          ) : visits.length === 0 ? (
            <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl text-center text-xs text-slate-500">
              No clinical visits configured yet.
            </div>
          ) : (
            <div className="space-y-3">
              {visits.map((v) => {
                let priorityColor = "bg-slate-800 text-slate-300 border-slate-700";
                if (v.visit_priority === "urgent") {
                  priorityColor = "bg-red-500/10 text-red-400 border-red-500/20";
                } else if (v.visit_priority === "consultation") {
                  priorityColor = "bg-indigo-500/10 text-indigo-400 border-indigo-500/25";
                }
                
                let levelColor = "text-slate-400";
                if (v.concern_level === "high") levelColor = "text-red-400";
                else if (v.concern_level === "medium") levelColor = "text-yellow-400";
                else if (v.concern_level === "low") levelColor = "text-emerald-400";

                return (
                  <div key={v.id} className="p-4 bg-slate-900/30 border border-slate-850 rounded-xl space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{v.clinician_name}</span>
                      <span className="text-[10px] text-slate-500">{new Date(v.visit_date).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-[9px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${priorityColor}`}>
                        {v.visit_priority}
                      </span>
                      <span className={`text-[10px] ${levelColor} font-semibold capitalize`}>
                        {v.concern_level} Concern
                      </span>
                    </div>
                    <p className="text-slate-400 italic line-clamp-2 mt-1">"{v.concern_note}"</p>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
