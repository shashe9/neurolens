"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useActiveChild } from "@/components/ActiveChildContext";
import { API_BASE_URL } from "@/config";

import { 
  Sparkles, 
  RotateCcw, 
  Check, 
  Search, 
  MapPin,
  Calendar,
  User,
  Heart,
  ChevronDown,
  ChevronUp,
  BookOpen,
  Trash2,
  Edit2
} from "lucide-react";

interface Observation {
  id: string;
  child_id: string;
  parent_id: string;
  body: string;
  entry_type: "general" | "concern" | "milestone";
  domain_id: number | null;
  milestone_id: string | null;
  observed_at: string;
  context_note: string | null;
  location: string | null;
  observer_relation: string | null;
  is_regression: boolean;
  structured_body: string | null;
  structuring_status: string | null;
  created_at: string;
}

interface Milestone {
  id: string;
  domain_id: number;
  title: string;
  description: string;
}

interface Cluster {
  cluster_id: string;
  domain_name: string;
  label: string;
  observation_ids: string[];
  observations: {
    id: string;
    body: string;
    structured_body: string | null;
    observed_at: string;
  }[];
}

const DOMAINS = [
  { id: 1, name: "Communication" },
  { id: 2, name: "Movement" },
  { id: 3, name: "Hands & Fingers" },
  { id: 4, name: "Feelings & Friendships" },
  { id: 5, name: "Thinking & Learning" },
  { id: 6, name: "Daily Activities" },
];

export default function Observations() {
  const { activeChild, activeParentId, loading: contextLoading, fetchWithAuth } = useActiveChild();

  const [observations, setObservations] = useState<Observation[]>([]);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [expandedClusters, setExpandedClusters] = useState<{ [key: string]: boolean }>({});
  const [loadingObs, setLoadingObs] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [body, setBody] = useState("");
  const [originalBody, setOriginalBody] = useState(""); 
  const [entryType, setEntryType] = useState<"general" | "concern" | "milestone">("general");
  const [domainId, setDomainId] = useState<number>(1);
  const [milestoneId, setMilestoneId] = useState<string>("");
  const [location, setLocation] = useState("");
  const [observerRelation, setObserverRelation] = useState("Mother");
  const [isRegression, setIsRegression] = useState(false);
  const [observedAt, setObservedAt] = useState(() => {
    const d = new Date();
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  });

  // Filter & Search State
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Editing State
  const [editingObs, setEditingObs] = useState<Observation | null>(null);
  const [editBody, setEditBody] = useState("");
  const [editEntryType, setEditEntryType] = useState<"general" | "concern" | "milestone">("general");
  const [editDomainId, setEditDomainId] = useState<number>(1);
  const [editMilestoneId, setEditMilestoneId] = useState<string>("");
  const [editLocation, setEditLocation] = useState("");
  const [editObserverRelation, setEditObserverRelation] = useState("");
  const [editIsRegression, setEditIsRegression] = useState(false);
  const [editObservedAt, setEditObservedAt] = useState("");

  // Deleting State
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  // Structuring State (Hidden details, parent-friendly flow)
  const [structuredDraftText, setStructuredDraftText] = useState("");
  const [structuringStatusState, setStructuringStatusState] = useState<string | null>(null); 
  const [loadingStructuring, setLoadingStructuring] = useState(false);

  const apiUrl = API_BASE_URL;

  // Prefill check
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const prefill = params.get("prefill");
      if (prefill) {
        setBody(prefill);
      }
    }
  }, []);

  // Fetch milestones
  useEffect(() => {
    const fetchMilestones = async () => {
      try {
        const res = await fetchWithAuth(`${apiUrl}/milestones`);
        if (res.ok) {
          const data = await res.json();
          setMilestones(data);
        }
      } catch (err) {
        console.error("Error loading milestones:", err);
      }
    };
    fetchMilestones();
  }, [apiUrl, fetchWithAuth]);

  // Fetch observations & timeline clusters
  const fetchObservationsAndTimeline = useCallback(async () => {
    if (!activeChild) return;
    setLoadingObs(true);
    setErrorMsg(null);
    try {
      // Fetch flat observations
      const obsRes = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/observations`);
      const obsData = obsRes.ok ? await obsRes.json() : [];
      setObservations(obsData);

      // Fetch clusters from timeline endpoint
      const timelineRes = await fetchWithAuth(`${apiUrl}/timeline/${activeChild.id}`);
      if (timelineRes.ok) {
        const timelineData = await timelineRes.json();
        setClusters(timelineData.clusters || []);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load journal timeline.");
    } finally {
      setLoadingObs(false);
    }
  }, [activeChild, apiUrl, fetchWithAuth]);

  useEffect(() => {
    fetchObservationsAndTimeline();
  }, [fetchObservationsAndTimeline]);

  // Autolink milestone on domain change in Form
  useEffect(() => {
    const filtered = milestones.filter((m) => m.domain_id === domainId);
    if (filtered.length > 0) {
      setMilestoneId(filtered[0].id);
    } else {
      setMilestoneId("");
    }
  }, [domainId, milestones]);

  // Autolink edit milestone
  useEffect(() => {
    if (editingObs) {
      const filtered = milestones.filter((m) => m.domain_id === editDomainId);
      if (filtered.length > 0 && !filtered.some((m) => m.id === editMilestoneId)) {
        setEditMilestoneId(filtered[0].id);
      }
    }
  }, [editDomainId, milestones, editingObs, editMilestoneId]);

  // AI Refinement Flow (Parent-friendly, no scores)
  const handleRefineWithAI = async () => {
    if (!activeChild || !body.trim()) return;
    setLoadingStructuring(true);
    try {
      const res = await fetchWithAuth(`${apiUrl}/observations/structure-draft`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          child_id: activeChild.id,
          body: body.trim(),
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setOriginalBody(body);
        setBody(data.structured_body);
        setStructuredDraftText(data.structured_body);
        setStructuringStatusState("completed");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingStructuring(false);
    }
  };

  const handleAcceptRefinement = () => {
    setStructuringStatusState("approved");
  };

  const handleUndoRefinement = () => {
    setBody(originalBody);
    setStructuringStatusState(null);
    setStructuredDraftText("");
  };

  // Submit Observation
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeChild || !activeParentId) return;

    if (!body.trim()) return;

    try {
      const payload = {
        parent_id: activeParentId,
        body: body.trim(),
        entry_type: entryType,
        domain_id: domainId,
        milestone_id: entryType === "milestone" && milestoneId ? milestoneId : null,
        observed_at: new Date(observedAt).toISOString(),
        location: location.trim() || null,
        observer_relation: observerRelation.trim() || null,
        is_regression: isRegression,
        structured_body: structuringStatusState === "approved" ? structuredDraftText : null,
        structuring_status: structuringStatusState || null
      };

      const res = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/observations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setBody("");
        setOriginalBody("");
        setStructuredDraftText("");
        setStructuringStatusState(null);
        setIsRegression(false);
        setLocation("");
        const d = new Date();
        setObservedAt(new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16));

        // Prompt caregiver if a First is candidate-detected
        if (data.first_suggestion) {
          const confirmFirst = window.confirm(
            `Neurolens detected a potential special moment:\n"${data.first_suggestion}"\n\nWould you like to save this as a confirmed First?`
          );
          if (confirmFirst) {
            try {
              await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/firsts`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  first_title: data.first_suggestion,
                  first_date: new Date(observedAt).toISOString().split("T")[0],
                  linked_observation_id: data.id
                })
              });
              alert("Saved to Firsts Timeline!");
            } catch (err) {
              console.error("Error saving confirmed first:", err);
            }
          }
        }

        // Prompt caregiver if OIE detected a milestone candidate
        if (data.milestone_suggestion) {
          const confirmMilestone = window.confirm(
            `Neurolens OIE detected a potential milestone achievement:\n\nDomain: ${data.milestone_suggestion.domain}\nMilestone: "${data.milestone_suggestion.title}"\n\nWould you like to record this milestone as achieved and link this log as evidence?`
          );
          if (confirmMilestone) {
            try {
              // 1. Update milestone status to observed
              await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/milestones/${data.milestone_suggestion.milestone_id}/status`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  status: "observed",
                  notes: `Linked automatically from journal log: "${data.body}"`
                })
              });
              
              // 2. Link this observation as evidence
              await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/milestones/${data.milestone_suggestion.milestone_id}/evidence`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  observation_id: data.id
                })
              });
              
              alert("Milestone updated and evidence linked!");
            } catch (err) {
              console.error("Error confirming milestone suggestion:", err);
            }
          }
        }

        fetchObservationsAndTimeline();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const startEdit = (obs: Observation) => {
    setEditingObs(obs);
    setEditBody(obs.body);
    setEditEntryType(obs.entry_type);
    setEditDomainId(obs.domain_id || 1);
    setEditMilestoneId(obs.milestone_id || "");
    setEditLocation(obs.location || "");
    setEditObserverRelation(obs.observer_relation || "Mother");
    setEditIsRegression(obs.is_regression);
    setEditObservedAt(new Date(new Date(obs.observed_at).getTime() - new Date(obs.observed_at).getTimezoneOffset() * 60000).toISOString().slice(0, 16));
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingObs) return;

    try {
      const payload = {
        body: editBody.trim(),
        entry_type: editEntryType,
        domain_id: editDomainId,
        milestone_id: editEntryType === "milestone" && editMilestoneId ? editMilestoneId : null,
        observed_at: new Date(editObservedAt).toISOString(),
        location: editLocation.trim() || null,
        observer_relation: editObserverRelation.trim() || null,
        is_regression: editIsRegression,
      };

      const res = await fetchWithAuth(`${apiUrl}/observations/${editingObs.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setEditingObs(null);
        fetchObservationsAndTimeline();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (obsId: string) => {
    if (!activeParentId) return;
    try {
      const res = await fetchWithAuth(`${apiUrl}/observations/${obsId}?deleted_by=${activeParentId}`, {
        method: "DELETE",
      });
      if (res.ok) {
        setDeleteConfirmId(null);
        fetchObservationsAndTimeline();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const toggleCluster = (clusterId: string) => {
    setExpandedClusters((prev) => ({ ...prev, [clusterId]: !prev[clusterId] }));
  };

  // Build Chronology of Observations & collapsed Clusters
  const getGroupedChronology = () => {
    const query = searchQuery.trim().toLowerCase();
    const clusteredObsIds = new Set(clusters.flatMap((c) => c.observation_ids));

    const chronology: {
      [monthYear: string]: (
        | { type: "observation"; data: Observation; date: Date }
        | { type: "cluster"; data: Cluster; date: Date }
      )[];
    } = {};

    // Map Clusters
    clusters.forEach((cluster) => {
      let latestDate = new Date(0);
      cluster.observations.forEach((o) => {
        const d = new Date(o.observed_at);
        if (d > latestDate) latestDate = d;
      });

      const monthYear = latestDate.toLocaleString("en-US", { month: "long", year: "numeric" });
      
      // Filter check
      const matchesQuery = !query || 
        cluster.label.toLowerCase().includes(query) || 
        cluster.observations.some(o => o.body.toLowerCase().includes(query));

      if (matchesQuery) {
        if (!chronology[monthYear]) chronology[monthYear] = [];
        chronology[monthYear].push({ type: "cluster", data: cluster, date: latestDate });
      }
    });

    // Map Independent Observations
    observations.forEach((obs) => {
      if (!clusteredObsIds.has(obs.id)) {
        const date = new Date(obs.observed_at);
        const monthYear = date.toLocaleString("en-US", { month: "long", year: "numeric" });

        const matchesQuery = !query || 
          obs.body.toLowerCase().includes(query) ||
          (obs.location && obs.location.toLowerCase().includes(query)) ||
          (obs.observer_relation && obs.observer_relation.toLowerCase().includes(query));

        if (matchesQuery) {
          if (!chronology[monthYear]) chronology[monthYear] = [];
          chronology[monthYear].push({ type: "observation", data: obs, date });
        }
      }
    });

    // Sort by Date
    Object.keys(chronology).forEach((monthYear) => {
      chronology[monthYear].sort((a, b) => b.date.getTime() - a.date.getTime());
    });

    // Filter empty months
    const filteredGrouped: typeof chronology = {};
    Object.entries(chronology).forEach(([mY, list]) => {
      if (list.length > 0) filteredGrouped[mY] = list;
    });

    return filteredGrouped;
  };

  if (contextLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!activeChild) {
    return (
      <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl text-center max-w-lg mx-auto mt-12 space-y-4 shadow-sm">
        <h2 className="text-2xl font-bold text-slate-100">No Child Profile Selected</h2>
        <p className="text-base text-slate-400 font-semibold">Please select a child profile to log observations.</p>
      </div>
    );
  }

  const groupedChronology = getGroupedChronology();

  return (
    <div className="max-w-4xl mx-auto space-y-10 py-6">
      
      {/* Title */}
      <div className="text-left space-y-2">
        <h1 className="text-4xl font-bold text-slate-100 leading-tight">Tell us about a moment you noticed today</h1>
        <p className="text-lg text-slate-300">
          Write daily moments to capture a reliable picture of your child's growth.
        </p>
      </div>

      {/* Diary Entry Form */}
      <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-sm space-y-6">
        <h2 className="text-2xl font-bold text-slate-100">Describe the moment</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Main prompt writing area */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-base font-semibold text-slate-200">Write your observations below</span>
              <button
                type="button"
                disabled={body.trim().length < 5 || loadingStructuring}
                onClick={handleRefineWithAI}
                className="text-sm font-semibold text-indigo-400 hover:text-indigo-300 transition-colors disabled:opacity-40 disabled:pointer-events-none flex items-center gap-1"
              >
                <Sparkles className="h-4 w-4" />
                {loadingStructuring ? "Making readable..." : "Make this easier to read"}
              </button>
            </div>

            <textarea
              placeholder="e.g., Today Rohan pointed at a puppy in the park, turned back to look at me, and smiled to share the moment. Or, Rohan used a two-word phrase to ask for apple juice."
              rows={4}
              value={body}
              onChange={(e) => {
                setBody(e.target.value);
                if (structuringStatusState) {
                  setStructuringStatusState(null);
                  setStructuredDraftText("");
                }
              }}
              className="w-full bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 rounded-xl p-4 text-base outline-none resize-none leading-relaxed font-medium"
            ></textarea>

            {/* AI Refinement Actions */}
            {structuringStatusState === "completed" && (
              <div className="bg-indigo-950/20 border border-indigo-900/40 p-4 rounded-xl text-left space-y-3">
                <p className="text-sm text-slate-300 leading-relaxed font-semibold">
                  We refined the wording to be easier to link to milestone records. Would you like to keep this draft?
                </p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={handleAcceptRefinement}
                    className="px-4 py-2 bg-indigo-650 text-white font-semibold text-sm rounded-lg hover:bg-indigo-750 flex items-center gap-1"
                  >
                    <Check className="h-4 w-4" /> Accept
                  </button>
                  <button
                    type="button"
                    onClick={handleUndoRefinement}
                    className="px-4 py-2 border border-slate-800 bg-slate-950 text-sm font-semibold rounded-lg text-slate-350 hover:bg-slate-900 flex items-center gap-1"
                  >
                    <RotateCcw className="h-4 w-4" /> Undo
                  </button>
                </div>
              </div>
            )}

            {structuringStatusState === "approved" && (
              <div className="bg-emerald-950/25 border border-emerald-900/30 px-4 py-2 rounded-xl text-sm text-emerald-400 flex items-center gap-1.5 font-bold">
                <Check className="h-4 w-4 shrink-0" /> Refined text draft selected.
              </div>
            )}
          </div>

          {/* More Details Collapsible Container */}
          <details className="group border-t border-slate-800 pt-4 outline-none">
            <summary className="flex items-center justify-between text-base font-bold text-indigo-400 hover:text-indigo-300 cursor-pointer list-none select-none">
              <span>More Details</span>
              <ChevronDown className="h-5 w-5 transform group-open:rotate-180 transition-transform text-slate-400" />
            </summary>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 cursor-default">
              {/* Type of Moment */}
              <div className="space-y-1.5">
                <label className="block text-sm font-semibold text-slate-200">Type of Moment</label>
                <select
                  value={entryType}
                  onChange={(e) => setEntryType(e.target.value as any)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-base text-slate-100 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                >
                  <option value="general">General Observation</option>
                  <option value="concern">Note for Visit</option>
                  <option value="milestone">Developmental Milestone</option>
                </select>
              </div>

              {/* Who Noticed This */}
              <div className="space-y-1.5">
                <label className="block text-sm font-semibold text-slate-200">Who Noticed This</label>
                <select
                  value={observerRelation}
                  onChange={(e) => setObserverRelation(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-base text-slate-100 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                >
                  <option value="Mother">Mother</option>
                  <option value="Father">Father</option>
                  <option value="Caregiver">Caregiver</option>
                  <option value="Teacher">Teacher</option>
                  <option value="Clinician">Clinician</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              {/* Development Area */}
              <div className="space-y-1.5">
                <label className="block text-sm font-semibold text-slate-200">Development Area</label>
                <select
                  value={domainId}
                  onChange={(e) => setDomainId(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-base text-slate-100 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                >
                  {DOMAINS.map((domain) => (
                    <option key={domain.id} value={domain.id}>
                      {domain.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* When was this? */}
              <div className="space-y-1.5">
                <label className="block text-sm font-semibold text-slate-200">When was this?</label>
                <input
                  type="datetime-local"
                  value={observedAt}
                  onChange={(e) => setObservedAt(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-base text-slate-100 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                />
              </div>

              {/* Linked Milestone Checklist Dropdown */}
              {entryType === "milestone" && (
                <div className="space-y-1.5 md:col-span-2">
                  <label className="block text-sm font-semibold text-slate-200">Which milestone was completed?</label>
                  <select
                    value={milestoneId}
                    onChange={(e) => setMilestoneId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-base text-slate-100 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                  >
                    {milestones.filter((m) => m.domain_id === domainId).length === 0 ? (
                      <option value="">No milestones configured for this area</option>
                    ) : (
                      milestones
                        .filter((m) => m.domain_id === domainId)
                        .map((m) => (
                          <option key={m.id} value={m.id}>
                            {m.title}
                          </option>
                        ))
                    )}
                  </select>
                </div>
              )}

              {/* Where was this? */}
              <div className="space-y-1.5 md:col-span-2">
                <label className="block text-sm font-semibold text-slate-200">Where was this? (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Living room, playground, mealtime"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-base text-slate-100 placeholder-slate-500 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                />
              </div>

              {/* Something That Changed (Regression toggle) */}
              <div className="flex items-start gap-3 pt-2 md:col-span-2">
                <input
                  type="checkbox"
                  id="regression"
                  checked={isRegression}
                  onChange={(e) => setIsRegression(e.target.checked)}
                  className="h-5 w-5 bg-slate-950 border-slate-800 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer mt-0.5"
                />
                <div className="text-left space-y-1">
                  <label htmlFor="regression" className="text-base font-semibold text-slate-100 cursor-pointer select-none">
                    Something that changed?
                  </label>
                  <p className="text-sm text-slate-400 leading-relaxed font-semibold">
                    Check this if it represents a sudden shift or loss of a skill they used to demonstrate.
                  </p>
                </div>
              </div>
            </div>
          </details>

          <button
            type="submit"
            className="w-full py-4 bg-indigo-600 hover:bg-indigo-750 text-white font-bold text-base rounded-xl transition-all shadow-sm cursor-pointer"
          >
            Add To Journal
          </button>
        </form>
      </div>

      {/* Timeline Stream */}
      <div className="space-y-6">
        
        {/* Stream Header & Search */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <h2 className="text-2xl font-bold text-slate-100">Recent Moments</h2>
          <div className="w-full sm:w-80 relative">
            <input
              type="text"
              placeholder="Search moments..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 rounded-xl pl-10 pr-4 py-2.5 text-base outline-none font-semibold"
            />
            <Search className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
          </div>
        </div>

        {/* Timeline Log List */}
        {loadingObs ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : Object.keys(groupedChronology).length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl py-12 px-6 text-center space-y-4 shadow-sm">
            <BookOpen className="h-12 w-12 text-slate-400 mx-auto" />
            <h3 className="text-lg font-bold text-slate-100">No moments found</h3>
            <p className="text-sm text-slate-400 max-w-sm mx-auto leading-relaxed font-semibold">
              Start writing daily moments above to begin tracking milestones and patterns.
            </p>
          </div>
        ) : (
          <div className="space-y-8 relative before:absolute before:top-2 before:bottom-2 before:left-[17px] before:w-[1.5px] before:bg-slate-800">
            {Object.entries(groupedChronology).map(([monthYear, items]) => (
              <div key={monthYear} className="space-y-4">
                
                {/* Month Group Header */}
                <div className="flex items-center gap-4 relative z-10">
                  <div className="h-9 w-9 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center shadow-sm">
                    <div className="h-2 w-2 rounded-full bg-indigo-500"></div>
                  </div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-355 text-slate-350 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 shadow-sm">
                    {monthYear}
                  </h3>
                </div>

                {/* Stream Cards */}
                <div className="pl-12 space-y-5">
                  {items.map((item) => {
                    if (item.type === "observation") {
                      const obs = item.data;
                      const isEditing = editingObs?.id === obs.id;
                      const isDeleting = deleteConfirmId === obs.id;

                      const formattedDate = new Date(obs.observed_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      });

                      const domainObj = DOMAINS.find((d) => d.id === obs.domain_id);
                      const domainName = domainObj ? domainObj.name : "General";

                      let borderClass = "border-slate-800";
                      let bgClass = "bg-slate-900";
                      let statusText = "General Moment";
                      let badgeColor = "bg-slate-800 text-slate-400 border border-slate-750";

                      if (obs.entry_type === "concern") {
                        borderClass = "border-rose-900/60";
                        bgClass = "bg-rose-950/10";
                        statusText = "Note for Visit";
                        badgeColor = "bg-rose-950/30 text-rose-400 border border-rose-900/50";
                      } else if (obs.entry_type === "milestone") {
                        borderClass = "border-emerald-900/60";
                        bgClass = "bg-emerald-950/10";
                        statusText = "Completed Milestone";
                        badgeColor = "bg-emerald-950/30 text-emerald-400 border border-emerald-900/50";
                      }

                      return (
                        <div
                          key={obs.id}
                          className={`p-6 rounded-2xl border ${borderClass} ${bgClass} space-y-4 shadow-sm relative`}
                        >
                          {isEditing ? (
                            /* Inline Edit Form */
                            <form onSubmit={handleUpdate} className="space-y-4">
                              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                                <span className="text-base font-bold text-slate-100">Edit Journal Entry</span>
                                <div className="flex items-center gap-2">
                                  <button
                                    type="button"
                                    onClick={() => setEditingObs(null)}
                                    className="text-sm font-bold text-slate-400 hover:text-slate-300 px-3 py-1.5 rounded-lg border border-slate-800"
                                  >
                                    Cancel
                                  </button>
                                  <button
                                    type="submit"
                                    className="text-sm bg-indigo-650 hover:bg-indigo-700 text-white font-bold px-4 py-1.5 rounded-lg"
                                  >
                                    Save
                                  </button>
                                </div>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-1">
                                  <label className="text-sm font-semibold text-slate-200">Who Noticed This</label>
                                  <select
                                    value={editObserverRelation}
                                    onChange={(e) => setEditObserverRelation(e.target.value)}
                                    className="w-full bg-slate-950 border border-slate-850 text-slate-150 rounded-xl px-3 py-2 text-base outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                                  >
                                    <option value="Mother">Mother</option>
                                    <option value="Father">Father</option>
                                    <option value="Caregiver">Caregiver</option>
                                    <option value="Teacher">Teacher</option>
                                    <option value="Clinician">Clinician</option>
                                    <option value="Other">Other</option>
                                  </select>
                                </div>
                                <div className="space-y-1">
                                  <label className="text-sm font-semibold text-slate-200">When was this?</label>
                                  <input
                                    type="datetime-local"
                                    value={editObservedAt}
                                    onChange={(e) => setEditObservedAt(e.target.value)}
                                    className="w-full bg-slate-950 border border-slate-850 text-slate-150 rounded-xl px-3 py-2 text-base outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                                  />
                                </div>
                                <div className="space-y-1">
                                  <label className="text-sm font-semibold text-slate-200">Type of Moment</label>
                                  <select
                                    value={editEntryType}
                                    onChange={(e) => setEditEntryType(e.target.value as any)}
                                    className="w-full bg-slate-950 border border-slate-850 text-slate-150 rounded-xl px-3 py-2 text-base outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                                  >
                                    <option value="general">General Observation</option>
                                    <option value="concern">Note for Visit</option>
                                    <option value="milestone">Completed Milestone</option>
                                  </select>
                                </div>
                                <div className="space-y-1">
                                  <label className="text-sm font-semibold text-slate-200">Development Area</label>
                                  <select
                                    value={editDomainId}
                                    onChange={(e) => setEditDomainId(Number(e.target.value))}
                                    className="w-full bg-slate-950 border border-slate-850 text-slate-150 rounded-xl px-3 py-2 text-base outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                                  >
                                    {DOMAINS.map((d) => (
                                      <option key={d.id} value={d.id}>{d.name}</option>
                                    ))}
                                  </select>
                                </div>
                              </div>

                              <div className="space-y-1">
                                <label className="text-sm font-semibold text-slate-200">Observation Details</label>
                                <textarea
                                  rows={3}
                                  value={editBody}
                                  onChange={(e) => setEditBody(e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-850 text-slate-150 rounded-xl p-3 text-base outline-none resize-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                                />
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-1">
                                  <label className="text-sm font-semibold text-slate-200">Where was this?</label>
                                  <input
                                    type="text"
                                    value={editLocation}
                                    onChange={(e) => setEditLocation(e.target.value)}
                                    className="w-full bg-slate-950 border border-slate-850 text-slate-150 rounded-xl px-3 py-2 text-base outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-semibold"
                                  />
                                </div>
                                <div className="flex items-center gap-2 pt-6">
                                  <input
                                    type="checkbox"
                                    id="editRegression"
                                    checked={editIsRegression}
                                    onChange={(e) => setEditIsRegression(e.target.checked)}
                                    className="h-5 w-5 cursor-pointer accent-indigo-650 bg-slate-950 border border-slate-800 rounded text-indigo-655 focus:ring-indigo-500"
                                  />
                                  <label htmlFor="editRegression" className="text-sm font-semibold text-slate-200 cursor-pointer select-none">
                                    Something changed / loss of skill?
                                  </label>
                                </div>
                              </div>
                            </form>
                          ) : isDeleting ? (
                            /* Confirm Delete dialog */
                            <div className="space-y-3">
                              <h4 className="text-base font-bold text-rose-500">Delete this journal entry?</h4>
                              <p className="text-sm text-slate-300 leading-relaxed font-semibold">
                                This will remove the moment from your journal feed. It will be excluded from future visit summaries.
                              </p>
                              <div className="flex gap-2 justify-end">
                                <button
                                  onClick={() => setDeleteConfirmId(null)}
                                  className="px-4 py-2 border border-slate-800 text-slate-400 font-bold text-sm rounded-lg hover:bg-slate-850"
                                >
                                  Cancel
                                </button>
                                <button
                                  onClick={() => handleDelete(obs.id)}
                                  className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white font-semibold text-sm rounded-lg"
                                >
                                  Delete
                                </button>
                              </div>
                            </div>
                          ) : (
                            /* Regular Diary Card */
                            <>
                              <div className="flex items-center justify-between flex-wrap gap-2">
                                <div className="flex items-center gap-3">
                                  <span className={`text-sm font-bold uppercase tracking-wide px-3 py-1 rounded-full border ${badgeColor}`}>
                                    {statusText}
                                  </span>
                                  {obs.is_regression && (
                                    <span className="text-sm font-bold tracking-wide text-orange-400 bg-orange-950/30 px-3 py-1 rounded-full border border-orange-900/50">
                                      Something Changed
                                    </span>
                                  )}
                                </div>
                                <span className="text-sm text-slate-400 font-bold">{formattedDate}</span>
                              </div>

                              <p className="text-base text-slate-100 leading-relaxed font-serif whitespace-pre-wrap">
                                "{obs.structured_body || obs.body}"
                              </p>
                              
                              {obs.structured_body && obs.structured_body !== obs.body && (
                                <p className="text-sm text-slate-400 italic bg-slate-950 p-3 rounded-xl border border-slate-850 font-medium">
                                  Original raw note: "{obs.body}"
                                </p>
                              )}

                              <div className="flex items-center justify-between border-t border-slate-850 pt-3 flex-wrap gap-2 text-sm text-slate-400">
                                <div className="flex flex-wrap gap-4 font-medium">
                                  <span>Area: {domainName}</span>
                                  {obs.observer_relation && <span>By: {obs.observer_relation}</span>}
                                  {obs.location && <span>Where: {obs.location}</span>}
                                </div>
                                
                                <div className="flex items-center gap-3 opacity-60 hover:opacity-100 transition-opacity">
                                  <button
                                    onClick={() => startEdit(obs)}
                                    className="text-slate-400 hover:text-indigo-400 flex items-center gap-1 font-bold"
                                  >
                                    <Edit2 className="h-3.5 w-3.5" /> Edit
                                  </button>
                                  <span className="text-slate-800">|</span>
                                  <button
                                    onClick={() => setDeleteConfirmId(obs.id)}
                                    className="text-rose-455 hover:text-rose-500 flex items-center gap-1 font-bold"
                                  >
                                    <Trash2 className="h-3.5 w-3.5" /> Delete
                                  </button>
                                </div>
                              </div>
                            </>
                          )}
                        </div>
                      );
                    } else {
                      // CLUSTERS (Collapsed Patterns)
                      const cluster = item.data;
                      const isExpanded = !!expandedClusters[cluster.cluster_id];
                      const latestDateStr = item.date.toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                      });

                      const domainObj = DOMAINS.find(d => d.name === cluster.domain_name);
                      const domainLabel = domainObj ? domainObj.name : cluster.domain_name;

                      return (
                        <div
                          key={cluster.cluster_id}
                          className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4"
                        >
                          <div className="flex items-start justify-between gap-4 flex-wrap">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <span className="text-sm uppercase tracking-wide font-bold text-slate-350 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-850">
                                  {domainLabel} Pattern
                                </span>
                                <span className="text-sm text-slate-400 font-semibold">
                                  You've mentioned this a few times recently (Last: {latestDateStr})
                                </span>
                              </div>
                              <h4 className="text-lg font-bold text-slate-100 leading-snug mt-1">
                                {cluster.label}
                              </h4>
                            </div>

                            <button
                              onClick={() => toggleCluster(cluster.cluster_id)}
                              className="px-4 py-2 bg-slate-950 hover:bg-slate-850 text-slate-300 text-sm font-semibold rounded-xl border border-slate-800 transition-all flex items-center gap-1"
                            >
                              <span>{isExpanded ? "Collapse" : `Expand (${cluster.observations.length} logs)`}</span>
                              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                            </button>
                          </div>

                          {/* Expanded logs of this cluster pattern */}
                          {isExpanded && (
                            <div className="space-y-4 mt-3 pt-4 border-t border-slate-850 pl-4 relative before:absolute before:top-2 before:bottom-2 before:left-[4px] before:w-[1.5px] before:bg-slate-800">
                              {cluster.observations.map((subObs) => {
                                const subDate = new Date(subObs.observed_at).toLocaleDateString("en-US", {
                                  month: "short",
                                  day: "numeric",
                                  hour: "2-digit",
                                  minute: "2-digit",
                                });

                                return (
                                  <div key={subObs.id} className="relative pl-6 space-y-1 text-left">
                                    <div className="absolute top-2.5 left-[-1.5px] h-2 w-2 rounded-full bg-slate-400 border border-slate-900 shadow-sm"></div>
                                    <div className="flex justify-between text-sm text-slate-400">
                                      <span>Journal Moment</span>
                                      <span>{subDate}</span>
                                    </div>
                                    <p className="text-base text-slate-100 font-serif leading-relaxed">
                                      "{subObs.structured_body || subObs.body}"
                                    </p>
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      );
                    }
                  })}
                </div>

              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
