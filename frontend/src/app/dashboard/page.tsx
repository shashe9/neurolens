"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useActiveChild } from "@/components/ActiveChildContext";

interface Stats {
  total_count: number;
  by_domain: { [key: string]: number };
  by_type: { [key: string]: number };
  active_concern_count: number;
}

interface Observation {
  id: string;
  body: string;
  entry_type: "general" | "concern" | "milestone";
  domain_id: number | null;
  observed_at: string;
  location: string | null;
  observer_relation: string | null;
}

interface Visit {
  id: string;
  visit_date: string;
  clinician_name: string;
}

const DOMAINS = [
  { id: 1, name: "Communication" },
  { id: 2, name: "Gross Motor" },
  { id: 3, name: "Fine Motor" },
  { id: 4, name: "Social Emotional" },
  { id: 5, name: "Cognitive" },
  { id: 6, name: "Behavioral Patterns" },
];

export default function Dashboard() {
  const { activeChild, loading: contextLoading } = useActiveChild();

  const [stats, setStats] = useState<Stats | null>(null);
  const [recentObs, setRecentObs] = useState<Observation[]>([]);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [loadingData, setLoadingData] = useState(true);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchDashboardData = useCallback(async () => {
    if (!activeChild) return;
    setLoadingData(true);
    try {
      // 1. Fetch Stats
      const statsRes = await fetch(`${apiUrl}/children/${activeChild.id}/observations/stats`);
      const statsData = statsRes.ok ? await statsRes.json() : null;
      setStats(statsData);

      // 2. Fetch Recent Observations (Limit 3)
      const obsRes = await fetch(`${apiUrl}/children/${activeChild.id}/observations`);
      if (obsRes.ok) {
        const obsData: Observation[] = await obsRes.json();
        setRecentObs(obsData.slice(0, 3));
      }

      // 3. Fetch Visits to check preparation status
      const visitsRes = await fetch(`${apiUrl}/visits/children/${activeChild.id}`);
      if (visitsRes.ok) {
        const visitsData: Visit[] = await visitsRes.json();
        setVisits(visitsData);
      }
    } catch (err) {
      console.error("Error fetching dashboard details:", err);
    } finally {
      setLoadingData(false);
    }
  }, [activeChild, apiUrl]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

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

  // Calculate age display
  const dob = new Date(activeChild.date_of_birth);
  const now = new Date();
  const yearsDiff = now.getFullYear() - dob.getFullYear();
  const monthsDiff = now.getMonth() - dob.getMonth();
  let ageMonths = yearsDiff * 12 + monthsDiff;
  if (now.getDate() < dob.getDate()) ageMonths -= 1;
  const ageDisplay = ageMonths >= 0 ? `${ageMonths} Months` : "Newborn";

  // Visit Status
  const hasVisits = visits.length > 0;
  const latestVisit = hasVisits ? visits[0] : null;

  return (
    <div className="space-y-10">
      {/* Profile Overview Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 backdrop-blur-sm">
        <div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/25">Active Record</span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 mt-2 bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
            {activeChild.first_name} {activeChild.last_name}
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            {ageDisplay} (DOB: {new Date(activeChild.date_of_birth).toLocaleDateString()}) &bull; {activeChild.gender}
          </p>
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

      {/* Aggregate Quality Progress Indicator */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Child Core Data Status */}
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between h-40 backdrop-blur-sm">
          <div>
            <h3 className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">Child Profile Details</h3>
            <p className="text-2xl font-bold text-slate-100 mt-2">Complete</p>
          </div>
          <p className="text-xs text-emerald-400 flex items-center gap-1">
            <span>&bull;</span> Essential demographics and age ranges verified
          </p>
        </div>

        {/* Observation Status */}
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between h-40 backdrop-blur-sm">
          <div>
            <h3 className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">Observations Logged</h3>
            <p className="text-2xl font-bold text-slate-100 mt-2">
              {loadingData ? "..." : `${stats?.total_count || 0} Items`}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-indigo-400 flex items-center gap-1">
              <span>&bull;</span> {stats?.by_type?.concern || 0} Concerns, {stats?.by_type?.milestone || 0} Milestones
            </p>
            {!loadingData && recentObs.length > 0 && (
              <p className="text-[10px] text-slate-500 font-mono">
                Last logged: {new Date(recentObs[0].observed_at).toLocaleDateString()}
              </p>
            )}
          </div>
        </div>

        {/* Clinical Visit Preparation */}
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between h-40 backdrop-blur-sm">
          <div>
            <h3 className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">Visit Prep Status</h3>
            <p className="text-2xl font-bold text-slate-100 mt-2">
              {loadingData ? "..." : hasVisits ? "Configured" : "Needs Setup"}
            </p>
          </div>
          {hasVisits ? (
            <p className="text-xs text-emerald-400 flex items-center gap-1">
              <span>&bull;</span> Next: {latestVisit?.clinician_name} on {latestVisit?.visit_date}
            </p>
          ) : (
            <Link href="/visit" className="text-xs text-violet-400 hover:underline flex items-center gap-1">
              Configure visit priorities & concern level &rarr;
            </Link>
          )}
        </div>
      </div>

      {/* Main Page Layout Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Columns - Platform Flow Quick Actions */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-lg font-bold text-slate-200">Clinician Report Context Assembly</h2>
          
          <div className="space-y-4">
            {/* Step 1 CTA */}
            <div className="p-5 bg-slate-900/40 border border-slate-800 hover:border-slate-700/80 rounded-2xl flex items-start gap-4 transition-all hover:bg-slate-900/50">
              <span className="text-2xl bg-indigo-500/10 text-indigo-400 p-3 rounded-xl select-none">📝</span>
              <div>
                <h3 className="font-semibold text-slate-200">1. Log Day-to-Day Observations</h3>
                <p className="text-xs text-slate-400 mt-1">Capture natural behavioral observations, tagging regressions or specific developmental domains. Feed qualitative evidence directly into the report.</p>
                <Link href="/observations" className="text-xs text-indigo-400 font-semibold hover:underline mt-2 inline-block">Go to Observations &rarr;</Link>
              </div>
            </div>

            {/* Step 2 CTA */}
            <div className="p-5 bg-slate-900/40 border border-slate-800 hover:border-slate-700/80 rounded-2xl flex items-start gap-4 transition-all hover:bg-slate-900/50">
              <span className="text-2xl bg-violet-500/10 text-violet-400 p-3 rounded-xl select-none">📊</span>
              <div>
                <h3 className="font-semibold text-slate-200">2. Review & Track Milestones</h3>
                <p className="text-xs text-slate-400 mt-1">Compare behaviors against evidence-based age ranges (e.g. 18-24m). Mark items as Achieved or In Progress to populate the developmental matrix.</p>
                <Link href="/milestones" className="text-xs text-violet-400 font-semibold hover:underline mt-2 inline-block">Review Milestones &rarr;</Link>
              </div>
            </div>

            {/* Step 3 CTA */}
            <div className="p-5 bg-slate-900/40 border border-slate-800 hover:border-slate-700/80 rounded-2xl flex items-start gap-4 transition-all hover:bg-slate-900/50">
              <span className="text-2xl bg-slate-800 text-slate-300 p-3 rounded-xl select-none">📅</span>
              <div>
                <h3 className="font-semibold text-slate-200">3. Set Clinical Visit Priorities</h3>
                <p className="text-xs text-slate-400 mt-1">Specify date, clinician name, priority, concern level, and primary notes to clarify the goals of the forthcoming consultation.</p>
                <Link href="/visit" className="text-xs text-slate-400 font-semibold hover:underline mt-2 inline-block">Configure Visit Context &rarr;</Link>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Recent Observations Preview */}
        <div className="space-y-6">
          <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-4 backdrop-blur-sm">
            <h2 className="text-xs font-bold text-slate-200 tracking-wide uppercase border-b border-slate-800 pb-2">
              Report Evidence Feed
            </h2>
            {loadingData ? (
              <div className="space-y-4">
                <div className="h-10 bg-slate-800 rounded animate-pulse"></div>
                <div className="h-10 bg-slate-800 rounded animate-pulse"></div>
              </div>
            ) : recentObs.length === 0 ? (
              <p className="text-xs text-slate-500 py-4 text-center">No active observations. Start by logging one!</p>
            ) : (
              <div className="divide-y divide-slate-800/80 space-y-4">
                {recentObs.map((obs, idx) => {
                  let badgeColor = "text-slate-400 bg-slate-800";
                  if (obs.entry_type === "concern") {
                    badgeColor = "text-red-400 bg-red-500/10";
                  } else if (obs.entry_type === "milestone") {
                    badgeColor = "text-emerald-400 bg-emerald-500/10";
                  }

                  const domainName = DOMAINS.find((d) => d.id === obs.domain_id)?.name || "General";

                  return (
                    <div key={obs.id} className={idx > 0 ? "pt-4" : ""}>
                      <span className={`text-[9px] uppercase font-bold px-2 py-0.5 rounded border border-slate-800/50 ${badgeColor}`}>
                        {obs.entry_type}
                      </span>
                      <p className="text-xs text-slate-200 mt-2 font-mono line-clamp-3 italic">
                        "{obs.body}"
                      </p>
                      <p className="text-[10px] text-slate-500 mt-1">
                        By {obs.observer_relation || "Parent"} &bull; {domainName}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
            
            {!loadingData && recentObs.length > 0 && (
              <div className="pt-2 border-t border-slate-800/60 text-center">
                <Link href="/observations" className="text-xs text-indigo-400 hover:text-indigo-350 hover:underline font-semibold">
                  View All Observations &rarr;
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
