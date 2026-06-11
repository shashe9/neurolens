"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useActiveChild } from "@/components/ActiveChildContext";

interface Observation {
  id: string;
  body: string;
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

interface CoverageItem {
  domain_name: string;
  milestone_count: number;
  milestones_with_evidence: number;
  milestones_without_evidence: number;
  observation_count: number;
  evidence_count: number;
}

const DOMAINS_METADATA = [
  { id: 1, name: "Communication", icon: "🗣️", color: "from-indigo-500 to-blue-500", text: "text-indigo-400" },
  { id: 2, name: "Gross Motor", icon: "🏃‍♂️", color: "from-emerald-500 to-teal-500", text: "text-emerald-400" },
  { id: 3, name: "Fine Motor", icon: "✍️", color: "from-amber-500 to-orange-500", text: "text-amber-400" },
  { id: 4, name: "Social Emotional", icon: "❤️", color: "from-rose-500 to-pink-500", text: "text-rose-400" },
  { id: 5, name: "Cognitive", icon: "🧠", color: "from-violet-500 to-purple-500", text: "text-violet-400" },
  { id: 6, name: "Behavioral Patterns", icon: "🌀", color: "from-sky-500 to-cyan-500", text: "text-sky-400" },
];

export default function Milestones() {
  const { activeChild, loading: contextLoading } = useActiveChild();
  
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [coverage, setCoverage] = useState<CoverageItem[]>([]);
  const [allObservations, setAllObservations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [selectedAgeRange, setSelectedAgeRange] = useState<string>("All");
  const [expandedMilestoneId, setExpandedMilestoneId] = useState<string | null>(null);
  const [linkTargetObs, setLinkTargetObs] = useState<{ [milestoneId: string]: string }>({});

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchMilestoneData = useCallback(async () => {
    if (!activeChild) return;
    setLoading(true);
    try {
      // 1. Fetch child milestones and evidence
      const milestonesRes = await fetch(`${apiUrl}/children/${activeChild.id}/milestones`);
      if (!milestonesRes.ok) throw new Error("Failed to load milestones.");
      const milestoneData = await milestonesRes.json();
      setMilestones(milestoneData);

      // 2. Fetch domain coverage calculations
      const coverageRes = await fetch(`${apiUrl}/children/${activeChild.id}/milestones/coverage`);
      if (coverageRes.ok) {
        const coverageData = await coverageRes.json();
        setCoverage(coverageData.domains);
      }

      // 3. Fetch all active observations (to enable inline linking)
      const obsRes = await fetch(`${apiUrl}/children/${activeChild.id}/observations`);
      if (obsRes.ok) {
        const obsData = await obsRes.json();
        setAllObservations(obsData);
      }
    } catch (err) {
      console.error("Error loading milestone data:", err);
    } finally {
      setLoading(false);
    }
  }, [activeChild, apiUrl]);

  useEffect(() => {
    fetchMilestoneData();
  }, [fetchMilestoneData]);

  // Handle status update
  const handleStatusChange = async (milestoneId: string, newStatus: string) => {
    if (!activeChild) return;
    if (activeChild.deleted_at) {
      alert("Archived child profile is read-only. Status updates are blocked.");
      return;
    }

    try {
      const res = await fetch(`${apiUrl}/children/${activeChild.id}/milestones/${milestoneId}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to update status.");
      }

      // Refresh data
      fetchMilestoneData();
    } catch (err: any) {
      alert(err.message || "Failed to update milestone status.");
    }
  };

  // Link observation as evidence
  const handleLinkEvidence = async (milestoneId: string) => {
    if (!activeChild) return;
    if (activeChild.deleted_at) {
      alert("Archived child profile is read-only. Evidence adjustments are blocked.");
      return;
    }

    const obsId = linkTargetObs[milestoneId];
    if (!obsId) {
      alert("Please select an observation to link.");
      return;
    }

    try {
      const res = await fetch(`${apiUrl}/children/${activeChild.id}/milestones/${milestoneId}/evidence`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ observation_id: obsId }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to link observation.");
      }

      // Reset selection state
      setLinkTargetObs(prev => ({ ...prev, [milestoneId]: "" }));
      // Refresh data
      fetchMilestoneData();
    } catch (err: any) {
      alert(err.message || "Failed to link evidence.");
    }
  };

  // Unlink observation evidence
  const handleUnlinkEvidence = async (milestoneId: string, obsId: string) => {
    if (!activeChild) return;
    if (activeChild.deleted_at) {
      alert("Archived child profile is read-only. Evidence adjustments are blocked.");
      return;
    }

    if (!confirm("Are you sure you want to unlink this observation as evidence?")) return;

    try {
      const res = await fetch(`${apiUrl}/children/${activeChild.id}/milestones/${milestoneId}/evidence/${obsId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to unlink observation.");
      }

      // Refresh data
      fetchMilestoneData();
    } catch (err: any) {
      alert(err.message || "Failed to unlink evidence.");
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
        <p className="text-sm text-slate-400">Please make sure a child profile is active or seeded on the database.</p>
      </div>
    );
  }

  // Filter unique age ranges
  const ageRanges = ["All", "18-24 Months", "24-36 Months"];

  // Apply filters
  const filteredMilestones = milestones.filter((m) => {
    if (selectedAgeRange === "All") return true;
    const is18to24 = m.age_range_low >= 18 && m.age_range_high <= 24;
    const is24to36 = m.age_range_low >= 24 && m.age_range_high <= 36;
    if (selectedAgeRange === "18-24 Months") return is18to24;
    if (selectedAgeRange === "24-36 Months") return is24to36;
    return true;
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
            Review Developmental Milestones
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Review behaviors aligned with evidence-based clinician criteria to populate the evidence matrix.
          </p>
        </div>
        
        {/* Age Filter Selector */}
        <div className="flex gap-2 bg-slate-900/60 p-1.5 border border-slate-800/80 rounded-xl max-w-max">
          {ageRanges.map((range) => (
            <button
              key={range}
              onClick={() => setSelectedAgeRange(range)}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                selectedAgeRange === range
                  ? "bg-indigo-500 text-white shadow-lg shadow-indigo-500/25"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Domain Coverage Summary Dashboard Panel */}
      {coverage.length > 0 && (
        <div className="bg-slate-900/30 border border-slate-850 p-6 rounded-2xl space-y-4 backdrop-blur-sm">
          <h2 className="text-sm font-bold tracking-wider text-slate-400 uppercase">Evidence Coverage Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {coverage.map((c) => {
              const meta = DOMAINS_METADATA.find((m) => m.name === c.domain_name) || {
                icon: "📊",
                color: "from-indigo-500 to-indigo-700",
                text: "text-indigo-400",
              };
              const ratio = c.milestone_count > 0 ? (c.milestones_with_evidence / c.milestone_count) * 100 : 0;

              return (
                <div
                  key={c.domain_name}
                  className="bg-slate-950/60 border border-slate-900 p-4 rounded-xl space-y-2 relative overflow-hidden flex flex-col justify-between"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{meta.icon}</span>
                      <span className="text-xs font-bold text-slate-300 truncate">{c.domain_name}</span>
                    </div>
                    
                    <div className="flex items-baseline gap-1">
                      <span className="text-lg font-bold text-slate-100">{c.milestones_with_evidence}</span>
                      <span className="text-[10px] text-slate-500">/ {c.milestone_count} supported</span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    {/* Micro Progress Bar */}
                    <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${meta.color}`}
                        style={{ width: `${ratio}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between items-center text-[9px] text-slate-500">
                      <span>{c.evidence_count} evidence items</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Loading state */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {DOMAINS_METADATA.map((domainMeta) => {
            const domainMilestones = filteredMilestones.filter((m) => m.domain_id === domainMeta.id);
            if (domainMilestones.length === 0) return null;

            return (
              <div key={domainMeta.id} className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-6">
                {/* Domain Header */}
                <div className="flex items-center gap-3 pb-3 border-b border-slate-850">
                  <span className="text-2xl">{domainMeta.icon}</span>
                  <h2 className="font-bold text-slate-200">{domainMeta.name}</h2>
                </div>

                {/* Milestones list */}
                <div className="space-y-4">
                  {domainMilestones.map((m) => {
                    const isExpanded = expandedMilestoneId === m.id;
                    const linkedObsIds = m.evidence_ids;

                    // Filter child observations that are NOT already linked to this milestone
                    const unlinkedObs = allObservations.filter(
                      (obs) => !linkedObsIds.includes(obs.id) && obs.entry_type === "milestone"
                    );

                    return (
                      <div
                        key={m.id}
                        className={`p-4 bg-slate-950/70 border ${
                          m.evidence_count > 0 ? "border-indigo-500/25 bg-slate-950/90" : "border-slate-850/80"
                        } rounded-xl space-y-4 hover:border-slate-700/60 transition-colors`}
                      >
                        <div className="space-y-1.5">
                          <div className="flex justify-between items-start gap-2">
                            <h3 className="text-xs font-semibold text-slate-200 leading-tight">{m.title}</h3>
                            {/* Evidence Indicator Badge */}
                            {m.evidence_count > 0 ? (
                              <span className="text-[9px] font-bold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded-full shrink-0">
                                🔍 {m.evidence_count} Supporting
                              </span>
                            ) : (
                              <span className="text-[9px] text-slate-500 bg-slate-900 border border-slate-850 px-2 py-0.5 rounded-full shrink-0">
                                No Evidence
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-400 leading-normal">{m.description}</p>
                        </div>

                        {/* Evidence Sources info */}
                        {m.sources.length > 0 && (
                          <div className="text-[9px] text-slate-500 font-mono italic">
                            Source: {m.sources[0].title} ({m.sources[0].year})
                          </div>
                        )}

                        {/* Action Selector */}
                        <div className="flex items-center justify-between pt-2.5 border-t border-slate-900/60">
                          <span className="text-[9px] uppercase font-bold text-slate-500">
                            {m.age_range_low}-{m.age_range_high} M
                          </span>

                          <select
                            value={m.status}
                            disabled={!!activeChild.deleted_at}
                            onChange={(e) => handleStatusChange(m.id, e.target.value)}
                            className="bg-slate-900 border border-slate-850 text-xs rounded-lg px-2.5 py-1 text-slate-300 outline-none focus:border-indigo-500/60 cursor-pointer disabled:opacity-50"
                          >
                            <option value="not_observed">⚪ Not Observed</option>
                            <option value="emerging">🟡 Emerging</option>
                            <option value="observed">🟢 Observed</option>
                            <option value="consistently_demonstrated">🏆 Consistently Demonstrated</option>
                          </select>
                        </div>

                        {/* Traceability/Evidence Expansion Panel */}
                        <div className="space-y-2 pt-1">
                          {m.evidence_count > 0 && (
                            <button
                              onClick={() => setExpandedMilestoneId(isExpanded ? null : m.id)}
                              className="text-[10px] text-indigo-400 hover:text-indigo-300 font-bold flex items-center gap-1"
                            >
                              {isExpanded ? "▲ Hide Supporting Evidence" : "▼ Show Supporting Evidence"}
                            </button>
                          )}

                          {isExpanded && m.evidence_count > 0 && (
                            <div className="p-3 bg-slate-900/40 border border-slate-900 rounded-lg space-y-2.5 animate-fadeIn">
                              {m.evidence.map((obs) => (
                                <div key={obs.id} className="text-[10px] space-y-1 relative border-b border-slate-900 pb-2 last:border-0 last:pb-0">
                                  <div className="flex justify-between items-start">
                                    <span className="text-slate-300 italic">
                                      {new Date(obs.observed_at).toLocaleDateString()} - {obs.observer_relation || "Observer"} ({obs.location || "Home"})
                                    </span>
                                    {!activeChild.deleted_at && (
                                      <button
                                        onClick={() => handleUnlinkEvidence(m.id, obs.id)}
                                        className="text-red-400 hover:text-red-300 font-semibold"
                                        title="Unlink evidence"
                                      >
                                        Remove
                                      </button>
                                    )}
                                  </div>
                                  <p className="text-slate-400 leading-normal">{obs.body}</p>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Link Evidence Inline Selector */}
                          {!activeChild.deleted_at && unlinkedObs.length > 0 && (
                            <div className="flex gap-2 items-center pt-2">
                              <select
                                value={linkTargetObs[m.id] || ""}
                                onChange={(e) => setLinkTargetObs(prev => ({ ...prev, [m.id]: e.target.value }))}
                                className="flex-1 bg-slate-950 border border-slate-850 text-[10px] rounded-lg px-2 py-1 text-slate-300 outline-none"
                              >
                                <option value="">Link observation as evidence...</option>
                                {unlinkedObs.map((obs) => (
                                  <option key={obs.id} value={obs.id}>
                                    {new Date(obs.observed_at).toLocaleDateString()} - {obs.body.substring(0, 30)}...
                                  </option>
                                ))}
                              </select>
                              <button
                                onClick={() => handleLinkEvidence(m.id)}
                                className="px-2 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 hover:bg-indigo-500/20 text-[10px] font-bold rounded-lg transition-colors"
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
      )}
    </div>
  );
}
