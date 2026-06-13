"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useActiveChild } from "@/components/ActiveChildContext";
import { ResponsibleAINotice } from "@/components/ResponsibleAINotice";


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
  created_at: string;
}

interface Milestone {
  id: string;
  domain_id: number;
  title: string;
  description: string;
}

const DOMAINS = [
  { id: 1, name: "Communication" },
  { id: 2, name: "Gross Motor" },
  { id: 3, name: "Fine Motor" },
  { id: 4, name: "Social Emotional" },
  { id: 5, name: "Cognitive" },
  { id: 6, name: "Behavioral Patterns" },
];

export default function Observations() {
  const { activeChild, activeParentId, loading: contextLoading, fetchWithAuth } = useActiveChild();

  const [observations, setObservations] = useState<Observation[]>([]);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [loadingObs, setLoadingObs] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [body, setBody] = useState("");
  const [entryType, setEntryType] = useState<"general" | "concern" | "milestone">("general");
  const [domainId, setDomainId] = useState<number>(1);
  const [milestoneId, setMilestoneId] = useState<string>("");
  const [location, setLocation] = useState("");
  const [observerRelation, setObserverRelation] = useState("Mother");
  const [isRegression, setIsRegression] = useState(false);
  const [observedAt, setObservedAt] = useState(() => {
    const d = new Date();
    // Format to local ISO-like string for datetime-local input
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  });

  // Filter State
  const [filterDomain, setFilterDomain] = useState<string>("");
  const [filterType, setFilterType] = useState<string>("");
  const [filterStart, setFilterStart] = useState<string>("");
  const [filterEnd, setFilterEnd] = useState<string>("");
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

  // AI Suggestions and Feedback States
  const [aiSuggestions, setAiSuggestions] = useState<any | null>(null);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [suggestionError, setSuggestionError] = useState<string | null>(null);
  const [expandedSuggestions, setExpandedSuggestions] = useState<{ [key: string]: boolean }>({});
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<{ [key: string]: boolean }>({});
  const [feedbackComment, setFeedbackComment] = useState<{ [key: string]: string }>({});
  const [showCommentBox, setShowCommentBox] = useState<{ [key: string]: boolean }>({});

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleAnalyzeWithAI = async () => {
    if (!activeChild || !activeParentId) return;
    if (body.trim().length < 10) {
      setSuggestionError("Observation details must be at least 10 characters long.");
      return;
    }
    setLoadingSuggestions(true);
    setSuggestionError(null);
    setAiSuggestions(null);
    setExpandedSuggestions({});
    setFeedbackSubmitted({});
    setFeedbackComment({});
    setShowCommentBox({});

    try {
      const dob = new Date(activeChild.date_of_birth);
      const now = new Date();
      const yearsDiff = now.getFullYear() - dob.getFullYear();
      const monthsDiff = now.getMonth() - dob.getMonth();
      let ageMonths = yearsDiff * 12 + monthsDiff;
      if (now.getDate() < dob.getDate()) ageMonths -= 1;
      const childAgeMonths = ageMonths >= 0 ? ageMonths : 0;

      const payload = {
        observation_text: body.trim(),
        child_id: activeChild.id,
        child_age_months: childAgeMonths
      };

      const res = await fetchWithAuth(`${apiUrl}/ai/suggest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to analyze observation.");
      }

      const data = await res.json();
      setAiSuggestions(data);
    } catch (err: any) {
      setSuggestionError(err.message || "Something went wrong during analysis.");
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleLinkSuggestion = async (suggestedMilestone: any) => {
    if (!aiSuggestions || !activeParentId || !activeChild) return;

    try {
      const matchedDomain = DOMAINS.find(d => d.name.toLowerCase() === suggestedMilestone.domain_name.toLowerCase());
      const domainId = matchedDomain ? matchedDomain.id : 1;

      const payload = {
        selected_domain: suggestedMilestone.domain_name,
        selected_milestone_id: suggestedMilestone.milestone_id,
        interaction_type: "accepted"
      };

      const res = await fetchWithAuth(`${apiUrl}/ai/confirm/${aiSuggestions.event_id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error("Failed to link suggestion on backend.");
      }

      setEntryType("milestone");
      setDomainId(domainId);
      setMilestoneId(suggestedMilestone.milestone_id);

      alert(`Milestone successfully linked: "${suggestedMilestone.title}". Fill out other fields and click "Add to Report Evidence" to submit observation.`);
    } catch (err: any) {
      alert(err.message || "Failed to link suggestion.");
    }
  };

  const handleSubmitFeedback = async (milestoneId: string, feedbackType: "helpful" | "not_helpful", commentText?: string) => {
    if (!aiSuggestions || !activeParentId || !activeChild) return;

    try {
      const payload = {
        parent_id: activeParentId,
        child_id: activeChild.id,
        ai_suggestion_event_id: aiSuggestions.event_id,
        milestone_id: milestoneId,
        feedback_type: feedbackType,
        comment: commentText || null
      };

      const res = await fetchWithAuth(`${apiUrl}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error("Failed to submit feedback.");
      }

      setFeedbackSubmitted(prev => ({ ...prev, [milestoneId]: true }));
    } catch (err: any) {
      alert(err.message || "Failed to submit feedback.");
    }
  };

  // Fetch Milestones once on mount

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

  // Fetch observations callback
  const fetchObservations = useCallback(async () => {
    if (!activeChild) return;
    setLoadingObs(true);
    setErrorMsg(null);
    try {
      const params = new URLSearchParams();
      if (filterDomain) params.append("domain_id", filterDomain);
      if (filterType) params.append("entry_type", filterType);
      if (filterStart) params.append("date_start", filterStart);
      if (filterEnd) params.append("date_end", filterEnd);

      const res = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/observations?${params.toString()}`);
      if (!res.ok) throw new Error("Failed to load observations.");
      const data: Observation[] = await res.json();
      setObservations(data);
    } catch (err: any) {
      setErrorMsg(err.message || "Something went wrong fetching observations.");
    } finally {
      setLoadingObs(false);
    }
  }, [activeChild, filterDomain, filterType, filterStart, filterEnd, apiUrl, fetchWithAuth]);

  // Refetch when child or filters change
  useEffect(() => {
    fetchObservations();
  }, [fetchObservations]);

  // Automatically adjust milestone selection if domain changes in Form
  useEffect(() => {
    const filtered = milestones.filter((m) => m.domain_id === domainId);
    if (filtered.length > 0) {
      setMilestoneId(filtered[0].id);
    } else {
      setMilestoneId("");
    }
  }, [domainId, milestones]);

  // Same for Edit Form
  useEffect(() => {
    if (editingObs) {
      const filtered = milestones.filter((m) => m.domain_id === editDomainId);
      if (filtered.length > 0 && !filtered.some((m) => m.id === editMilestoneId)) {
        setEditMilestoneId(filtered[0].id);
      }
    }
  }, [editDomainId, milestones, editingObs, editMilestoneId]);

  // Form Submit (Create)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeChild || !activeParentId) return;

    if (!body.trim()) {
      alert("Observation details cannot be empty.");
      return;
    }

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
      };

      const res = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/observations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to create observation.");
      }

      // Reset Form on Success
      setBody("");
      setIsRegression(false);
      setLocation("");
      // Keep observer name and timestamp up-to-date
      const d = new Date();
      setObservedAt(new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16));

      // Refresh Observations
      fetchObservations();
    } catch (err: any) {
      alert(err.message || "Failed to create observation.");
    }
  };

  // Edit Trigger
  const startEdit = (obs: Observation) => {
    setEditingObs(obs);
    setEditBody(obs.body);
    setEditEntryType(obs.entry_type);
    setEditDomainId(obs.domain_id || 1);
    setEditMilestoneId(obs.milestone_id || "");
    setEditLocation(obs.location || "");
    setEditObserverRelation(obs.observer_relation || "");
    setEditIsRegression(obs.is_regression);
    setEditObservedAt(new Date(new Date(obs.observed_at).getTime() - new Date(obs.observed_at).getTimezoneOffset() * 60000).toISOString().slice(0, 16));
  };

  // Edit Save
  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingObs) return;

    if (!editBody.trim()) {
      alert("Observation details cannot be empty.");
      return;
    }

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

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to update observation.");
      }

      setEditingObs(null);
      fetchObservations();
    } catch (err: any) {
      alert(err.message || "Failed to update observation.");
    }
  };

  // Soft Delete Trigger
  const handleDelete = async (obsId: string) => {
    if (!activeParentId) return;
    try {
      const res = await fetchWithAuth(`${apiUrl}/observations/${obsId}?deleted_by=${activeParentId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to delete observation.");
      }

      setDeleteConfirmId(null);
      fetchObservations();
    } catch (err: any) {
      alert(err.message || "Failed to delete observation.");
    }
  };

  // Group Observations by Month/Year for chronological layout
  const getGroupedObservations = () => {
    const filtered = observations.filter((obs) => {
      if (!searchQuery.trim()) return true;
      return obs.body.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (obs.location && obs.location.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (obs.observer_relation && obs.observer_relation.toLowerCase().includes(searchQuery.toLowerCase()));
    });

    const groups: { [key: string]: Observation[] } = {};
    filtered.forEach((obs) => {
      const date = new Date(obs.observed_at);
      const key = date.toLocaleString("en-US", { month: "long", year: "numeric" });
      if (!groups[key]) groups[key] = [];
      groups[key].push(obs);
    });

    return groups;
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

  const groupedObs = getGroupedObservations();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Form Column */}
      <div className="lg:col-span-1">
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl space-y-6 sticky top-24 backdrop-blur-sm">
          <div>
            <h2 className="text-xl font-bold text-slate-100 bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
              Log Observation
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Add qualitative parent observations. Logs feed the clinician report as evidence snapshots.
            </p>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            {/* Observer */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Observer Relation</label>
                <select
                  value={observerRelation}
                  onChange={(e) => setObserverRelation(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-100 outline-none transition-colors"
                >
                  <option value="Mother">Mother</option>
                  <option value="Father">Father</option>
                  <option value="Caregiver">Caregiver</option>
                  <option value="Teacher">Teacher</option>
                  <option value="Clinician">Clinician</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Date & Time</label>
                <input
                  type="datetime-local"
                  value={observedAt}
                  onChange={(e) => setObservedAt(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-100 outline-none transition-colors"
                />
              </div>
            </div>

            {/* Entry Type */}
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Entry Type</label>
              <div className="grid grid-cols-3 gap-2">
                {(["general", "concern", "milestone"] as const).map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setEntryType(type)}
                    className={`py-2 text-xs font-semibold rounded-xl border capitalize transition-all ${
                      entryType === type
                        ? type === "concern"
                          ? "bg-red-500/10 border-red-500 text-red-400 shadow-md shadow-red-500/5"
                          : type === "milestone"
                          ? "bg-emerald-500/10 border-emerald-500 text-emerald-400 shadow-md shadow-emerald-500/5"
                          : "bg-indigo-500/10 border-indigo-500 text-indigo-400 shadow-md shadow-indigo-500/5"
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            {/* Developmental Domain */}
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Developmental Domain</label>
              <select
                value={domainId}
                onChange={(e) => setDomainId(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors"
              >
                {DOMAINS.map((domain) => (
                  <option key={domain.id} value={domain.id}>
                    {domain.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Milestone Dropdown (Conditional) */}
            {entryType === "milestone" && (
              <div className="animate-fadeIn">
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Linked Milestone</label>
                <select
                  value={milestoneId}
                  onChange={(e) => setMilestoneId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-slate-100 outline-none transition-colors"
                >
                  {milestones.filter((m) => m.domain_id === domainId).length === 0 ? (
                    <option value="">No milestones configured for this domain</option>
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

            {/* Body */}
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Observation Details</label>
              <textarea
                placeholder={`Describe what ${activeChild.first_name} did. e.g. "Used index finger to point at a bird, then turned to make eye contact with me."`}
                rows={4}
                value={body}
                onChange={(e) => setBody(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-sm text-slate-100 outline-none transition-colors resize-none"
              ></textarea>
              
              {/* Analyze with AI Button */}
              <div className="mt-2.5 flex justify-between items-center">
                <span className="text-[10px] text-slate-500">Min 10 characters</span>
                <button
                  type="button"
                  disabled={body.trim().length < 10 || loadingSuggestions}
                  onClick={handleAnalyzeWithAI}
                  className="px-4 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 hover:brightness-110 text-white font-bold text-xs rounded-xl shadow disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center gap-1.5"
                >
                  {loadingSuggestions ? (
                    <>
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <span>✨</span> Analyze with OIE AI
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* AI Suggestions Results */}
            {suggestionError && (
              <div className="p-3 bg-red-950/20 border border-red-500/20 text-red-400 text-xs rounded-xl">
                {suggestionError}
              </div>
            )}

            {aiSuggestions && (
              <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-4 mt-3 space-y-4 animate-fadeIn">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <h3 className="text-xs font-bold text-violet-400 uppercase tracking-wider flex items-center gap-1">
                    <span>✨</span> OIE AI Suggestions
                  </h3>
                  <span className="text-[9px] bg-slate-850 px-2 py-0.5 rounded text-slate-400 border border-slate-800 font-mono">
                    {aiSuggestions.milestones.length} Found
                  </span>
                </div>

                {aiSuggestions.milestones.length === 0 ? (
                  <p className="text-xs text-slate-500 italic py-2 text-center">No matching milestones retrieved above threshold.</p>
                ) : (
                  <div className="space-y-3">
                    {aiSuggestions.milestones.map((m: any) => {
                      const isExpanded = !!expandedSuggestions[m.milestone_id];
                      const isSubmitted = !!feedbackSubmitted[m.milestone_id];
                      const showComment = !!showCommentBox[m.milestone_id];
                      const comment = feedbackComment[m.milestone_id] || "";

                      return (
                        <div key={m.milestone_id} className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-3 space-y-2 hover:border-slate-700/80 transition-all text-left">
                          <div className="flex items-start justify-between gap-2">
                            <div className="min-w-0 flex-1">
                              <span className="text-[8px] uppercase tracking-wider font-bold text-slate-400 bg-slate-850 px-1.5 py-0.5 rounded">
                                {m.domain_name}
                              </span>
                              <h4 className="text-xs font-semibold text-slate-200 mt-1.5 leading-snug">{m.title}</h4>
                            </div>
                            <span className="text-[8px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 font-bold whitespace-nowrap">
                              {Math.round(m.relevance_score * 100)}% match
                            </span>
                          </div>

                          {/* Expandable Why section */}
                          <div className="border-t border-slate-800/40 pt-2">
                            <button
                              type="button"
                              onClick={() => setExpandedSuggestions(prev => ({ ...prev, [m.milestone_id]: !isExpanded }))}
                              className="text-[9px] text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1"
                            >
                              {isExpanded ? "▼ Hide Explanation" : "▶ Why was this suggested?"}
                            </button>
                            {isExpanded && (
                              <div className="mt-1.5 bg-slate-950/60 p-2.5 rounded-lg border border-slate-850 space-y-1.5 text-[10px] text-slate-300 animate-slideDown leading-relaxed font-sans">
                                <p><strong className="text-slate-400 font-semibold">Age band relevance:</strong> {m.age_band_relevance}</p>
                                <p className="italic text-slate-200">"{m.explanation_text}"</p>
                              </div>
                            )}
                          </div>

                          {/* Suggestion Actions */}
                          <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/40">
                            <button
                              type="button"
                              onClick={() => handleLinkSuggestion(m)}
                              className="px-2.5 py-1 bg-indigo-600/20 hover:bg-indigo-600 text-indigo-400 hover:text-white font-bold text-[9px] rounded-lg border border-indigo-600/30 transition-all"
                            >
                              🔗 Link to Log
                            </button>

                            {/* 👍 / 👎 Ratings */}
                            {!isSubmitted ? (
                              <div className="flex items-center gap-1.5">
                                <span className="text-[9px] text-slate-500">Caregiver vote:</span>
                                <button
                                  type="button"
                                  title="Helpful"
                                  onClick={() => handleSubmitFeedback(m.milestone_id, "helpful")}
                                  className="text-xs hover:scale-110 active:scale-95 transition-transform"
                                >
                                  👍
                                </button>
                                <button
                                  type="button"
                                  title="Not Helpful"
                                  onClick={() => setShowCommentBox(prev => ({ ...prev, [m.milestone_id]: !showComment }))}
                                  className="text-xs hover:scale-110 active:scale-95 transition-transform"
                                >
                                  👎
                                </button>
                              </div>
                            ) : (
                              <span className="text-[9px] text-emerald-400 font-semibold">✓ Feedback saved</span>
                            )}
                          </div>

                          {/* Optional Comment for 👎 */}
                          {showComment && !isSubmitted && (
                            <div className="mt-2 space-y-1.5 border-t border-slate-800/40 pt-2 animate-slideDown">
                              <textarea
                                placeholder="Optional comments on why this suggestion was not helpful..."
                                rows={2}
                                value={comment}
                                onChange={(e) => setFeedbackComment(prev => ({ ...prev, [m.milestone_id]: e.target.value }))}
                                className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2 text-[10px] text-slate-200 outline-none resize-none"
                              ></textarea>
                              <div className="flex justify-end gap-1.5">
                                <button
                                  type="button"
                                  onClick={() => setShowCommentBox(prev => ({ ...prev, [m.milestone_id]: false }))}
                                  className="px-2 py-1 text-[9px] text-slate-400 hover:text-slate-200"
                                >
                                  Cancel
                                </button>
                                <button
                                  type="button"
                                  onClick={() => handleSubmitFeedback(m.milestone_id, "not_helpful", comment)}
                                  className="px-2.5 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 font-bold text-[9px] rounded-md border border-red-500/20"
                                >
                                  Submit Vote
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
                
                <div className="border-t border-slate-850 pt-2.5 text-[8px] text-slate-500 text-center uppercase tracking-wider font-semibold">
                  OIE suggestions are non-clinical and for tracking support only.
                </div>
              </div>
            )}


            {/* Location */}
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Location / Context (Optional)</label>
              <input
                type="text"
                placeholder="e.g. Living room, Grandma's house, Grocery store"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-sm text-slate-100 outline-none transition-colors"
              />
            </div>

            {/* Regression Toggle */}
            <div className="flex items-center gap-3 pt-2">
              <input
                type="checkbox"
                id="regression"
                checked={isRegression}
                onChange={(e) => setIsRegression(e.target.checked)}
                className="h-4 w-4 bg-slate-950 border-slate-800 rounded focus:ring-indigo-500 accent-indigo-500 cursor-pointer"
              />
              <label htmlFor="regression" className="text-xs font-semibold text-slate-300 cursor-pointer select-none">
                Is this a regression of a previously achieved skill?
              </label>
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="w-full py-3 bg-gradient-to-r from-indigo-500 to-violet-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-500/25 hover:brightness-110 active:scale-[0.98] transition-all mt-4"
            >
              Add to Report Evidence
            </button>
          </form>
        </div>
      </div>

      {/* Logs Feed Column */}
      <div className="lg:col-span-2 space-y-6">
        {/* Filter Bar */}
        <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-2xl space-y-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-slate-100">Evidence Logs</h2>
              <p className="text-xs text-slate-400 mt-1">Longitudinal observation tracker for {activeChild.first_name}.</p>
            </div>
            
            {/* Simple Search Input */}
            <div className="w-full sm:w-64">
              <input
                type="text"
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-xs text-slate-100 outline-none transition-colors"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-slate-800/60">
            {/* Domain Filter */}
            <div>
              <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Domain</label>
              <select
                value={filterDomain}
                onChange={(e) => setFilterDomain(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 outline-none"
              >
                <option value="">All Domains</option>
                {DOMAINS.map((d) => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>

            {/* Type Filter */}
            <div>
              <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Type</label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 outline-none"
              >
                <option value="">All Types</option>
                <option value="general">📋 General</option>
                <option value="concern">⚠️ Concern</option>
                <option value="milestone">📊 Milestone</option>
              </select>
            </div>

            {/* Date Start Filter */}
            <div>
              <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Start Date</label>
              <input
                type="date"
                value={filterStart}
                onChange={(e) => setFilterStart(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 outline-none"
              />
            </div>

            {/* Date End Filter */}
            <div>
              <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">End Date</label>
              <input
                type="date"
                value={filterEnd}
                onChange={(e) => setFilterEnd(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 outline-none"
              />
            </div>
          </div>
          
          {(filterDomain || filterType || filterStart || filterEnd || searchQuery) && (
            <div className="flex justify-end pt-1">
              <button
                type="button"
                onClick={() => {
                  setFilterDomain("");
                  setFilterType("");
                  setFilterStart("");
                  setFilterEnd("");
                  setSearchQuery("");
                }}
                className="text-[10px] text-indigo-400 hover:text-indigo-300 font-semibold"
              >
                Reset Filters
              </button>
            </div>
          )}
        </div>

        {/* Timeline Feed */}
        {loadingObs ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-700"></div>
          </div>
        ) : Object.keys(groupedObs).length === 0 ? (
          <div className="bg-slate-900/20 border border-slate-800/80 rounded-2xl py-12 px-4 text-center">
            <p className="text-slate-400 text-sm">No observations match your query.</p>
            <p className="text-slate-500 text-xs mt-1">Try resetting the filters or logging a new observation.</p>
          </div>
        ) : (
          <div className="space-y-8 relative before:absolute before:top-2 before:bottom-2 before:left-[17px] before:w-[2px] before:bg-slate-850">
            {Object.entries(groupedObs).map(([monthYear, items]) => (
              <div key={monthYear} className="space-y-4">
                {/* Month/Year Group Header */}
                <div className="flex items-center gap-4 relative z-10">
                  <div className="h-9 w-9 rounded-full bg-slate-950 border border-slate-850 flex items-center justify-center shadow-lg">
                    <div className="h-2 w-2 rounded-full bg-indigo-500"></div>
                  </div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 bg-slate-950 px-3 py-1 rounded-md border border-slate-850/60 shadow">
                    {monthYear}
                  </h3>
                </div>

                {/* Group Items */}
                <div className="pl-12 space-y-4">
                  {items.map((obs) => {
                    const isEditing = editingObs?.id === obs.id;
                    const isDeleting = deleteConfirmId === obs.id;

                    const obsDate = new Date(obs.observed_at);
                    const formattedDate = obsDate.toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    });

                    const domainName = DOMAINS.find((d) => d.id === obs.domain_id)?.name || "General";

                    // Type-based styles
                    let borderClass = "border-slate-800";
                    let bgClass = "bg-slate-900/30";
                    let accentClass = "bg-slate-500";
                    let badgeClass = "text-slate-400 bg-slate-800/60 border-slate-700";

                    if (obs.entry_type === "concern") {
                      borderClass = "border-red-500/20";
                      bgClass = "bg-red-950/5";
                      accentClass = "bg-red-500";
                      badgeClass = "text-red-400 bg-red-500/10 border-red-500/25";
                    } else if (obs.entry_type === "milestone") {
                      borderClass = "border-emerald-500/20";
                      bgClass = "bg-emerald-950/5";
                      accentClass = "bg-emerald-500";
                      badgeClass = "text-emerald-400 bg-emerald-500/10 border-emerald-500/25";
                    }

                    return (
                      <div
                        key={obs.id}
                        className={`p-5 rounded-2xl border ${borderClass} ${bgClass} space-y-3 relative overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-indigo-500/[0.02]`}
                      >
                        <div className={`absolute top-0 left-0 w-[3px] h-full ${accentClass}`}></div>

                        {/* NORMAL / EDIT / DELETE VIEWS */}
                        {isEditing ? (
                          /* EDIT FORM */
                          <form onSubmit={handleUpdate} className="space-y-4">
                            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                              <span className="text-xs font-semibold text-slate-400">Editing Log Entry</span>
                              <div className="flex items-center gap-2">
                                <button
                                  type="button"
                                  onClick={() => setEditingObs(null)}
                                  className="text-xs text-slate-400 hover:text-slate-200 px-2.5 py-1 rounded"
                                >
                                  Cancel
                                </button>
                                <button
                                  type="submit"
                                  className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-3 py-1.5 rounded-lg"
                                >
                                  Save Changes
                                </button>
                              </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Relation</label>
                                <select
                                  value={editObserverRelation}
                                  onChange={(e) => setEditObserverRelation(e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 outline-none"
                                >
                                  <option value="Mother">Mother</option>
                                  <option value="Father">Father</option>
                                  <option value="Caregiver">Caregiver</option>
                                  <option value="Teacher">Teacher</option>
                                  <option value="Clinician">Clinician</option>
                                  <option value="Other">Other</option>
                                </select>
                              </div>
                              <div>
                                <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Date & Time</label>
                                <input
                                  type="datetime-local"
                                  value={editObservedAt}
                                  onChange={(e) => setEditObservedAt(e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 outline-none"
                                />
                              </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Type</label>
                                <select
                                  value={editEntryType}
                                  onChange={(e) => setEditEntryType(e.target.value as any)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 outline-none"
                                >
                                  <option value="general">📋 General</option>
                                  <option value="concern">⚠️ Concern</option>
                                  <option value="milestone">📊 Milestone</option>
                                </select>
                              </div>
                              <div>
                                <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Domain</label>
                                <select
                                  value={editDomainId}
                                  onChange={(e) => setEditDomainId(Number(e.target.value))}
                                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 outline-none"
                                >
                                  {DOMAINS.map((domain) => (
                                    <option key={domain.id} value={domain.id}>{domain.name}</option>
                                  ))}
                                </select>
                              </div>
                            </div>

                            {editEntryType === "milestone" && (
                              <div>
                                <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Linked Milestone</label>
                                <select
                                  value={editMilestoneId}
                                  onChange={(e) => setEditMilestoneId(e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 outline-none"
                                >
                                  {milestones.filter((m) => m.domain_id === editDomainId).length === 0 ? (
                                    <option value="">No milestones configured for this domain</option>
                                  ) : (
                                    milestones
                                      .filter((m) => m.domain_id === editDomainId)
                                      .map((m) => (
                                        <option key={m.id} value={m.id}>{m.title}</option>
                                      ))
                                  )}
                                </select>
                              </div>
                            )}

                            <div>
                              <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Details</label>
                              <textarea
                                value={editBody}
                                onChange={(e) => setEditBody(e.target.value)}
                                rows={3}
                                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 outline-none resize-none"
                              ></textarea>
                            </div>

                            <div className="grid grid-cols-2 gap-4 items-center">
                              <div>
                                <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Location</label>
                                <input
                                  type="text"
                                  value={editLocation}
                                  onChange={(e) => setEditLocation(e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 outline-none"
                                />
                              </div>
                              <div className="flex items-center gap-2 pt-4">
                                <input
                                  type="checkbox"
                                  id={`edit-regression-${obs.id}`}
                                  checked={editIsRegression}
                                  onChange={(e) => setEditIsRegression(e.target.checked)}
                                  className="h-3.5 w-3.5 bg-slate-950 border-slate-800 rounded focus:ring-indigo-500 accent-indigo-500"
                                />
                                <label htmlFor={`edit-regression-${obs.id}`} className="text-xs text-slate-300 select-none cursor-pointer">
                                  Regression?
                                </label>
                              </div>
                            </div>
                          </form>
                        ) : isDeleting ? (
                          /* CONFIRM DELETE */
                          <div className="space-y-4 py-1">
                            <div className="flex items-start gap-3">
                              <div className="p-2 rounded bg-red-500/10 text-red-400 mt-0.5">
                                ⚠️
                              </div>
                              <div>
                                <h4 className="text-sm font-bold text-slate-100">Soft-Delete Observation?</h4>
                                <p className="text-xs text-slate-400 mt-1">
                                  This observation will be hidden from reports and dashboards. You can recover or trace historic reports that used this log later.
                                </p>
                              </div>
                            </div>
                            <div className="flex justify-end gap-2 pt-2">
                              <button
                                type="button"
                                onClick={() => setDeleteConfirmId(null)}
                                className="px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 font-semibold"
                              >
                                Cancel
                              </button>
                              <button
                                type="button"
                                onClick={() => handleDelete(obs.id)}
                                className="px-4 py-1.5 text-xs bg-red-600 hover:bg-red-500 text-white font-semibold rounded-lg"
                              >
                                Confirm Delete
                              </button>
                            </div>
                          </div>
                        ) : (
                          /* STANDARD DISPLAY CARD */
                          <>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className={`text-[9px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full border ${badgeClass}`}>
                                  {obs.entry_type}
                                </span>
                                {obs.is_regression && (
                                  <span className="text-[9px] font-bold tracking-wider text-orange-400 uppercase bg-orange-500/10 px-2 py-0.5 rounded-full border border-orange-500/25 flex items-center gap-1">
                                    <span>⚠️</span> Regression
                                  </span>
                                )}
                              </div>
                              <span className="text-[10px] text-slate-500">{formattedDate}</span>
                            </div>

                            <p className="text-sm text-slate-200 leading-relaxed font-mono whitespace-pre-wrap">
                              "{obs.body}"
                            </p>

                            <div className="flex flex-wrap gap-2 text-[10px] text-slate-400">
                              <span className="bg-slate-850/60 px-2.5 py-1 rounded-md border border-slate-800/40">
                                Domain: {domainName}
                              </span>
                              {obs.observer_relation && (
                                <span className="bg-slate-850/60 px-2.5 py-1 rounded-md border border-slate-800/40">
                                  Observer: {obs.observer_relation}
                                </span>
                              )}
                              {obs.location && (
                                <span className="bg-slate-850/60 px-2.5 py-1 rounded-md border border-slate-800/40">
                                  Context: {obs.location}
                                </span>
                              )}
                              {obs.entry_type === "milestone" && obs.milestone_id && (
                                <span className="bg-emerald-950/20 text-emerald-400 border border-emerald-500/15 px-2.5 py-1 rounded-md">
                                  Milestone: {milestones.find((m) => m.id === obs.milestone_id)?.title || "Linked milestone"}
                                </span>
                              )}
                            </div>

                            {/* Card Footer Actions */}
                            <div className="flex justify-end gap-3 pt-3 border-t border-slate-800/50 mt-2">
                              <button
                                type="button"
                                onClick={() => startEdit(obs)}
                                className="text-[10px] text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1 transition-colors"
                              >
                                ✏️ Edit
                              </button>
                              <button
                                type="button"
                                onClick={() => setDeleteConfirmId(obs.id)}
                                className="text-[10px] text-red-400 hover:text-red-350 font-semibold flex items-center gap-1 transition-colors"
                              >
                                🗑️ Delete
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      {/* Safety Notice Disclaimer */}
      <div className="lg:col-span-3 mt-8">
        <ResponsibleAINotice />
      </div>
    </div>
  );
}

