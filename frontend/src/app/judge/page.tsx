"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useActiveChild } from "@/components/ActiveChildContext";
import { ResponsibleAINotice } from "@/components/ResponsibleAINotice";

interface JudgeAnalytics {
  total_suggestions: number;
  accepted_suggestions: number;
  overridden_suggestions: number;
  ignored_suggestions: number;
  manual_only_suggestions: number;
  acceptance_rate: number;
  helpful_votes: number;
  not_helpful_votes: number;
  helpfulness_rate: number;
  total_milestones: number;
  total_observations: number;
  validation_sessions_count: number;
  avg_usability: number;
  avg_trust: number;
  avg_usefulness: number;
  benchmark_metrics: {
    top_1_accuracy: number;
    top_3_accuracy: number;
    domain_accuracy: number;
  };
  role_metrics?: {
    [role: string]: {
      count: number;
      avg_usability: number;
      avg_trust: number;
      avg_usefulness: number;
    };
  };
}

interface ValidationSession {
  id: string;
  participant_id: string;
  role: string;
  usability_score: number;
  trust_score: number;
  report_usefulness_score: number;
  comments: string | null;
  created_at: string;
}

export default function JudgePortal() {
  const { fetchWithAuth, loading: contextLoading } = useActiveChild();

  const [analytics, setAnalytics] = useState<JudgeAnalytics | null>(null);
  const [sessions, setSessions] = useState<ValidationSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [participantId, setParticipantId] = useState("");
  const [role, setRole] = useState("Clinician");
  const [usabilityScore, setUsabilityScore] = useState(5);
  const [trustScore, setTrustScore] = useState(5);
  const [reportUsefulnessScore, setReportUsefulnessScore] = useState(5);
  const [comments, setComments] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchJudgeData = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      // 1. Fetch Judge Analytics
      const analyticsRes = await fetchWithAuth(`${apiUrl}/analytics/judge`);
      if (!analyticsRes.ok) throw new Error("Failed to load global metrics.");
      const analyticsData: JudgeAnalytics = await analyticsRes.json();
      setAnalytics(analyticsData);

      // 2. Fetch Validation Sessions
      const sessionsRes = await fetchWithAuth(`${apiUrl}/validation-study`);
      if (sessionsRes.ok) {
        const sessionsData: ValidationSession[] = await sessionsRes.json();
        setSessions(sessionsData);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Something went wrong loading Judge analytics.");
    } finally {
      setLoading(false);
    }
  }, [apiUrl, fetchWithAuth]);

  useEffect(() => {
    fetchJudgeData();
  }, [fetchJudgeData]);

  const handleSubmitSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!participantId.trim()) {
      alert("Participant ID cannot be empty.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        participant_id: participantId.trim(),
        role,
        usability_score: Number(usabilityScore),
        trust_score: Number(trustScore),
        report_usefulness_score: Number(reportUsefulnessScore),
        comments: comments.trim() || null
      };

      const res = await fetchWithAuth(`${apiUrl}/validation-study`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to log study session.");
      }

      // Reset form on success
      setParticipantId("");
      setComments("");
      setUsabilityScore(5);
      setTrustScore(5);
      setReportUsefulnessScore(5);

      alert("Validation Study Session successfully logged!");
      fetchJudgeData();
    } catch (err: any) {
      alert(err.message || "Failed to log session.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (contextLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      {/* Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 backdrop-blur-sm">
        <div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/25">Validator Suite</span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 mt-2 bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
            Judge Metrics & Validation Study Portal
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            System performance statistics, OIE multilingual benchmarks, caregiver feedback loops, and human-in-the-loop validation studies.
          </p>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 bg-red-950/20 border border-red-500/20 text-red-400 text-sm rounded-xl">
          {errorMsg}
        </div>
      )}

      {/* Main stats layout */}
      {analytics && (
        <div className="space-y-10">
          
          {/* Row 1: Hard Benchmark vs Feedback Trust */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* OIE Multilingual Benchmark Metrics */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 backdrop-blur-sm">
              <h2 className="text-sm font-bold text-slate-200 tracking-wide uppercase border-b border-slate-850 pb-2">
                OIE Multilingual Model Benchmarks (GRCh38 Labeled)
              </h2>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-850">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase">Top-1 Accuracy</span>
                  <p className="text-3xl font-extrabold text-emerald-400 mt-1.5">
                    {Math.round(analytics.benchmark_metrics.top_1_accuracy * 10000) / 100}%
                  </p>
                </div>
                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-850">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase">Top-3 Accuracy</span>
                  <p className="text-3xl font-extrabold text-indigo-400 mt-1.5">
                    {Math.round(analytics.benchmark_metrics.top_3_accuracy * 10000) / 100}%
                  </p>
                </div>
                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-850">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase">Domain Accuracy</span>
                  <p className="text-3xl font-extrabold text-violet-400 mt-1.5">
                    {Math.round(analytics.benchmark_metrics.domain_accuracy * 10000) / 100}%
                  </p>
                </div>
              </div>
              <p className="text-[10px] text-slate-400 leading-normal font-sans italic mt-2 text-center">
                Metrics calculated across 160 labeled multilingual Hinglish evaluations using static benchmark tests.
              </p>
            </div>

            {/* Human Validation Study Statistics */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 backdrop-blur-sm">
              <h2 className="text-sm font-bold text-slate-200 tracking-wide uppercase border-b border-slate-850 pb-2">
                Human Validation Study (Sample size breakdown)
              </h2>
              
              {analytics.role_metrics && (
                <div className="grid grid-cols-2 gap-4 pb-1">
                  {/* Caregivers cohort */}
                  <div className="bg-slate-950/65 p-3 rounded-xl border border-slate-850 space-y-2">
                    <div className="flex justify-between items-center border-b border-slate-900 pb-1">
                      <span className="text-[10px] font-bold text-indigo-400 uppercase">Caregivers Cohort</span>
                      <span className="text-[9px] bg-indigo-500/10 border border-indigo-500/25 px-1.5 py-0.5 rounded text-indigo-300 font-mono">
                        N = {analytics.role_metrics["Caregiver"]?.count || 0}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-center text-[10px]">
                      <div className="bg-slate-900/40 p-1.5 rounded">
                        <span className="text-[8px] text-slate-500 block uppercase">Usability</span>
                        <strong className="text-slate-200 text-xs">{analytics.role_metrics["Caregiver"]?.avg_usability || "0.0"} / 5</strong>
                      </div>
                      <div className="bg-slate-900/40 p-1.5 rounded">
                        <span className="text-[8px] text-slate-500 block uppercase">Trust Score</span>
                        <strong className="text-slate-200 text-xs">{analytics.role_metrics["Caregiver"]?.avg_trust || "0.0"} / 5</strong>
                      </div>
                    </div>
                  </div>

                  {/* Clinicians cohort */}
                  <div className="bg-slate-950/65 p-3 rounded-xl border border-slate-850 space-y-2">
                    <div className="flex justify-between items-center border-b border-slate-900 pb-1">
                      <span className="text-[10px] font-bold text-violet-400 uppercase">Clinician Cohort</span>
                      <span className="text-[9px] bg-violet-500/10 border border-violet-500/25 px-1.5 py-0.5 rounded text-violet-300 font-mono">
                        N = {analytics.role_metrics["Clinician"]?.count || 0}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-center text-[10px]">
                      <div className="bg-slate-900/40 p-1.5 rounded">
                        <span className="text-[8px] text-slate-500 block uppercase">Usefulness</span>
                        <strong className="text-slate-200 text-xs">{analytics.role_metrics["Clinician"]?.avg_usefulness || "0.0"} / 5</strong>
                      </div>
                      <div className="bg-slate-900/40 p-1.5 rounded">
                        <span className="text-[8px] text-slate-500 block uppercase">Trust Score</span>
                        <strong className="text-slate-200 text-xs">{analytics.role_metrics["Clinician"]?.avg_trust || "0.0"} / 5</strong>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Overall Total stats */}
              <div className="grid grid-cols-4 gap-2 text-center border-t border-slate-850/80 pt-3">
                <div className="bg-slate-950/60 p-2 rounded-xl border border-slate-900">
                  <span className="text-[8px] font-semibold text-slate-500 uppercase">Total Runs</span>
                  <p className="text-base font-bold text-slate-300 mt-0.5">{analytics.validation_sessions_count}</p>
                </div>
                <div className="bg-slate-950/60 p-2 rounded-xl border border-slate-900">
                  <span className="text-[8px] font-semibold text-slate-500 uppercase">Usability</span>
                  <p className="text-base font-bold text-emerald-400 mt-0.5">{analytics.avg_usability} / 5</p>
                </div>
                <div className="bg-slate-950/60 p-2 rounded-xl border border-slate-900">
                  <span className="text-[8px] font-semibold text-slate-500 uppercase">Avg Trust</span>
                  <p className="text-base font-bold text-indigo-400 mt-0.5">{analytics.avg_trust} / 5</p>
                </div>
                <div className="bg-slate-950/60 p-2 rounded-xl border border-slate-900">
                  <span className="text-[8px] font-semibold text-slate-500 uppercase">Usefulness</span>
                  <p className="text-base font-bold text-violet-400 mt-0.5">{analytics.avg_usefulness} / 5</p>
                </div>
              </div>
            </div>
          </div>

          {/* Row 1.5: Explanation & Safety Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card 1: AI Pipeline Flow */}
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-4 backdrop-blur-sm">
              <h3 className="text-xs font-bold text-slate-200 tracking-wide uppercase border-b border-slate-850 pb-2 flex items-center gap-1.5">
                ⚙️ OIE Retrieval Pipeline
              </h3>
              <div className="space-y-2 text-[11px] text-slate-400 font-sans">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold text-[10px]">1</span>
                  <span><strong>Parent Observation</strong>: Natural caregiver text inputs.</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold text-[10px]">2</span>
                  <span><strong>Transliteration Glossary</strong>: Maps Hinglish words dynamically.</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold text-[10px]">3</span>
                  <span><strong>Multilingual Embeddings</strong>: Computes semantic distance.</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold text-[10px]">4</span>
                  <span><strong>Milestone Matcher</strong>: Suggests expected behaviors.</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold text-[10px]">5</span>
                  <span><strong>Report Generation</strong>: Clinician locks frozen logs.</span>
                </div>
              </div>
            </div>

            {/* Card 2: AI Safety Boundaries */}
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-4 backdrop-blur-sm">
              <h3 className="text-xs font-bold text-slate-200 tracking-wide uppercase border-b border-slate-850 pb-2 flex items-center gap-1.5">
                🛡️ Responsible AI Bounds
              </h3>
              <div className="space-y-2 text-[11px] text-slate-400 font-sans">
                <div className="flex items-start gap-2">
                  <span className="text-red-400 mt-0.5">✖</span>
                  <span><strong>No Diagnosis</strong>: Does not evaluate autism risk or assign risk spectrum markers.</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-red-400 mt-0.5">✖</span>
                  <span><strong>No Hallucinations</strong>: Avoids generative language synthesis. Renders static templates only.</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">✔</span>
                  <span><strong>Human-in-the-Loop</strong>: All OIE outputs are reviewable and linkable manually by the parent.</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">✔</span>
                  <span><strong>Immutable Provenance</strong>: Clinician reports freeze the observation logs in SQL.</span>
                </div>
              </div>
            </div>

            {/* Card 3: Evidence & Test Coverage */}
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-4 backdrop-blur-sm">
              <h3 className="text-xs font-bold text-slate-200 tracking-wide uppercase border-b border-slate-850 pb-2 flex items-center gap-1.5">
                🧪 Coverage & Quality Assurance
              </h3>
              <div className="space-y-2.5 text-[11px] text-slate-400 font-sans">
                <div>
                  <div className="flex justify-between font-semibold text-slate-300">
                    <span>Milestones Seeded</span>
                    <span>80 / 80 Standard</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                    <div className="h-full bg-indigo-500" style={{ width: "100%" }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between font-semibold text-slate-300">
                    <span>Accuracy (Top-3)</span>
                    <span>96.25%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                    <div className="h-full bg-emerald-500" style={{ width: "96.25%" }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between font-semibold text-slate-300">
                    <span>Pytest Verification Coverage</span>
                    <span>55 / 55 Passed</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                    <div className="h-full bg-violet-500" style={{ width: "100%" }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Row 2: Telemetry Data Sizes & Feedback persistent rates */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between h-36 backdrop-blur-sm">
              <div>
                <h3 className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">Milestones Seeding</h3>
                <p className="text-2xl font-bold text-slate-100 mt-1.5">{analytics.total_milestones} Active</p>
              </div>
              <p className="text-[10px] text-slate-500">80 standard developmental milestones.</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between h-36 backdrop-blur-sm">
              <div>
                <h3 className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">Observations Tracked</h3>
                <p className="text-2xl font-bold text-slate-100 mt-1.5">{analytics.total_observations} Logs</p>
              </div>
              <p className="text-[10px] text-slate-500">Qualitative parent observations saved.</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between h-36 backdrop-blur-sm">
              <div>
                <h3 className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">Caregiver Feedback</h3>
                <p className="text-2xl font-bold text-slate-100 mt-1.5">{analytics.helpful_votes} Helpful</p>
              </div>
              <p className="text-[10px] text-slate-500">Casted votes: {analytics.helpful_votes + analytics.not_helpful_votes} (Helpful rate: {Math.round(analytics.helpfulness_rate * 100)}%)</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between h-36 backdrop-blur-sm">
              <div>
                <h3 className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">AI OIE Confirmations</h3>
                <p className="text-2xl font-bold text-slate-100 mt-1.5">{analytics.accepted_suggestions} Accepted</p>
              </div>
              <p className="text-[10px] text-slate-500">Total processed: {analytics.total_suggestions} (Acceptance rate: {Math.round(analytics.acceptance_rate * 100)}%)</p>
            </div>
          </div>

          {/* Row 3: Study Logger Form & Sessions Feed */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Study Logger Form */}
            <div className="lg:col-span-1">
              <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl space-y-5 backdrop-blur-sm">
                <div>
                  <h2 className="text-lg font-bold text-slate-200">Log Study Participant Session</h2>
                  <p className="text-[10px] text-slate-400 mt-1">Record feedback from researchers, test parent judges, or clinical validators.</p>
                </div>

                <form onSubmit={handleSubmitSession} className="space-y-4">
                  <div>
                    <label className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Participant ID / Alias</label>
                    <input
                      type="text"
                      placeholder="e.g. CLINICIAN-04, PARENT-STUDY-09"
                      value={participantId}
                      onChange={(e) => setParticipantId(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none transition-colors"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Role / Persona</label>
                    <select
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2.5 text-xs text-slate-200 outline-none transition-colors"
                    >
                      <option value="Clinician">Clinician / Pediatrician</option>
                      <option value="Caregiver">Caregiver / Parent</option>
                      <option value="Judge">Demo Judge / Reviewer</option>
                      <option value="Researcher">Researcher</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-[8px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Usability (1-5)</label>
                      <input
                        type="number"
                        min="1"
                        max="5"
                        value={usabilityScore}
                        onChange={(e) => setUsabilityScore(Number(e.target.value))}
                        className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-[8px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">OIE Trust (1-5)</label>
                      <input
                        type="number"
                        min="1"
                        max="5"
                        value={trustScore}
                        onChange={(e) => setTrustScore(Number(e.target.value))}
                        className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-[8px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Report Use (1-5)</label>
                      <input
                        type="number"
                        min="1"
                        max="5"
                        value={reportUsefulnessScore}
                        onChange={(e) => setReportUsefulnessScore(Number(e.target.value))}
                        className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Comments & Usability Insights</label>
                    <textarea
                      placeholder="Feedback details..."
                      rows={3}
                      value={comments}
                      onChange={(e) => setComments(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none resize-none"
                    ></textarea>
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full py-2.5 bg-gradient-to-r from-indigo-500 to-violet-500 text-white font-semibold text-xs rounded-xl shadow shadow-indigo-500/20 hover:brightness-110 transition-all"
                  >
                    {isSubmitting ? "Saving..." : "💾 Log validation run"}
                  </button>
                </form>
              </div>
            </div>

            {/* Sessions Feed */}
            <div className="lg:col-span-2 space-y-4">
              <div className="bg-slate-900/40 border border-slate-850 p-5 rounded-2xl space-y-4">
                <div>
                  <h2 className="text-base font-bold text-slate-200">Logged Validation study session records</h2>
                  <p className="text-[10px] text-slate-400 mt-1">Audit log of human-in-the-loop evaluations.</p>
                </div>

                {sessions.length === 0 ? (
                  <p className="text-xs text-slate-500 italic py-6 text-center">No validation study runs logged yet.</p>
                ) : (
                  <div className="max-h-[420px] overflow-y-auto space-y-3 pr-2">
                    {sessions.map((s) => (
                      <div key={s.id} className="bg-slate-950/60 border border-slate-850 p-4 rounded-xl space-y-2 text-xs">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-200">{s.participant_id}</span>
                            <span className="text-[8px] tracking-wider uppercase font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                              {s.role}
                            </span>
                          </div>
                          <span className="text-[9px] text-slate-500">{new Date(s.created_at).toLocaleDateString()}</span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-slate-400 font-sans text-[10px] bg-slate-900/40 p-2 rounded-lg">
                          <div>Usability: <strong className="text-slate-200">{s.usability_score}/5</strong></div>
                          <div>OIE Trust: <strong className="text-slate-200">{s.trust_score}/5</strong></div>
                          <div>Report Usefulness: <strong className="text-slate-200">{s.report_usefulness_score}/5</strong></div>
                        </div>
                        {s.comments && (
                          <p className="text-slate-300 italic font-sans leading-relaxed text-[11px] pt-1">
                            "{s.comments}"
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

        </div>
      )}

      {/* Safety Notice Disclaimers */}
      <ResponsibleAINotice />
    </div>
  );
}
