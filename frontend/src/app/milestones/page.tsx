"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useActiveChild } from "@/components/ActiveChildContext";

import { 
  MessageSquare, 
  Activity, 
  Edit3, 
  Heart, 
  Brain, 
  Layers, 
  Search, 
  BookOpen, 
  Check, 
  Plus 
} from "lucide-react";

interface Observation {
  id: string;
  body: string;
  structured_body: string | null;
  observed_at: string;
  location: string | null;
  observer_relation: string | null;
}

interface EvidenceSource {
  title: string;
  organization: string;
  year: number;
}

interface Milestone {
  id: string;
  domain_id: number;
  title: string;
  description: string;
  age_range_low: number;
  age_range_high: number;
  status: "not_observed" | "emerging" | "observed" | "consistently_demonstrated";
  evidence_count: number;
  evidence_ids: string[];
  evidence: Observation[];
  sources: EvidenceSource[];
}

interface FirstItem {
  id: string;
  is_first: boolean;
  first_title: string;
  first_date: string;
  linked_observation_id: string | null;
}

const DOMAINS_METADATA = [
  { id: 1, name: "Communication", key: "communication" },
  { id: 2, name: "Movement", key: "gross_motor" },
  { id: 3, name: "Hands & Fingers", key: "fine_motor" },
  { id: 4, name: "Feelings & Friendships", key: "social_emotional" },
  { id: 5, name: "Thinking & Learning", key: "cognitive" },
  { id: 6, name: "Daily Activities", key: "behavioral" },
];

export default function Milestones() {
  const { activeChild, loading: contextLoading, fetchWithAuth } = useActiveChild();
  
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [allObservations, setAllObservations] = useState<any[]>([]);
  const [firsts, setFirsts] = useState<FirstItem[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [loadingFirsts, setLoadingFirsts] = useState(false);
  
  const [selectedAgeRange, setSelectedAgeRange] = useState<string>("All");
  const [expandedMilestoneId, setExpandedMilestoneId] = useState<string | null>(null);
  const [linkTargetObs, setLinkTargetObs] = useState<{ [milestoneId: string]: string }>({});
  const [viewMode, setViewMode] = useState<"checklist" | "journey">("checklist");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchMilestoneData = useCallback(async () => {
    if (!activeChild) return;
    setLoading(true);
    try {
      const milestonesRes = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/milestones`);
      if (!milestonesRes.ok) throw new Error("Failed to load milestones.");
      const milestoneData = await milestonesRes.json();
      setMilestones(milestoneData);

      const obsRes = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/observations`);
      if (obsRes.ok) {
        const obsData = await obsRes.json();
        setAllObservations(obsData);
      }
    } catch (err) {
      console.error("Error loading milestone data:", err);
    } finally {
      setLoading(false);
    }
  }, [activeChild, apiUrl, fetchWithAuth]);

  const fetchFirstsData = useCallback(async () => {
    if (!activeChild) return;
    setLoadingFirsts(true);
    try {
      const res = await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/firsts`);
      if (res.ok) {
        const firstsData = await res.json();
        setFirsts(firstsData);
      }
    } catch (err) {
      console.error("Error loading firsts timeline:", err);
    } finally {
      setLoadingFirsts(false);
    }
  }, [activeChild, apiUrl, fetchWithAuth]);

  useEffect(() => {
    if (activeChild) {
      fetchMilestoneData();
      fetchFirstsData();
    }
  }, [activeChild, fetchMilestoneData, fetchFirstsData]);

  const handleStatusChange = async (milestoneId: string, newStatus: string) => {
    if (!activeChild) return;
    if (activeChild.deleted_at) {
      alert("Archived child profile is read-only. Status updates are blocked.");
      return;
    }

    try {
      const res = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/milestones/${milestoneId}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to update status.");
      }

      fetchMilestoneData();
      fetchFirstsData();
    } catch (err: any) {
      alert(err.message || "Failed to update milestone status.");
    }
  };

  const handleLinkEvidence = async (milestoneId: string) => {
    if (!activeChild) return;
    if (activeChild.deleted_at) {
      alert("Archived child profile is read-only. Status adjustments are blocked.");
      return;
    }

    const obsId = linkTargetObs[milestoneId];
    if (!obsId) {
      alert("Please select an observation to link.");
      return;
    }

    try {
      const res = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/milestones/${milestoneId}/evidence`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ observation_id: obsId }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to link observation.");
      }

      setLinkTargetObs(prev => ({ ...prev, [milestoneId]: "" }));
      fetchMilestoneData();
      fetchFirstsData();
    } catch (err: any) {
      alert(err.message || "Failed to link observation.");
    }
  };

  const handleUnlinkEvidence = async (milestoneId: string, obsId: string) => {
    if (!activeChild) return;
    if (activeChild.deleted_at) {
      alert("Archived child profile is read-only. Status adjustments are blocked.");
      return;
    }

    if (!confirm("Are you sure you want to unlink this observation?")) return;

    try {
      const res = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/milestones/${milestoneId}/evidence/${obsId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to unlink observation.");
      }

      fetchMilestoneData();
      fetchFirstsData();
    } catch (err: any) {
      alert(err.message || "Failed to unlink observation.");
    }
  };

  const renderDomainIcon = (id: number) => {
    switch (id) {
      case 1: return <MessageSquare className="h-5 w-5 text-indigo-500" />;
      case 2: return <Activity className="h-5 w-5 text-indigo-500" />;
      case 3: return <Edit3 className="h-5 w-5 text-indigo-500" />;
      case 4: return <Heart className="h-5 w-5 text-indigo-500" />;
      case 5: return <Brain className="h-5 w-5 text-indigo-500" />;
      default: return <Layers className="h-5 w-5 text-indigo-500" />;
    }
  };

  if (contextLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-650"></div>
      </div>
    );
  }

  if (!activeChild) {
    return (
      <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl text-center max-w-lg mx-auto mt-12 space-y-4 shadow-sm">
        <h2 className="text-2xl font-bold text-slate-50">No Child Profile Selected</h2>
        <p className="text-base text-slate-350">Please select a child profile to track milestones.</p>
      </div>
    );
  }

  const ageRanges = ["All", "18-24 Months", "24-36 Months"];

  const filteredMilestones = milestones.filter((m) => {
    if (selectedAgeRange === "All") return true;
    const is18to24 = m.age_range_low >= 18 && m.age_range_high <= 24;
    const is24to36 = m.age_range_low >= 24 && m.age_range_high <= 36;
    if (selectedAgeRange === "18-24 Months") return is18to24;
    if (selectedAgeRange === "24-36 Months") return is24to36;
    return true;
  });

  const achievedMilestones = milestones.filter(
    (m) => m.status === "observed" || m.status === "consistently_demonstrated"
  );

  const resolvedAchievedMilestones = achievedMilestones.map((m) => {
    let resolvedDate: Date | null = null;
    let isFromBaseline = false;
    
    if ((m as any).observed_date) {
      resolvedDate = new Date((m as any).observed_date);
    } else if (m.evidence && m.evidence.length > 0) {
      const dates = m.evidence.map((e) => new Date(e.observed_at).getTime());
      resolvedDate = new Date(Math.max(...dates));
    } else {
      isFromBaseline = true;
    }
    
    return {
      ...m,
      resolvedDate,
      isFromBaseline,
    };
  });

  resolvedAchievedMilestones.sort((a, b) => {
    if (a.isFromBaseline && b.isFromBaseline) return 0;
    if (a.isFromBaseline) return -1;
    if (b.isFromBaseline) return 1;
    if (!a.resolvedDate || !b.resolvedDate) return 0;
    return a.resolvedDate.getTime() - b.resolvedDate.getTime();
  });

  const observedCount = milestones.filter(m => m.status === "observed" || m.status === "consistently_demonstrated").length;
  const emergingCount = milestones.filter(m => m.status === "emerging").length;

  const recentProgress = [...resolvedAchievedMilestones].reverse().slice(0, 5);

  const whatMightComeNext = milestones
    .filter(m => m.status === "not_observed" || m.status === "emerging")
    .sort((a, b) => a.age_range_low - b.age_range_low)
    .slice(0, 4);

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-10 px-6 text-left">
      
      {/* Header */}
      <div className="text-left space-y-3">
        <h1 className="text-4xl font-extrabold text-slate-50 leading-tight">
          Development Journey
        </h1>
        <p className="text-lg text-slate-350">
          Observe and follow your child's growth naturally, note down emerging skills, and prepare simple summaries for pediatric visits.
        </p>
      </div>

      {/* Sub-navigation Tabs */}
      <div className="flex gap-2 bg-slate-900 p-1 border border-slate-800 rounded-xl max-w-xs">
        <button
          onClick={() => setViewMode("checklist")}
          className={`flex-1 px-4 py-2.5 text-sm font-bold rounded-lg transition-all cursor-pointer ${
            viewMode === "checklist"
              ? "bg-slate-800 text-slate-100 shadow-sm"
              : "text-slate-350 hover:text-slate-200"
          }`}
        >
          Checklist
        </button>
        <button
          onClick={() => setViewMode("journey")}
          className={`flex-1 px-4 py-2.5 text-sm font-bold rounded-lg transition-all cursor-pointer ${
            viewMode === "journey"
              ? "bg-slate-800 text-slate-100 shadow-sm"
              : "text-slate-350 hover:text-slate-200"
          }`}
        >
          Firsts
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-650"></div>
        </div>
      ) : viewMode === "journey" ? (
        
        /* FIRSTS TIMELINE VIEW */
        <div className="space-y-8">
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-sm space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-50">Firsts Timeline</h2>
              <p className="text-base text-slate-350 mt-1">
                A chronological history of {activeChild.first_name}'s developmental "first" moments, confirmed by you.
              </p>
            </div>

            {loadingFirsts ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-650"></div>
              </div>
            ) : firsts.length > 0 ? (
              <div className="relative border-l border-slate-800 ml-4 pl-8 space-y-8 py-2">
                {firsts.map((first) => {
                  const firstDate = new Date(first.first_date).toLocaleDateString("en-US", {
                    month: "long",
                    day: "numeric",
                    year: "numeric"
                  });
                  // Match linked observation text
                  const linkedObs = allObservations.find(obs => obs.id === first.linked_observation_id);
                  
                  return (
                    <div key={first.id} className="relative group">
                      {/* Dot */}
                      <div className="absolute -left-[41px] top-1.5 bg-indigo-500 border-4 border-slate-950 rounded-full h-[18px] w-[18px] z-10 group-hover:scale-125 transition-transform" />
                      
                      <div className="space-y-1 bg-slate-950 p-6 rounded-xl border border-slate-850 max-w-xl">
                        <span className="text-sm font-bold text-indigo-500 block">{firstDate}</span>
                        <h4 className="text-lg font-bold text-slate-100">{first.first_title}</h4>
                        {linkedObs && (
                          <p className="text-base text-slate-350 italic leading-relaxed mt-2 font-medium">
                            "{linkedObs.body || linkedObs.notes}"
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-8 bg-slate-950 border border-slate-850 rounded-2xl text-center space-y-3">
                <p className="text-base text-slate-350 italic font-medium">
                  No confirmed firsts yet. Write a new entry in your journal and Neurolens will detect potential firsts for you to confirm.
                </p>
                <Link
                  href="/observations"
                  className="inline-block px-5 py-2.5 bg-indigo-600 hover:bg-indigo-650 text-white font-bold text-sm rounded-xl transition-all"
                >
                  Go to Journal
                </Link>
              </div>
            )}
          </div>
        </div>

      ) : (
        
        /* STANDAR CHECKLIST VIEW */
        <div className="space-y-12">
          
          {/* Section 1: Journey Overview */}
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-sm space-y-6">
            <h2 className="text-2xl font-bold text-slate-50">Overview</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div className="bg-slate-950 p-6 rounded-xl border border-slate-850 text-center space-y-2">
                <span className="text-sm font-semibold text-slate-300 uppercase tracking-wider block">Things {activeChild.first_name} Is Doing</span>
                <p className="text-3xl font-bold text-slate-50">{observedCount}</p>
              </div>
              <div className="bg-slate-950 p-6 rounded-xl border border-slate-850 text-center space-y-2">
                <span className="text-sm font-semibold text-slate-300 uppercase tracking-wider block">Emerging Skills</span>
                <p className="text-3xl font-bold text-slate-50">{emergingCount}</p>
              </div>
              <div className="bg-slate-950 p-6 rounded-xl border border-slate-850 text-center space-y-2">
                <span className="text-sm font-semibold text-slate-300 uppercase tracking-wider block">Things To Watch For Next</span>
                <p className="text-3xl font-bold text-slate-50">{whatMightComeNext.length}</p>
              </div>
            </div>
          </div>

          {/* Section 2: Recent Progress */}
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-sm space-y-6">
            <h2 className="text-2xl font-bold text-slate-50">Recent Progress</h2>
            {recentProgress.length === 0 ? (
              <p className="text-base text-slate-350 italic font-medium">No progress recorded yet. Log daily moments to check off milestones.</p>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {recentProgress.map((m) => {
                  const meta = DOMAINS_METADATA.find(dm => dm.id === m.domain_id);
                  return (
                    <div key={m.id} className="bg-slate-950 p-6 rounded-xl border border-slate-850 flex items-start gap-4">
                      <div className="h-6 w-6 rounded-full bg-indigo-950 text-indigo-400 flex items-center justify-center font-bold text-sm shrink-0 mt-0.5">
                        ✓
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 flex-wrap text-sm text-slate-350 font-medium">
                          <span className="font-bold text-slate-200">{meta?.name}</span>
                          <span>&bull;</span>
                          <span>Observed at {m.age_range_low}-{m.age_range_high} Months</span>
                        </div>
                        <h4 className="text-lg font-bold text-slate-50">{m.title}</h4>
                        <p className="text-base text-slate-300 leading-relaxed font-medium">{m.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Section 3: What Might Come Next */}
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-sm space-y-6">
            <h2 className="text-2xl font-bold text-slate-50">What Might Come Next</h2>
            <p className="text-base text-slate-300 leading-relaxed font-medium">
              Based on your child's age band, you may start noticing these milestone behaviors next. Keep an eye out during play or mealtime:
            </p>
            <div className="grid grid-cols-1 gap-4">
              {whatMightComeNext.map((m) => {
                const meta = DOMAINS_METADATA.find(dm => dm.id === m.domain_id);
                return (
                  <div key={m.id} className="bg-slate-950 p-6 rounded-xl border border-slate-850 flex items-start gap-4">
                    <div className="h-6 w-6 rounded-full bg-slate-900 text-slate-400 flex items-center justify-center font-bold text-sm shrink-0 mt-0.5">
                      •
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap text-sm text-slate-350 font-medium">
                        <span className="font-bold text-slate-200">{meta?.name}</span>
                        <span>&bull;</span>
                        <span>Typically develops around {m.age_range_low}-{m.age_range_high} Months</span>
                      </div>
                      <h4 className="text-lg font-bold text-slate-50">{m.title}</h4>
                      <p className="text-base text-slate-300 leading-relaxed font-medium">{m.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section 4: Explore All Milestones */}
          <details className="bg-slate-900 border border-slate-800 rounded-2xl shadow-sm overflow-hidden group">
            <summary className="p-8 font-bold text-2xl text-slate-50 cursor-pointer hover:bg-slate-850/40 select-none flex justify-between items-center outline-none">
              Explore All Milestones
              <span className="text-sm font-bold text-indigo-600 bg-indigo-50 border border-indigo-200 px-4 py-2 rounded-xl group-open:hidden transition-all shadow-xs">
                Show Full List
              </span>
              <span className="text-sm font-bold text-slate-200 bg-slate-850 border border-slate-800 px-4 py-2 rounded-xl hidden group-open:inline-block transition-all">
                Hide Full List
              </span>
            </summary>
            
            <div className="p-8 border-t border-slate-800 space-y-8">
              <div className="flex gap-1 bg-slate-950 p-1 border border-slate-800 rounded-xl max-w-sm">
                {ageRanges.map((range) => (
                  <button
                    key={range}
                    onClick={() => setSelectedAgeRange(range)}
                    className={`flex-1 px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
                      selectedAgeRange === range
                        ? "bg-slate-800 text-slate-100 shadow-sm"
                        : "text-slate-500 hover:text-slate-200"
                    }`}
                  >
                    {range}
                  </button>
                ))}
              </div>

              <div className="space-y-8">
                {DOMAINS_METADATA.map((domainMeta) => {
                  const domainMilestones = filteredMilestones.filter((m) => m.domain_id === domainMeta.id);
                  if (domainMilestones.length === 0) return null;

                  return (
                    <div key={domainMeta.id} className="space-y-6">
                      <div className="flex items-center gap-3 pb-3 border-b border-slate-800">
                        {renderDomainIcon(domainMeta.id)}
                        <h2 className="font-semibold text-slate-50 text-xl">{domainMeta.name}</h2>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {domainMilestones.map((m) => {
                          const isExpanded = expandedMilestoneId === m.id;
                          const linkedObsIds = m.evidence_ids;

                          const unlinkedObs = allObservations.filter(
                            (obs) => !linkedObsIds.includes(obs.id) && obs.entry_type === "milestone"
                          );

                          return (
                            <div
                              key={m.id}
                              className={`p-6 bg-slate-950 border ${
                                m.evidence_count > 0 ? "border-indigo-900" : "border-slate-800"
                              } rounded-xl space-y-4 hover:border-slate-700 transition-all text-left flex flex-col justify-between`}
                            >
                              <div className="space-y-2">
                                <div className="flex justify-between items-start gap-3">
                                  <h3 className="text-base font-semibold text-slate-50 leading-snug">{m.title}</h3>
                                  {m.evidence_count > 0 ? (
                                    <span className="text-sm font-semibold text-indigo-400 bg-indigo-950/40 border border-indigo-900 px-2.5 py-0.5 rounded-lg shrink-0">
                                      {m.evidence_count} Observed
                                    </span>
                                  ) : (
                                    <span className="text-sm text-slate-500 bg-slate-900/60 border border-slate-800 px-2.5 py-0.5 rounded-lg shrink-0">
                                      No moments
                                    </span>
                                  )}
                                </div>
                                <p className="text-base text-slate-350 leading-relaxed font-sans">{m.description}</p>
                              </div>

                              <div className="flex items-center justify-between pt-3 border-t border-slate-850/60 flex-wrap gap-2">
                                <span className="text-sm font-semibold text-slate-500">
                                  {m.age_range_low}-{m.age_range_high} Months
                                </span>

                                <select
                                  value={m.status === "consistently_demonstrated" ? "observed" : m.status}
                                  disabled={!!activeChild.deleted_at}
                                  onChange={(e) => handleStatusChange(m.id, e.target.value)}
                                  className="bg-slate-900 border border-slate-800 text-sm rounded-xl px-3 py-1.5 text-slate-300 outline-none cursor-pointer disabled:opacity-50 font-medium"
                                >
                                  <option value="not_observed">Not Yet Noticed</option>
                                  <option value="emerging">Emerging</option>
                                  <option value="observed">Observed</option>
                                </select>
                              </div>

                              <div className="space-y-3 pt-1">
                                {m.evidence_count > 0 && (
                                  <button
                                    onClick={() => setExpandedMilestoneId(isExpanded ? null : m.id)}
                                    className="text-sm text-slate-500 hover:text-slate-300 font-semibold flex items-center gap-1"
                                  >
                                    {isExpanded ? "▲ Hide supporting moments" : "▼ Show supporting moments"}
                                  </button>
                                )}

                                {isExpanded && m.evidence_count > 0 && (
                                  <div className="p-4 bg-slate-905 border border-slate-800 rounded-xl space-y-3 shadow-sm">
                                    {m.evidence.map((obs) => (
                                      <div key={obs.id} className="text-sm space-y-1 relative border-b border-slate-850 pb-3 last:border-0 last:pb-0">
                                        <div className="flex justify-between items-start text-sm text-slate-500">
                                          <span>
                                            {new Date(obs.observed_at).toLocaleDateString()} &bull; {obs.observer_relation || "Parent"}
                                          </span>
                                          {!activeChild.deleted_at && (
                                            <button
                                              onClick={() => handleUnlinkEvidence(m.id, obs.id)}
                                              className="text-rose-500 hover:text-rose-455 font-semibold"
                                            >
                                              Unlink
                                            </button>
                                          )}
                                        </div>
                                        <p className="text-slate-305 leading-relaxed font-serif">"{obs.body}"</p>
                                      </div>
                                    ))}
                                  </div>
                                )}

                                {!activeChild.deleted_at && unlinkedObs.length > 0 && (
                                  <div className="flex gap-2 items-center pt-2">
                                    <select
                                      value={linkTargetObs[m.id] || ""}
                                      onChange={(e) => setLinkTargetObs(prev => ({ ...prev, [m.id]: e.target.value }))}
                                      className="flex-1 bg-slate-900 border border-slate-800 text-sm rounded-xl px-3 py-2 text-slate-400 outline-none"
                                    >
                                      <option value="">Link logged moment...</option>
                                      {unlinkedObs.map((obs) => (
                                        <option key={obs.id} value={obs.id}>
                                          {new Date(obs.observed_at).toLocaleDateString()} - {obs.body.substring(0, 25)}...
                                        </option>
                                      ))}
                                    </select>
                                    <button
                                      onClick={() => handleLinkEvidence(m.id)}
                                      className="px-3 py-2 bg-indigo-950 border border-indigo-900 text-indigo-400 hover:bg-indigo-900 text-sm font-semibold rounded-xl"
                                    >
                                      Link
                                    </button>
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </details>

        </div>
      )}
    </div>
  );
}
