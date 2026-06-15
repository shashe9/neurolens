"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useActiveChild } from "@/components/ActiveChildContext";
import { 
  Calendar, 
  ArrowRight,
  ShieldAlert,
  ClipboardList,
  Sparkles,
  TrendingUp,
  HelpCircle
} from "lucide-react";

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

interface VisitPrepData {
  things_worth_discussing: string[];
  recent_positive_changes: string[];
  suggested_topics: string[];
}

export default function VisitPrep() {
  const { activeChild, loading: contextLoading, fetchWithAuth } = useActiveChild();

  const [visits, setVisits] = useState<Visit[]>([]);
  const [clusters, setClusters] = useState<any[]>([]);
  const [selectedPoints, setSelectedPoints] = useState<string[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [loadingPrep, setLoadingPrep] = useState(true);
  const [prepData, setPrepData] = useState<VisitPrepData | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Form fields
  const [visitDate, setVisitDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().split("T")[0];
  });
  const [clinicianName, setClinicianName] = useState("");
  const [visitPriority, setVisitPriority] = useState<"routine" | "consultation" | "urgent">("consultation");
  const [concernLevel, setConcernLevel] = useState<"low" | "medium" | "high">("medium");
  const [concernNote, setConcernNote] = useState("");
  const [doctors, setDoctors] = useState<any[]>([]);
  const [selectedDoctorId, setSelectedDoctorId] = useState<string>("");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const togglePoint = (label: string) => {
    setSelectedPoints(prev => {
      const next = prev.includes(label) ? prev.filter(l => l !== label) : [...prev, label];
      const baseNote = concernNote.split("\n\n--- Suggested Talking Points ---\n")[0];
      if (next.length > 0) {
        setConcernNote(baseNote + "\n\n--- Suggested Talking Points ---\n" + next.map(p => `• ${p}`).join("\n"));
      } else {
        setConcernNote(baseNote);
      }
      return next;
    });
  };

  const loadPageData = useCallback(async () => {
    if (!activeChild) return;
    setLoadingData(true);
    setLoadingPrep(true);
    try {
      // 1. Fetch visits list
      const visitsRes = await fetchWithAuth(`${apiUrl}/visits/children/${activeChild.id}`);
      const visitsData = visitsRes.ok ? await visitsRes.json() : [];
      setVisits(visitsData);

      // Fetch doctors registry
      const docRes = await fetchWithAuth(`${apiUrl}/doctors`);
      const docData = docRes.ok ? await docRes.json() : [];
      setDoctors(docData);

      // 2. Fetch timeline clusters (to choose pediatric topics checklist)
      const timelineRes = await fetchWithAuth(`${apiUrl}/timeline/${activeChild.id}`);
      const timelineData = timelineRes.ok ? await timelineRes.json() : null;
      setClusters(timelineData ? timelineData.clusters : []);

      // 3. Fetch automated visit prep highlights
      const prepRes = await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/visit-prep`);
      if (prepRes.ok) {
        const prepJson = await prepRes.json();
        setPrepData(prepJson);
      } else {
        setPrepData(null);
      }
    } catch (err) {
      console.error("Error loading visit data:", err);
    } finally {
      setLoadingData(false);
      setLoadingPrep(false);
    }
  }, [activeChild, apiUrl, fetchWithAuth]);

  useEffect(() => {
    loadPageData();
  }, [loadPageData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeChild) return;

    if (!clinicianName.trim() || !concernNote.trim()) {
      alert("Please enter a pediatrician name and fill out what you'd like to share.");
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
        doctor_id: selectedDoctorId && selectedDoctorId !== "custom" ? selectedDoctorId : null
      };

      const res = await fetchWithAuth(`${apiUrl}/visits`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to save visit preparation.");
      }

      setSubmitSuccess(true);
      setClinicianName("");
      setConcernNote("");
      setSelectedPoints([]);
      
      setTimeout(() => setSubmitSuccess(false), 5000);
      loadPageData();
    } catch (err: any) {
      alert(err.message || "Failed to save visit preparation details.");
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
      <div className="bg-white border border-slate-200 p-8 rounded-2xl text-center max-w-lg mx-auto mt-12 space-y-4 shadow-sm">
        <h2 className="text-2xl font-semibold text-slate-800">No Child Profile Selected</h2>
        <p className="text-base text-slate-700">Please make sure you have selected a child profile.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-6 space-y-10">
      
      {/* Title */}
      <div className="text-left space-y-2">
        <h1 className="text-4xl font-bold text-slate-100 leading-tight">Visit Prep</h1>
        <p className="text-lg text-slate-300">
          Organize observations and draft notes to share with your pediatrician.
        </p>
      </div>

      {/* Automated Highlights Summary at the Top */}
      {!loadingPrep && prepData && (
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-sm space-y-6 text-left">
          <div>
            <h2 className="text-2xl font-semibold text-slate-100 flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-indigo-400" />
              Pediatrician Discussion Guide
            </h2>
            <p className="text-base text-slate-300 mt-1">
              Automated intelligence compiled from {activeChild.first_name}'s journal entries.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Recurring Concerns */}
            <div className="p-5 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
              <div className="flex items-center gap-2 text-indigo-400 font-semibold text-base">
                <ShieldAlert className="h-5 w-5 shrink-0" />
                <span>Things You've Mentioned More Than Once</span>
              </div>
              <ul className="space-y-2 text-base text-slate-200 font-medium">
                {prepData.things_worth_discussing.map((item, idx) => (
                  <li key={idx} className="list-disc ml-4 leading-relaxed">
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Progress Deltas */}
            <div className="p-5 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
              <div className="flex items-center gap-2 text-indigo-400 font-semibold text-base">
                <TrendingUp className="h-5 w-5 shrink-0" />
                <span>Positive Changes You've Noticed</span>
              </div>
              <ul className="space-y-2 text-base text-slate-200 font-medium">
                {prepData.recent_positive_changes.map((item, idx) => (
                  <li key={idx} className="list-disc ml-4 leading-relaxed">
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Suggested Doctor Questions */}
            <div className="p-5 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
              <div className="flex items-center gap-2 text-indigo-400 font-semibold text-base">
                <HelpCircle className="h-5 w-5 shrink-0" />
                <span>Questions You May Want To Ask</span>
              </div>
              <ul className="space-y-2 text-base text-slate-200 font-medium">
                {prepData.suggested_topics.map((item, idx) => (
                  <li key={idx} className="list-disc ml-4 leading-relaxed">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Form + Saved Visits */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Configuration Column */}
        <div className="lg:col-span-2 space-y-8">
          {submitSuccess && (
            <div className="p-5 bg-emerald-50 border border-emerald-100 text-emerald-700 text-sm font-medium rounded-xl flex items-center gap-2 shadow-sm">
              <span>✓</span> Visit preparation details saved successfully!
            </div>
          )}

          <form className="bg-white border border-slate-200 p-8 rounded-2xl space-y-6 shadow-sm" onSubmit={handleSubmit}>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Visit Date */}
              <div className="space-y-1.5 text-left">
                <label className="block text-base font-semibold text-slate-700">Visit Date</label>
                <input
                  type="date"
                  value={visitDate}
                  onChange={(e) => setVisitDate(e.target.value)}
                  className="w-full bg-white border border-slate-200 focus:border-indigo-500 rounded-xl px-4 py-3 text-base text-slate-800 outline-none"
                />
              </div>

              {/* Pediatrician / Specialist Select Dropdown */}
              <div className="space-y-1.5 text-left">
                <label className="block text-base font-semibold text-slate-700">Pediatrician / Specialist</label>
                <select
                  value={selectedDoctorId}
                  onChange={(e) => {
                    const val = e.target.value;
                    setSelectedDoctorId(val);
                    if (val && val !== "custom") {
                      const docObj = doctors.find(d => d.id === val);
                      if (docObj) setClinicianName(docObj.name);
                    } else if (val === "") {
                      setClinicianName("");
                    }
                  }}
                  className="w-full bg-white border border-slate-200 focus:border-indigo-500 rounded-xl px-4 py-3 text-base text-slate-800 outline-none"
                >
                  <option value="">-- Select Registered Provider --</option>
                  {doctors.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.name} ({doc.specialization || "Pediatrician"})
                    </option>
                  ))}
                  <option value="custom">-- Custom Clinician Name --</option>
                </select>
              </div>

              {/* Custom clinician input (conditional or fallback) */}
              {(selectedDoctorId === "custom" || selectedDoctorId === "") && (
                <div className="space-y-1.5 text-left">
                  <label className="block text-base font-semibold text-slate-700">Custom Provider Name</label>
                  <input
                    type="text"
                    placeholder="e.g. Dr. Evelyn Marcus"
                    value={clinicianName}
                    onChange={(e) => setClinicianName(e.target.value)}
                    className="w-full bg-white border border-slate-200 focus:border-indigo-500 rounded-xl px-4 py-3 text-base text-slate-800 outline-none"
                  />
                </div>
              )}
            </div>

            {/* What would you like to discuss? */}
            <div className="space-y-1.5 text-left">
              <label className="block text-base font-semibold text-slate-300">What is the focus of this visit?</label>
              <select
                value={visitPriority}
                onChange={(e) => setVisitPriority(e.target.value as any)}
                className="w-full bg-white border border-slate-200 focus:border-indigo-500 rounded-xl px-4 py-3 text-base text-slate-100 outline-none"
              >
                <option value="routine">Routine developmental checkup</option>
                <option value="consultation">Specific question or developmental milestone review</option>
                <option value="urgent">Urgent follow-up and review</option>
              </select>
            </div>

            {/* What has been on your mind recently? */}
            <div className="space-y-1.5 text-left">
              <label className="block text-base font-semibold text-slate-300">What has been on your mind recently?</label>
              <select
                value={concernLevel}
                onChange={(e) => setConcernLevel(e.target.value as any)}
                className="w-full bg-white border border-slate-200 focus:border-indigo-500 rounded-xl px-4 py-3 text-base text-slate-100 outline-none"
              >
                <option value="low">Just checking in (Comfortable / Low concern)</option>
                <option value="medium">Some questions to run by the doctor (Medium concern)</option>
                <option value="high">Specific behaviors I want evaluated (High concern)</option>
              </select>
            </div>

            {/* Anything you'd like the doctor to know? */}
            <div className="space-y-1.5 text-left">
              <label className="block text-base font-semibold text-slate-300">Describe what you want to share with the doctor</label>
              <textarea
                placeholder="State any observations, daily moments, or patterns you want to share during the visit."
                rows={5}
                value={concernNote}
                onChange={(e) => setConcernNote(e.target.value)}
                className="w-full bg-white border border-slate-200 focus:border-indigo-500 rounded-xl p-4 text-base text-slate-100 outline-none resize-none leading-relaxed"
              ></textarea>
            </div>

            {/* Suggested Talking Points Checklist */}
            {clusters.length > 0 && (
              <div className="space-y-4 pt-2 border-t border-slate-100 text-left">
                <label className="block text-base font-semibold text-slate-100">
                  Select Recurring Patterns to Append
                </label>
                <p className="text-base text-slate-700 leading-relaxed">
                  We identified these recurring patterns in your journal logs. Check the ones you'd like to ask the doctor about:
                </p>
                
                <div className="grid grid-cols-1 gap-3">
                  {clusters.map((c) => {
                    const isChecked = selectedPoints.includes(c.label);
                    return (
                      <div
                        key={c.cluster_id}
                        onClick={() => togglePoint(c.label)}
                        className={`p-5 rounded-xl border transition-all cursor-pointer flex items-center justify-between gap-4 ${
                          isChecked
                            ? "bg-indigo-50/30 border-indigo-200"
                            : "bg-slate-50 border-slate-200 hover:border-slate-300"
                        }`}
                      >
                        <div className="space-y-1 text-left">
                          <span className="text-sm uppercase tracking-wide font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-100">
                            {c.domain_name === "Gross Motor" ? "Movement" :
                             c.domain_name === "Fine Motor" ? "Hands & Fingers" :
                             c.domain_name === "Social Emotional" ? "Feelings & Friendships" :
                             c.domain_name === "Cognitive" ? "Thinking & Learning" : c.domain_name}
                          </span>
                          <p className="text-base font-semibold text-slate-800 mt-2">{c.label}</p>
                          <p className="text-sm text-slate-700">From {c.observations.length} supporting journal entries</p>
                        </div>
                        
                        <div className="flex items-center justify-center select-none shrink-0">
                          {isChecked ? (
                            <span className="h-6 w-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-sm font-bold shadow-sm">
                              ✓
                            </span>
                          ) : (
                            <span className="h-6 w-6 rounded-full border border-slate-300 bg-white" />
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              className="w-full py-4 bg-indigo-650 hover:bg-indigo-755 text-white font-semibold text-base rounded-xl transition-all shadow-sm"
            >
              Save Visit Prep Details
            </button>
          </form>
        </div>

        {/* Overview Column */}
        <div className="lg:col-span-1 space-y-8">
          
          {/* Saved Visit Configs */}
          <div className="space-y-4 text-left">
            <h3 className="text-lg font-semibold text-slate-150">Saved Visits</h3>
            {loadingData ? (
              <p className="text-base text-slate-300 italic">Loading visit archives...</p>
            ) : visits.length === 0 ? (
              <div className="p-6 bg-white border border-slate-200 rounded-2xl text-center text-base text-slate-700 shadow-sm">
                No upcoming visits set up yet.
              </div>
            ) : (
              <div className="space-y-4">
                {visits.map((v) => {
                  let priorityText = "Routine check-in";
                  let concernText = "Low Concern";
                  let badgeColor = "bg-slate-100 text-slate-650 border-slate-200";

                  if (v.visit_priority === "consultation") priorityText = "Milestone Review";
                  if (v.visit_priority === "urgent") priorityText = "Urgent Review";

                  if (v.concern_level === "medium") {
                    concernText = "Some Questions";
                    badgeColor = "bg-indigo-50 text-indigo-700 border-indigo-100";
                  } else if (v.concern_level === "high") {
                    concernText = "Specific Concerns";
                    badgeColor = "bg-rose-50 text-rose-700 border-rose-100";
                  }

                  return (
                    <div key={v.id} className="p-6 bg-white border border-slate-200 rounded-2xl space-y-3 text-sm shadow-sm">
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <span className="font-semibold text-slate-50 text-base">{v.clinician_name}</span>
                        <span className="text-sm text-slate-300 font-medium">{new Date(v.visit_date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs uppercase font-bold tracking-wide px-2.5 py-0.5 rounded-md bg-slate-100 text-slate-300 border border-slate-200">
                          {priorityText}
                        </span>
                        <span className={`text-xs uppercase font-bold tracking-wide px-2.5 py-0.5 rounded-md border ${badgeColor}`}>
                          {concernText}
                        </span>
                      </div>
                      <p className="text-slate-200 italic line-clamp-3 leading-relaxed mt-2 text-base">"{v.concern_note}"</p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
