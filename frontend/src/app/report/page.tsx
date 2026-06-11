"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useActiveChild } from "@/components/ActiveChildContext";

interface Visit {
  id: string;
  clinician_name: string;
  visit_date: string;
  visit_priority: string;
}

interface SourceObservation {
  id: string;
  contribution: string;
}

interface ReportSection {
  section_key: string;
  title: string;
  observation_count: number;
  period_start: string | null;
  period_end: string | null;
  source_observations: SourceObservation[];
}

interface EvidenceLog {
  id: string;
  entry_type: "general" | "concern" | "milestone";
  body: string;
  domain: string | null;
  milestone: string | null;
  observed_at: string;
  context_note: string | null;
  location: string | null;
  observer_relation: string | null;
  is_regression: boolean;
}

interface MilestoneEvidence {
  title: string;
  organization: string;
  year: number;
}

interface MilestoneStatusData {
  id: string;
  domain: string;
  title: string;
  description: string;
  age_range: string;
  status: string;
  observed_date: string | null;
  notes: string | null;
  sources: MilestoneEvidence[];
}

interface ReportPayload {
  metadata: {
    platform: string;
    generated_at: string;
    version: string;
  };
  child: {
    id: string;
    first_name: string;
    last_name: string;
    date_of_birth: string;
    gender: string;
    chronological_age: string;
  };
  parents: Array<{
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    relationship: string;
  }>;
  visit_context: {
    id?: string;
    date?: string;
    clinician?: string;
    priority?: string;
    concern_level?: string;
    primary_concern_note?: string;
  };
  report_sections: ReportSection[];
  evidence: EvidenceLog[];
  milestones: MilestoneStatusData[];
}

export default function ReportPreview() {
  const { activeChild, loading: contextLoading } = useActiveChild();

  const [visits, setVisits] = useState<Visit[]>([]);
  const [selectedVisitId, setSelectedVisitId] = useState<string>("");
  const [reportData, setReportData] = useState<ReportPayload | null>(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [expandedSections, setExpandedSections] = useState<{ [key: string]: boolean }>({});

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Fetch child's visit contexts to populate selector
  useEffect(() => {
    const fetchVisits = async () => {
      if (!activeChild) return;
      try {
        const res = await fetch(`${apiUrl}/visits/children/${activeChild.id}`);
        if (res.ok) {
          const data: Visit[] = await res.json();
          setVisits(data);
          if (data.length > 0) {
            setSelectedVisitId(data[0].id); // select latest by default
          }
        }
      } catch (err) {
        console.error("Error loading visits for report:", err);
      }
    };
    fetchVisits();
  }, [activeChild, apiUrl]);

  const handleAssemble = async () => {
    if (!activeChild) return;
    setLoadingReport(true);
    setReportData(null);
    try {
      const payload = {
        child_id: activeChild.id,
        visit_id: selectedVisitId || null,
      };

      const res = await fetch(`${apiUrl}/reports`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to assemble report snapshot.");
      }

      const reportResponse = await res.json();
      setReportData(reportResponse.report_json);
      // Auto-expand all sections for clarity
      setExpandedSections({
        primary_concerns: true,
        milestone_evidence: true,
        general_logs: true,
      });
    } catch (err: any) {
      alert(err.message || "Failed to assemble report.");
    } finally {
      setLoadingReport(false);
    }
  };

  const toggleSection = (key: string) => {
    setExpandedSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  // Helper: Find evidence log by ID
  const findEvidenceLog = (obsId: string) => {
    return reportData?.evidence.find((e) => e.id === obsId);
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
    <div className="space-y-8">
      {/* Header Panel */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
            Clinician Report Snapshot
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Assemble, review, and print the frozen qualitative data snapshot compiled for the clinician.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Visit Selector Dropdown */}
          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-400 whitespace-nowrap">Visit context:</label>
            <select
              value={selectedVisitId}
              onChange={(e) => setSelectedVisitId(e.target.value)}
              className="bg-slate-900 border border-slate-800 text-xs text-slate-200 rounded-xl px-3 py-2 outline-none focus:border-indigo-500"
            >
              <option value="">Latest Visit Context (Default)</option>
              {visits.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.clinician_name} ({new Date(v.visit_date).toLocaleDateString()})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleAssemble}
            disabled={loadingReport}
            className="px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-violet-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-500/20 hover:brightness-110 active:scale-95 disabled:opacity-50 transition-all"
          >
            {loadingReport ? "Assembling..." : "📄 Compile Report Snapshot"}
          </button>
          
          {reportData && (
            <button
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl border border-slate-700 transition-colors"
              onClick={() => window.print()}
            >
              🖨️ Print / Save PDF
            </button>
          )}
        </div>
      </div>

      {!reportData ? (
        /* Empty / CTA State */
        <div className="bg-slate-900/30 border border-slate-800/80 p-12 rounded-2xl text-center max-w-xl mx-auto space-y-4">
          <span className="text-4xl select-none block">📁</span>
          <h2 className="text-lg font-bold text-slate-200">Generate Audit-Ready Clinician Report</h2>
          <p className="text-xs text-slate-400 leading-relaxed max-w-md mx-auto">
            This action generates an immutable snapshot of all logged parent observations, active milestone matrices, and clinical visit priorities. The report guarantees traceability and clinical audit trails.
          </p>
          <button
            onClick={handleAssemble}
            className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-violet-500 text-white text-sm font-semibold rounded-xl hover:brightness-105 transition-all mt-2"
          >
            Compile Report Now
          </button>
        </div>
      ) : (
        /* Document Preview Layout Grid */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Columns - Document Preview */}
          <div className="lg:col-span-2 bg-white text-slate-900 rounded-2xl p-8 shadow-2xl border border-slate-200 print:p-0 print:border-none print:shadow-none space-y-8">
            
            {/* Document Header */}
            <div className="flex justify-between items-start border-b border-slate-200 pb-6">
              <div>
                <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">NEUROLENS</h2>
                <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mt-1">
                  Developmental Observation & Visit Prep Summary
                </p>
              </div>
              <div className="text-right text-xs text-slate-400 font-mono">
                <p>Generated: {new Date(reportData.metadata.generated_at).toLocaleString()}</p>
                <p>Format: JSON Snapshot v{reportData.metadata.version}</p>
              </div>
            </div>

            {/* Child & Parent Details */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 bg-slate-50 p-4 rounded-xl border border-slate-100">
              <div>
                <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Subject Demographics</h3>
                <p className="text-sm font-bold text-slate-800">
                  {reportData.child.first_name} {reportData.child.last_name}
                </p>
                <p className="text-xs text-slate-600 mt-1">
                  Age: {reportData.child.chronological_age} &bull; Gender: {reportData.child.gender}
                </p>
                <p className="text-xs text-slate-600">
                  DOB: {new Date(reportData.child.date_of_birth).toLocaleDateString()}
                </p>
              </div>
              <div>
                <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Historians / Reporters</h3>
                {reportData.parents.map((p) => (
                  <div key={p.id} className="text-xs text-slate-600 mb-1">
                    <p className="font-semibold text-slate-700">{p.first_name} {p.last_name}</p>
                    <p>Relation: {p.relationship} &bull; Email: {p.email}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Visit Context */}
            {reportData.visit_context && reportData.visit_context.date ? (
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-indigo-600 uppercase tracking-wider border-b border-slate-100 pb-1.5">
                  Visit Goals & Priority Context
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                  <div>
                    <p className="text-slate-400 font-semibold">Scheduled Clinician</p>
                    <p className="font-bold text-slate-800 mt-0.5">{reportData.visit_context.clinician}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 font-semibold">Priority Classification</p>
                    <p className="font-bold text-slate-800 mt-0.5 capitalize">{reportData.visit_context.priority}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 font-semibold">Parent Concern Level</p>
                    <p className="font-bold text-slate-800 mt-0.5 capitalize">
                      {reportData.visit_context.concern_level}
                    </p>
                  </div>
                </div>
                <div className="bg-indigo-50/50 p-4 rounded-xl border border-indigo-100/50 mt-2">
                  <p className="text-xs font-semibold text-slate-400 mb-1">Primary Concern Note</p>
                  <p className="text-xs text-slate-700 leading-relaxed font-sans">{reportData.visit_context.primary_concern_note}</p>
                </div>
              </div>
            ) : (
              <div className="bg-amber-50 p-4 rounded-xl border border-amber-100 text-xs text-amber-800">
                ⚠️ No clinical visit context was attached. Complete visit details inside the "Prepare Visit" section to add clinical priorities to this report.
              </div>
            )}

            {/* Evidence-First Traceable Report Sections */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-indigo-600 uppercase tracking-wider border-b border-slate-100 pb-1.5">
                Traceable Observation Evidence Segments
              </h3>
              
              <div className="space-y-4">
                {reportData.report_sections.map((sec) => {
                  const isExpanded = !!expandedSections[sec.section_key];
                  
                  return (
                    <div key={sec.section_key} className="border border-slate-150 rounded-xl overflow-hidden shadow-sm">
                      {/* Section Header */}
                      <button
                        type="button"
                        onClick={() => toggleSection(sec.section_key)}
                        className="w-full flex items-center justify-between p-4 bg-slate-50 border-b border-slate-150 hover:bg-slate-100/60 transition-colors text-left"
                      >
                        <div>
                          <h4 className="text-xs font-bold text-slate-800">{sec.title}</h4>
                          <div className="flex gap-3 text-[10px] text-slate-500 mt-1 font-mono">
                            <span>Observations: {sec.observation_count}</span>
                            {sec.period_start && (
                              <span>Active Period: {new Date(sec.period_start).toLocaleDateString()} - {new Date(sec.period_end!).toLocaleDateString()}</span>
                            )}
                          </div>
                        </div>
                        <span className="text-slate-400 text-sm">{isExpanded ? "▲" : "▼"}</span>
                      </button>

                      {/* Section Body - Show sources */}
                      {isExpanded && (
                        <div className="p-4 bg-white divide-y divide-slate-100 space-y-4">
                          {sec.observation_count === 0 ? (
                            <p className="text-xs text-slate-400 italic py-2">No observations logged in this category.</p>
                          ) : (
                            sec.source_observations.map((src, index) => {
                              const detail = findEvidenceLog(src.id);
                              if (!detail) return null;

                              return (
                                <div key={src.id} className={`text-xs ${index > 0 ? "pt-4" : ""}`}>
                                  <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                                    <span className="font-bold text-indigo-600 uppercase">
                                      Provenance ID: {src.id.slice(0, 8)}
                                    </span>
                                    <span>
                                      Observed by: {detail.observer_relation || "Parent"} &bull; {new Date(detail.observed_at).toLocaleString()}
                                    </span>
                                  </div>
                                  <p className="text-slate-800 leading-relaxed font-mono italic">
                                    "{detail.body}"
                                  </p>
                                  <div className="flex flex-wrap gap-2 mt-1.5 text-[9px] text-slate-400 font-mono">
                                    <span>Domain: {detail.domain || "N/A"}</span>
                                    {detail.location && <span>Location: {detail.location}</span>}
                                    {detail.is_regression && <span className="text-orange-500 font-bold">⚠️ Skill Regression</span>}
                                    {detail.milestone && <span className="text-emerald-600">Milestone verified: {detail.milestone}</span>}
                                  </div>
                                </div>
                              );
                            })
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Developmental Milestone Tracker Matrix */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-indigo-600 uppercase tracking-wider border-b border-slate-100 pb-1.5">
                Developmental Milestone Matrix
              </h3>
              <div className="border border-slate-100 rounded-xl overflow-hidden">
                <table className="w-full border-collapse text-left text-xs">
                  <thead>
                    <tr className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-100">
                      <th className="py-2.5 px-4">Domain</th>
                      <th className="py-2.5 px-4">Milestone Element</th>
                      <th className="py-2.5 px-4 text-center">Developmental Range</th>
                      <th className="py-2.5 px-4 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {reportData.milestones.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="py-4 px-4 text-slate-400 text-center italic">
                          No milestones have been tracked or marked. Review milestones inside the "Review Milestones" tab.
                        </td>
                      </tr>
                    ) : (
                      reportData.milestones.map((m) => (
                        <tr key={m.id} className="hover:bg-slate-50/50">
                          <td className="py-2.5 px-4 font-medium text-slate-700">{m.domain}</td>
                          <td className="py-2.5 px-4 text-slate-600">
                            <div>
                              <p className="font-semibold text-slate-800">{m.title}</p>
                              <p className="text-[10px] text-slate-400 mt-0.5">{m.description}</p>
                              {m.sources && m.sources.length > 0 && (
                                <p className="text-[9px] text-indigo-500/80 font-mono mt-1">
                                  Evidence reference: {m.sources.map((s) => `${s.organization} (${s.year})`).join(", ")}
                                </p>
                              )}
                            </div>
                          </td>
                          <td className="py-2.5 px-4 text-center text-slate-500 font-mono whitespace-nowrap">{m.age_range}</td>
                          <td className="py-2.5 px-4 text-right font-semibold">
                            <span
                              className={`px-1.5 py-0.5 rounded text-[10px] uppercase tracking-wider ${
                                m.status === "achieved"
                                  ? "bg-emerald-100 text-emerald-800"
                                  : m.status === "in_progress"
                                  ? "bg-yellow-100 text-yellow-850"
                                  : "bg-slate-100 text-slate-600"
                              }`}
                            >
                              {m.status.replace("_", " ")}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Right Column - Aggregate Root Raw JSON Inspector */}
          <div className="lg:col-span-1 space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-100">JSON snapshot</h2>
              <p className="text-xs text-slate-400 mt-1">This raw structure represents the exact aggregate root saved in the database.</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-4 backdrop-blur-sm sticky top-24">
              <div className="flex justify-between items-center pb-2 border-b border-slate-800">
                <span className="text-xs font-mono text-slate-400">report_json (JSONB)</span>
                <span className="text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/25 px-1.5 py-0.5 rounded font-mono">
                  Immutable
                </span>
              </div>
              <pre className="text-[10px] text-slate-300 font-mono bg-slate-950 p-4 rounded-xl border border-slate-900 overflow-x-auto max-h-[500px] leading-relaxed select-all">
                {JSON.stringify(reportData, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
