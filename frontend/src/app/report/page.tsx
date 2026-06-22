"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useActiveChild } from "@/components/ActiveChildContext";
import { ResponsibleAINotice } from "@/components/ResponsibleAINotice";
import { API_BASE_URL } from "@/config";
import { 
  Printer, 
  Sparkles,
  Award,
  Eye,
  MessageSquare,
  Info,
  BookOpen,
  FileText
} from "lucide-react";

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
  evidence_count: number;
  evidence_observation_ids: string[];
  first_evidence_date: string | null;
  last_evidence_date: string | null;
}

interface ParentSummary {
  narrative: string;
  key_achievements: string[];
  logged_moments_count: number;
  parent_effort?: {
    text: string;
    total_observations: number;
    completed_activities_count: number;
    attempted_activities_count: number;
    guides_read_count: number;
  };
  observation_blind_spots?: string[];
  growth_highlights?: string[];
  learning_opportunities?: string[];
  suggested_discussion_topics?: string[];
}

interface ClinicianBrief {
  demographics: {
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
  domain_summaries?: {
    [key: string]: {
      total_milestones: number;
      supported_milestones: number;
      total_evidence_observations: number;
    };
  };
  excerpts: EvidenceLog[];
  milestone_matrix: MilestoneStatusData[];
  clusters?: Array<{
    cluster_id: string;
    domain_name: string;
    label: string;
    observation_ids: string[];
    observations: Array<{
      id: string;
      body: string;
      structured_body: string | null;
      observed_at: string;
    }>;
  }>;
  persistent_concerns?: any[];
  visit_delta?: any;
  quality_data?: any;
}

interface ReportPayload {
  metadata: {
    platform: string;
    generated_at: string;
    version: string;
  };
  parent_summary?: ParentSummary;
  clinician_brief?: ClinicianBrief;
  child?: any;
  parents?: any;
  visit_context?: any;
  report_sections?: any;
  evidence?: any;
  milestones?: any;
  coverage_summary?: any;
}

export default function ReportPreview() {
  const { activeChild, loading: contextLoading, fetchWithAuth } = useActiveChild();

  const [visits, setVisits] = useState<Visit[]>([]);
  const [selectedVisitId, setSelectedVisitId] = useState<string>("");
  const [reportData, setReportData] = useState<ReportPayload | null>(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [devMode, setDevMode] = useState(false);
  const [reportTab, setReportTab] = useState<"clinician" | "parent">("clinician");

  const getBrief = useCallback(() => {
    if (!reportData) return null;
    if (reportData.clinician_brief) {
      return reportData.clinician_brief;
    }
    return {
      demographics: reportData.child,
      parents: reportData.parents,
      visit_context: reportData.visit_context,
      domain_summaries: reportData.coverage_summary,
      excerpts: reportData.evidence,
      milestone_matrix: reportData.milestones,
      clusters: []
    } as any as ClinicianBrief;
  }, [reportData]);

  const apiUrl = API_BASE_URL;

  useEffect(() => {
    const fetchVisits = async () => {
      if (!activeChild) return;
      try {
        const res = await fetchWithAuth(`${apiUrl}/visits/children/${activeChild.id}`);
        if (res.ok) {
          const data: Visit[] = await res.json();
          setVisits(data);
          if (data.length > 0) {
            setSelectedVisitId(data[0].id);
          }
        }
      } catch (err) {
        console.error("Error loading visits for report:", err);
      }
    };
    fetchVisits();
  }, [activeChild, apiUrl, fetchWithAuth]);

  const handleAssemble = async () => {
    if (!activeChild) return;
    setLoadingReport(true);
    setReportData(null);
    try {
      const payload = {
        child_id: activeChild.id,
        visit_id: selectedVisitId || null,
      };

      const res = await fetchWithAuth(`${apiUrl}/reports`, {
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
    } catch (err: any) {
      alert(err.message || "Failed to assemble report.");
    } finally {
      setLoadingReport(false);
    }
  };

  const brief = getBrief();

  const findEvidenceLog = (obsId: string) => {
    return brief?.excerpts?.find((e) => e.id === obsId);
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
      <div className="bg-white border border-slate-200 p-8 rounded-2xl text-center max-w-lg mx-auto mt-12 space-y-4 shadow-sm">
        <h2 className="text-2xl font-semibold text-slate-800">No Child Profile Selected</h2>
        <p className="text-base text-slate-500">Please make sure you have selected a child profile.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-6">
      
      {/* Header Panel */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-slate-200 pb-5">
        <div className="text-left space-y-2">
          <h1 className="text-4xl font-bold text-slate-900 leading-tight">
            Prepare Visit Summary
          </h1>
          <p className="text-lg text-slate-500">
            Compile your child's milestones progression and observations into SBAR clinician briefs and parent narratives.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          {/* Visit Context Selector */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-slate-500 whitespace-nowrap">Visit:</span>
            <select
              value={selectedVisitId}
              onChange={(e) => setSelectedVisitId(e.target.value)}
              className="bg-white border border-slate-200 text-sm text-slate-700 rounded-xl px-3 py-2 outline-none font-medium"
            >
              <option value="">Latest Visit (Default)</option>
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
            className="px-5 py-2.5 bg-indigo-650 text-white text-base font-semibold rounded-xl hover:bg-indigo-750 disabled:opacity-50 transition-all cursor-pointer shadow-sm"
          >
            {loadingReport ? "Assembling..." : "Compile Summary"}
          </button>
        </div>
      </div>

      {brief && reportData && (
        <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200 no-print">
          <div className="flex gap-1 bg-slate-100 p-1 border border-slate-200 rounded-xl">
            <button
              onClick={() => setReportTab("clinician")}
              className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
                reportTab === "clinician"
                  ? "bg-white text-indigo-600 shadow-sm"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              Clinician Brief (SBAR)
            </button>
            <button
              onClick={() => setReportTab("parent")}
              className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
                reportTab === "parent"
                  ? "bg-white text-indigo-600 shadow-sm"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              Parent Summary
            </button>
          </div>

          <div className="flex items-center gap-3">
            <button
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold rounded-xl transition-all flex items-center gap-1.5"
              onClick={() => window.print()}
            >
              <Printer className="h-4 w-4" />
              <span>Print / Save PDF</span>
            </button>
            
            <label className="flex items-center gap-2 cursor-pointer select-none text-sm font-semibold text-slate-500">
              <input
                type="checkbox"
                checked={devMode}
                onChange={(e) => setDevMode(e.target.checked)}
                className="rounded bg-white border-slate-300 text-indigo-600 accent-indigo-600 cursor-pointer h-4 w-4"
              />
              <span>Developer JSON</span>
            </label>
          </div>
        </div>
      )}

      {!brief || !reportData ? (
        /* Replaced Empty State with Premium Landing Experience */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 text-left">
          {/* Left Columns: Visual Previews of Reports */}
          <div className="lg:col-span-2 space-y-6 text-left">
            <h2 className="text-2xl font-bold text-slate-100 mb-2">Available Report Formats</h2>
            
            {/* 1. Parent Summary Preview Card */}
            <div className="bg-white border border-slate-800 p-6 rounded-2xl shadow-sm space-y-4 hover:border-indigo-200 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-indigo-50 border border-indigo-100 text-indigo-600 rounded-xl">
                    <BookOpen className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-100">Parent Summary</h3>
                    <p className="text-sm text-slate-350">Empathic narrative reflection & milestone progress</p>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-100">
                  Parent-First
                </span>
              </div>
              
              <div className="bg-slate-950 p-5 rounded-xl border border-slate-850 space-y-4">
                <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                  <span className="text-[10px] font-sans font-bold text-indigo-400 uppercase tracking-widest">Sample Preview (Demo Only)</span>
                  <span className="text-[10px] text-slate-500 font-semibold italic">Structure visualizer</span>
                </div>
                
                {/* Skeletons representing narrative paragraph */}
                <div className="space-y-2.5 py-1 animate-pulse">
                  <div className="h-3 bg-slate-800 rounded-md w-full"></div>
                  <div className="h-3 bg-slate-800 rounded-md w-11/12"></div>
                  <div className="h-3 bg-slate-800 rounded-md w-5/6"></div>
                  <div className="h-3 bg-slate-800 rounded-md w-4/5"></div>
                </div>

                <div className="flex gap-2 pt-2 border-t border-slate-900/60 font-sans">
                  <div className="h-6 bg-slate-900 border border-slate-800 rounded px-3 w-28 animate-pulse"></div>
                  <div className="h-6 bg-slate-900 border border-slate-800 rounded px-3 w-32 animate-pulse"></div>
                </div>
              </div>
            </div>

            {/* 2. Clinician Brief Preview Card */}
            <div className="bg-white border border-slate-800 p-6 rounded-2xl shadow-sm space-y-4 hover:border-indigo-200 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-indigo-50 border border-indigo-100 text-indigo-600 rounded-xl">
                    <FileText className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-100">Clinician Brief</h3>
                    <p className="text-sm text-slate-350">Pediatric SBAR summary & CDC checklist matrix</p>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-100">
                  SBAR Format
                </span>
              </div>
              
              <div className="bg-slate-950 p-5 rounded-xl border border-slate-850 space-y-4 text-left font-mono text-xs">
                <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                  <span className="text-[10px] font-sans font-bold text-indigo-400 uppercase tracking-widest">SBAR Format Preview (Demo Only)</span>
                  <span className="text-[10px] text-slate-500 font-semibold italic">Structure visualizer</span>
                </div>

                {/* S Situation */}
                <div className="space-y-1.5">
                  <div className="flex justify-between border-b border-slate-850 pb-1 font-bold text-slate-300">
                    <span>S &bull; SITUATION</span>
                    <span className="text-indigo-400 h-3 bg-slate-900 w-20 rounded animate-pulse inline-block"></span>
                  </div>
                  <div className="h-3.5 bg-slate-900 rounded-md w-full animate-pulse"></div>
                </div>
                
                {/* A Assessment */}
                <div className="space-y-1.5 pt-2">
                  <div className="flex justify-between border-b border-slate-850 pb-1 font-bold text-slate-300">
                    <span>A &bull; ASSESSMENT</span>
                    <span className="text-emerald-400 h-3 bg-slate-900 w-24 rounded animate-pulse inline-block"></span>
                  </div>
                  <div className="h-3.5 bg-slate-900 rounded-md w-5/6 animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Controls and Actions */}
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-slate-100 mb-2">Configure Summary</h2>
            
            {/* Generate Action Card */}
            <div className="bg-white border border-slate-800 p-6 rounded-2xl shadow-sm space-y-6">
              <div className="space-y-2">
                <h3 className="text-lg font-bold text-slate-100">Generate Report Snapshot</h3>
                <p className="text-sm text-slate-350">
                  Compile your child's milestones checking histories and logged parent observations into structured reports.
                </p>
              </div>

              {/* Visit context selection */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-slate-100">Select Target Visit</label>
                <select
                  value={selectedVisitId}
                  onChange={(e) => setSelectedVisitId(e.target.value)}
                  className="w-full bg-white border border-slate-800 text-slate-100 rounded-xl px-4 py-3 text-base outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
                >
                  <option value="">Latest Visit (Default)</option>
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
                className="w-full py-4 bg-indigo-600 hover:bg-indigo-755 text-white font-bold text-base rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 cursor-pointer"
              >
                <Sparkles className="h-5 w-5" />
                {loadingReport ? "Compiling Snapshot..." : "Compile Summary Snapshot"}
              </button>
            </div>

            {/* Previous Report Access Card */}
            <div className="bg-white border border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
              <h3 className="text-lg font-bold text-slate-100">Saved Clinician Visits</h3>
              {visits.length === 0 ? (
                <p className="text-sm text-slate-350 italic">No clinician visits registered. Add one under Visit Prep to link observation history.</p>
              ) : (
                <div className="divide-y divide-slate-800 max-h-48 overflow-y-auto pr-1">
                  {visits.map((v) => (
                    <div key={v.id} className="py-2.5 flex items-center justify-between text-sm">
                      <div className="text-left">
                        <p className="font-semibold text-slate-100">Dr. {v.clinician_name}</p>
                        <p className="text-xs text-slate-350">{new Date(v.visit_date).toLocaleDateString()}</p>
                      </div>
                      <button
                        onClick={() => {
                          setSelectedVisitId(v.id);
                          // Trigger assembly for this visit
                          setTimeout(() => {
                            const payload = {
                              child_id: activeChild.id,
                              visit_id: v.id,
                            };
                            setLoadingReport(true);
                            setReportData(null);
                            fetchWithAuth(`${apiUrl}/reports`, {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify(payload),
                            })
                            .then((res: any) => res.json())
                            .then((data: any) => {
                              setReportData(data.report_json);
                              setLoadingReport(false);
                            })
                            .catch((err: any) => {
                              console.error(err);
                              setLoadingReport(false);
                            });
                          }, 100);
                        }}
                        className="text-xs font-bold text-indigo-600 hover:underline cursor-pointer"
                      >
                        View
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        /* Document Layout */
        <div className={`grid grid-cols-1 ${devMode ? 'lg:grid-cols-3' : 'lg:grid-cols-1'} gap-8`}>
          
          {/* Main Document Preview */}
          <div className={`${devMode ? 'lg:col-span-2' : 'lg:col-span-1'} bg-white text-slate-900 rounded-2xl p-8 shadow-sm border border-slate-200 print:p-0 print:border-none print:shadow-none space-y-8 text-left`}>
            
            {/* Document Header */}
            <div className="flex justify-between items-start border-b border-slate-800 pb-6 flex-wrap gap-4">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-slate-50 uppercase">NEUROLENS</h2>
                <p className="text-sm text-slate-350 font-semibold uppercase mt-1">
                  Developmental Summary & Visit Prep
                </p>
              </div>
              <div className="text-right text-sm text-slate-300 font-mono">
                <p>Date: {new Date(reportData.metadata.generated_at).toLocaleDateString()}</p>
                <p>Snapshot ID: v{reportData.metadata.version}</p>
              </div>
            </div>

            {/* Disclaimer */}
            <div className="bg-amber-50/55 border border-amber-200 rounded-xl p-5 space-y-1 print:bg-white print:border-amber-200">
              <h4 className="text-sm font-bold uppercase tracking-wider text-amber-800">
                Responsible AI Disclaimer
              </h4>
              <p className="text-sm leading-relaxed text-slate-100">
                Neurolens is designed as a qualitative log compilation to support parent-clinician preparation. <strong>This document is not diagnostic, does not evaluate autism risk, and does not provide medical assessments.</strong> Clinical assessments must be performed by qualified healthcare professionals.
              </p>
            </div>

            {reportTab === "clinician" ? (
              /* CLINICIAN BRIEF (SBAR STRUCTURE) */
              <div className="space-y-8 font-sans">
                
                {/* 1. SITUATION (S) */}
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-slate-50 uppercase tracking-wide border-b border-slate-800 pb-1.5">
                    S &bull; Situation
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 bg-slate-950 p-6 rounded-xl border border-slate-880 border-slate-800">
                    <div className="space-y-1">
                      <p className="text-sm font-bold text-slate-350 uppercase">Child Profile</p>
                      <p className="text-base font-bold text-slate-100">
                        {brief.demographics.first_name} {brief.demographics.last_name}
                      </p>
                      <p className="text-sm text-slate-300 mt-0.5">
                        Age: {brief.demographics.chronological_age} &bull; DOB: {new Date(brief.demographics.date_of_birth).toLocaleDateString()}
                      </p>
                    </div>
                    
                    <div className="space-y-1">
                      <p className="text-sm font-bold text-slate-355 uppercase">Scheduled Visit Context</p>
                      {brief.visit_context && brief.visit_context.date ? (
                        <>
                          <p className="text-sm font-semibold text-slate-100">
                            Pediatrician: Dr. {brief.visit_context.clinician || "Sharma"}
                          </p>
                          <p className="text-sm text-slate-300">
                            Priority: <span className="font-semibold capitalize">{brief.visit_context.priority}</span> &bull; Concern level: <span className="font-semibold capitalize text-amber-700">{brief.visit_context.concern_level}</span>
                          </p>
                        </>
                      ) : (
                        <p className="text-sm text-slate-350 italic">No scheduled visit parameters attached.</p>
                      )}
                    </div>
                  </div>

                  {brief.visit_context && brief.visit_context.primary_concern_note && (
                    <div className="bg-slate-950 border border-slate-800 p-6 rounded-xl">
                      <span className="text-sm font-bold text-slate-350 uppercase block mb-1">Primary Visit Goal / Concern Note</span>
                      <p className="text-sm text-slate-200 leading-relaxed font-serif">
                        "{brief.visit_context.primary_concern_note}"
                      </p>
                    </div>
                  )}
                </div>

                {/* 2. BACKGROUND (B) */}
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-slate-50 uppercase tracking-wide border-b border-slate-800 pb-1.5">
                    B &bull; Background
                  </h3>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-sm text-slate-200">
                    <div className="space-y-3">
                      <h4 className="text-sm font-bold text-slate-350 uppercase">Family & Observers</h4>
                      {brief.parents.map((p) => (
                        <div key={p.id} className="border-l border-slate-800 pl-4 space-y-0.5">
                          <p className="font-semibold text-slate-100">{p.first_name} {p.last_name}</p>
                          <p className="text-sm text-slate-355 text-slate-350">{p.relationship} &bull; {p.email}</p>
                        </div>
                      ))}
                    </div>

                    <div className="space-y-3">
                      <h4 className="text-sm font-bold text-slate-350 uppercase">Observation Summary</h4>
                      {brief.quality_data ? (
                        <div className="space-y-1 bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-sm">
                          <p>Logging scope: <strong>{brief.quality_data.quality_level} logs</strong></p>
                          <p>Observation period: {brief.quality_data.observation_period}</p>
                          <p>Moments logged: {brief.quality_data.total_observations}</p>
                          <p>Represented areas: {brief.quality_data.domains_represented}</p>
                        </div>
                      ) : (
                        <p className="text-sm text-slate-350 italic">No logging statistics available.</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* 3. ASSESSMENT (A) */}
                <div className="space-y-6 print:break-inside-avoid">
                  <h3 className="text-lg font-bold text-slate-50 uppercase tracking-wide border-b border-slate-800 pb-1.5">
                    A &bull; Assessment
                  </h3>

                  {/* Visit Delta */}
                  {brief.visit_delta && (
                    <div className="space-y-4 bg-slate-950 p-6 rounded-xl border border-slate-800">
                      <h4 className="text-xs font-bold text-slate-350 uppercase tracking-wider border-b border-slate-800 pb-1.5">
                        Something that changed (Since Last Visit)
                      </h4>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                        <div className="space-y-2">
                          <div>
                            <span className="font-semibold text-rose-700">&bull; Regressions ({brief.visit_delta.new_regressions?.length || 0}):</span>{" "}
                            {brief.visit_delta.new_regressions && brief.visit_delta.new_regressions.length > 0 
                              ? brief.visit_delta.new_regressions.map((r: any) => r.body).join("; ")
                              : "None reported"
                            }
                          </div>
                          <div>
                            <span className="font-semibold text-amber-700">&bull; New Concerns ({brief.visit_delta.new_concerns?.length || 0}):</span>{" "}
                            {brief.visit_delta.new_concerns && brief.visit_delta.new_concerns.length > 0 
                              ? brief.visit_delta.new_concerns.map((c: any) => c.body).join("; ")
                              : "None logged"
                            }
                          </div>
                          <div>
                            <span className="font-semibold text-slate-100">&bull; Persistent Concerns ({brief.visit_delta.persistent_concerns?.length || 0}):</span>{" "}
                            {brief.visit_delta.persistent_concerns && brief.visit_delta.persistent_concerns.length > 0
                              ? brief.visit_delta.persistent_concerns.map((c: any) => c.body).join("; ")
                              : "None logged"
                            }
                          </div>
                        </div>

                        <div>
                          <span className="font-semibold text-slate-100 block mb-2">New Milestones Observed:</span>
                          {brief.visit_delta.new_milestones_observed && brief.visit_delta.new_milestones_observed.length > 0 ? (
                            <ul className="list-disc pl-5 space-y-1 text-sm text-slate-200">
                              {brief.visit_delta.new_milestones_observed.map((m: any, idx: number) => {
                                const mappedDomainName = m.domain === "Gross Motor" ? "Movement" :
                                                         m.domain === "Fine Motor" ? "Hands & Fingers" :
                                                         m.domain === "Social Emotional" ? "Feelings & Friendships" :
                                                         m.domain === "Cognitive" ? "Thinking & Learning" : m.domain;
                                return (
                                  <li key={idx}><strong>[{mappedDomainName}]</strong> {m.title}</li>
                                );
                              })}
                            </ul>
                          ) : (
                            <p className="italic text-slate-350 text-sm">No new milestones logged since last brief.</p>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Milestone Checklist Table */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-slate-355 text-slate-350 uppercase">CDC developmental milestone checklist</h4>
                    <div className="border border-slate-800 rounded-xl overflow-hidden shadow-sm">
                      <table className="w-full border-collapse text-left text-sm">
                        <thead>
                          <tr className="bg-slate-950 text-slate-100 font-semibold border-b border-slate-800">
                            <th className="py-3 px-4">Area</th>
                            <th className="py-3 px-4">Milestone</th>
                            <th className="py-3 px-4 text-center">Age Range</th>
                            <th className="py-3 px-4 text-right">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                          {brief.milestone_matrix.map((m) => {
                            const domainLabel = m.domain === "Gross Motor" ? "Movement" :
                                                m.domain === "Fine Motor" ? "Hands & Fingers" :
                                                m.domain === "Social Emotional" ? "Feelings & Friendships" :
                                                m.domain === "Cognitive" ? "Thinking & Learning" : m.domain;
                            
                            return (
                              <tr key={m.id} className="hover:bg-slate-950/40 align-top">
                                <td className="py-3 px-4 font-semibold text-slate-200">{domainLabel}</td>
                                <td className="py-3 px-4 text-slate-200 space-y-2">
                                  <div className="space-y-1">
                                    <span className="font-semibold text-slate-100">{m.title}</span>
                                    <p className="text-sm text-slate-350 leading-relaxed">{m.description}</p>
                                  </div>
                                  
                                  {m.evidence_count > 0 && (
                                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl text-sm">
                                      <p className="font-semibold text-slate-350 uppercase tracking-wider mb-2">
                                        Supporting observations ({m.evidence_count})
                                      </p>
                                      {m.evidence_observation_ids.map((id) => {
                                        const l = findEvidenceLog(id);
                                        if (!l) return null;
                                        return (
                                          <div key={id} className="border-t border-slate-800/50 pt-2.5 mt-2.5 first:border-0 first:pt-0 first:mt-0 italic font-serif text-slate-200">
                                            "{l.body}"
                                            <span className="block text-sm text-slate-350 not-italic mt-1 font-sans">
                                              Observed: {new Date(l.observed_at).toLocaleDateString()} &bull; By: {l.observer_relation || "Parent"}
                                            </span>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  )}
                                </td>
                                <td className="py-3 px-4 text-center font-mono whitespace-nowrap text-slate-350">{m.age_range}</td>
                                <td className="py-3 px-4 text-right">
                                  <span className="text-sm uppercase font-bold px-2.5 py-1 rounded-lg border border-slate-800 bg-slate-950">
                                    {m.status.replace("_", " ")}
                                  </span>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                {/* 4. RECOMMENDATION (R) */}
                <div className="space-y-4 print:break-inside-avoid">
                  <h3 className="text-lg font-bold text-slate-50 uppercase tracking-wide border-b border-slate-800 pb-1.5">
                    R &bull; Recommendation
                  </h3>
                  
                  {/* Pattern clusters */}
                  {brief.clusters && brief.clusters.length > 0 ? (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-slate-350 uppercase">Recurring behavior pattern topics</h4>
                      <div className="grid grid-cols-1 gap-3">
                        {brief.clusters.map((c) => (
                          <div key={c.cluster_id} className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-2">
                            <span className="text-xs font-bold text-indigo-600 bg-indigo-50 border border-indigo-100 px-2.5 py-0.5 rounded-md">
                              {c.domain_name === "Gross Motor" ? "Movement" :
                               c.domain_name === "Fine Motor" ? "Hands & Fingers" :
                               c.domain_name === "Social Emotional" ? "Feelings & Friendships" :
                               c.domain_name === "Cognitive" ? "Thinking & Learning" : c.domain_name} Area
                            </span>
                            <h4 className="text-base font-bold text-slate-100 mt-2">{c.label}</h4>
                            <div className="space-y-2 pl-4 border-l border-slate-800 mt-3 text-sm text-slate-300">
                              {c.observations.map((o) => (
                                <p key={o.id} className="italic font-serif leading-relaxed">
                                  &bull; "{o.structured_body || o.body}" ({new Date(o.observed_at).toLocaleDateString()})
                                </p>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-slate-355 text-slate-350 italic">No recurring behavior pattern clusters detected.</p>
                  )}
                </div>

              </div>
            ) : (
              /* WARM PARENT SUMMARY */
              <div className="space-y-8 font-serif">
                
                {/* Introduction narrative */}
                <div className="bg-indigo-50/20 border border-indigo-100/50 p-8 rounded-2xl space-y-3">
                  <h3 className="text-sm font-bold uppercase tracking-widest text-indigo-650 font-sans">
                    A reflection of {activeChild.first_name}'s journey
                  </h3>
                  <p className="text-base text-slate-800 leading-relaxed">
                    {reportData.parent_summary?.narrative || `We have compiled ${activeChild.first_name}'s developmental moments. This narrative reflection showcases growth highlights and focus areas.`}
                  </p>
                </div>

                {/* Growth Highlights */}
                <div className="space-y-4 text-left">
                  <h4 className="text-sm font-bold uppercase tracking-widest text-slate-350 font-sans flex items-center gap-2">
                    <Award className="h-5 w-5 text-indigo-600" />
                    Growth Highlights
                  </h4>
                  {reportData.parent_summary?.key_achievements && reportData.parent_summary.key_achievements.length > 0 ? (
                    <ul className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-sans">
                      {reportData.parent_summary.key_achievements.map((item, idx) => (
                        <li key={idx} className="text-sm text-slate-200 bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-start gap-3 shadow-xs">
                          <span className="text-indigo-655 font-bold mt-0.5">✓</span>
                          <span className="leading-relaxed">{item}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-slate-350 italic font-sans pl-2">No key highlights recorded in this summary.</p>
                  )}
                </div>

                {/* Things We Noticed */}
                <div className="space-y-4 text-left">
                  <h4 className="text-sm font-bold uppercase tracking-widest text-slate-350 font-sans flex items-center gap-2">
                    <Eye className="h-5 w-5 text-indigo-600" />
                    Things We Noticed
                  </h4>
                  <div className="space-y-4 pl-2 font-sans text-sm text-slate-200">
                    {reportData.parent_summary?.parent_effort?.text && (
                      <p className="leading-relaxed bg-slate-950 border border-slate-800 p-4 rounded-xl">
                        <strong>Logging & Play Summary:</strong> {reportData.parent_summary.parent_effort.text}
                      </p>
                    )}
                    {reportData.parent_summary?.observation_blind_spots && reportData.parent_summary.observation_blind_spots.length > 0 && (
                      <p className="leading-relaxed bg-slate-950 border border-slate-800 p-4 rounded-xl">
                        <strong>Targeted Observation Areas:</strong> We noticed lower coverage in <strong>{reportData.parent_summary.observation_blind_spots.map((d: string) => d.replace("_", " ")).join(", ")}</strong>. Sharing logs in these areas will give your clinician a more complete view of {activeChild.first_name}'s progress.
                      </p>
                    )}
                  </div>
                </div>

                {/* Questions Worth Discussing */}
                <div className="space-y-4 text-left">
                  <h4 className="text-sm font-bold uppercase tracking-widest text-slate-355 text-slate-350 font-sans flex items-center gap-2">
                    <MessageSquare className="h-5 w-5 text-indigo-600" />
                    Pediatrician Discussion Guide
                  </h4>
                  
                  <div className="bg-slate-955 bg-slate-950 border border-slate-800 p-6 rounded-2xl space-y-4 font-sans text-sm text-slate-200">
                    <p className="font-bold text-slate-100 text-base">Consider asking your pediatrician about these observed areas:</p>
                    <ul className="space-y-3 list-disc pl-5 leading-relaxed font-medium">
                      {brief.clusters && brief.clusters.length > 0 ? (
                        brief.clusters.map((c, idx) => (
                          <li key={idx}>
                            Discuss behaviors around <strong>{c.label.toLowerCase()}</strong> observed during their daily logs.
                          </li>
                        ))
                      ) : (
                        <li>
                          Discuss milestone progression trends across motor skills and general communication behaviors.
                        </li>
                      )}
                    </ul>
                  </div>
                </div>

                {/* Reflection */}
                <div className="space-y-4 border-t border-slate-800 pt-6 text-left">
                  <h4 className="text-sm font-bold uppercase tracking-widest text-slate-350 font-sans flex items-center gap-2">
                    <Info className="h-5 w-5 text-indigo-600" />
                    Grounded Reflection
                  </h4>
                  <p className="text-sm text-slate-300 leading-relaxed font-medium">
                    Remember that developmental checks are checkpoints, not strict schedules. Every child follows a unique progress track. Your regular observations are the most valuable tool to align with clinicians and support {activeChild.first_name}'s developmental story.
                  </p>
                </div>

              </div>
            )}
          </div>

          {/* Developer JSON Inspector */}
          {devMode && (
            <div className="lg:col-span-1 space-y-6">
              <div className="text-left">
                <h2 className="text-xl font-bold text-slate-900">Developer JSON</h2>
                <p className="text-sm text-slate-500 mt-1">This read-only inspection block represents the exact frozen SQL record payload.</p>
              </div>

              <div className="bg-white border border-slate-200 p-6 rounded-2xl space-y-4 sticky top-24 text-left shadow-sm">
                <span className="text-xs bg-slate-100 px-3 py-1 rounded-lg text-slate-600 border border-slate-200 font-mono">
                  frozen_snapshot_schema (JSON)
                </span>
                <pre className="text-xs text-slate-700 font-mono bg-slate-50 p-4 rounded-xl border border-slate-200 overflow-x-auto max-h-[500px] leading-relaxed">
                  {JSON.stringify(reportData, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
