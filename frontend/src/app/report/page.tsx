"use client";

export default function ReportPreview() {
  const sampleReportJson = {
    metadata: {
      platform: "Neurolens V1",
      generated_at: "2026-06-11T23:15:00Z",
      version: "1.0.0"
    },
    child: {
      first_name: "Leo",
      last_name: "Carter",
      date_of_birth: "2024-06-15",
      chronological_age: "24 months",
      gender: "Male"
    },
    parents: [
      {
        first_name: "Sarah",
        last_name: "Carter",
        relationship: "Mother",
        email: "sarah.carter@example.com"
      }
    ],
    visit_context: {
      date: "2026-06-25",
      clinician: "Dr. Evelyn Marcus",
      priority: "consultation",
      concern_level: "medium",
      primary_concern_note: "Primary focus of this visit is to discuss communication progress. Leo has achieved solid motor milestones, but we are noticing inconsistency in his response to verbal requests and name calls. We would love advice on social attention exercises."
    },
    milestones: [
      { domain: "Communication", title: "Points to show someone what he wants", status: "achieved", age_range: "18-24 Months" },
      { domain: "Communication", title: "Says at least two words together", status: "in_progress", age_range: "18-24 Months" },
      { domain: "Social Emotional", title: "Looks at your face when you talk to him", status: "achieved", age_range: "18-24 Months" },
      { domain: "Gross Motor", title: "Kicks a ball forward", status: "achieved", age_range: "18-24 Months" },
      { domain: "Gross Motor", title: "Runs easily without falling", status: "achieved", age_range: "18-24 Months" }
    ],
    observations: [
      {
        entry_type: "concern",
        body: "Not responding to name call, even when sitting nearby and with minimal background noise. Appeared fully locked onto stacking blocks.",
        domain: "Communication",
        observed_at: "2026-06-11T16:12:00Z",
        context_note: "Stacking blocks in living room",
        is_regression: false
      },
      {
        entry_type: "milestone_observation",
        body: "Leo pointed directly to the teddy bear on the top shelf to show me what he wanted, making eye contact immediately after pointing.",
        domain: "Social Emotional",
        observed_at: "2026-06-10T14:30:00Z",
        context_note: "Playroom before nap",
        is_regression: false
      }
    ]
  };

  return (
    <div className="space-y-8">
      {/* Header Panel */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Clinician Report Snapshot</h1>
          <p className="text-xs text-slate-400 mt-1">Review, print, or serialize the historical record compiled for the upcoming consultation.</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold rounded-xl border border-slate-700 transition-colors" onClick={() => window.print()}>
            🖨️ Print / PDF
          </button>
          <button className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-violet-500 text-white text-xs font-semibold rounded-xl shadow-lg transition-all hover:brightness-110 active:scale-95">
            💾 Freeze & Finalize
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Columns - Document Preview */}
        <div className="lg:col-span-2 bg-white text-slate-900 rounded-2xl p-8 shadow-2xl border border-slate-200 print:p-0 print:border-none print:shadow-none space-y-8">
          
          {/* Document Header */}
          <div className="flex justify-between items-start border-b border-slate-200 pb-6">
            <div>
              <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">NEUROLENS</h2>
              <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mt-1">Developmental Observation & Visit Prep Summary</p>
            </div>
            <div className="text-right text-xs text-slate-400 font-mono">
              <p>Generated: {new Date(sampleReportJson.metadata.generated_at).toLocaleDateString()}</p>
              <p>Format: JSON Snapshot v{sampleReportJson.metadata.version}</p>
            </div>
          </div>

          {/* Child & Parent Details */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 bg-slate-50 p-4 rounded-xl border border-slate-100">
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Subject Demographics</h3>
              <p className="text-sm font-bold text-slate-800">{sampleReportJson.child.first_name} {sampleReportJson.child.last_name}</p>
              <p className="text-xs text-slate-600 mt-1">Age: {sampleReportJson.child.chronological_age} &bull; Gender: {sampleReportJson.child.gender}</p>
              <p className="text-xs text-slate-600">DOB: {sampleReportJson.child.date_of_birth}</p>
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Historian / Reporter</h3>
              <p className="text-sm font-bold text-slate-800">{sampleReportJson.parents[0].first_name} {sampleReportJson.parents[0].last_name}</p>
              <p className="text-xs text-slate-600 mt-1">Relation: {sampleReportJson.parents[0].relationship}</p>
              <p className="text-xs text-slate-600">Email: {sampleReportJson.parents[0].email}</p>
            </div>
          </div>

          {/* Visit Context */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-indigo-600 uppercase tracking-wider border-b border-slate-100 pb-1.5">Visit Goals & Priority Context</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div>
                <p className="text-slate-400 font-semibold">Scheduled Clinician</p>
                <p className="font-bold text-slate-800 mt-0.5">{sampleReportJson.visit_context.clinician}</p>
              </div>
              <div>
                <p className="text-slate-400 font-semibold">Priority Classification</p>
                <p className="font-bold text-slate-800 mt-0.5 capitalize">{sampleReportJson.visit_context.priority}</p>
              </div>
              <div>
                <p className="text-slate-400 font-semibold">Parent Concern Level</p>
                <p className="font-bold text-slate-800 mt-0.5 capitalize">
                  {sampleReportJson.visit_context.concern_level}
                </p>
              </div>
            </div>
            <div className="bg-indigo-50/50 p-4 rounded-xl border border-indigo-100/50 mt-2">
              <p className="text-xs font-semibold text-slate-400 mb-1">Primary Concern Note</p>
              <p className="text-xs text-slate-700 leading-relaxed font-sans">{sampleReportJson.visit_context.primary_concern_note}</p>
            </div>
          </div>

          {/* Qualitative Observations */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-indigo-600 uppercase tracking-wider border-b border-slate-100 pb-1.5">Qualitative Observation Logs</h3>
            <div className="space-y-3">
              {sampleReportJson.observations.map((obs, index) => (
                <div key={index} className="p-3 bg-slate-50 border border-slate-100 rounded-lg space-y-1">
                  <div className="flex items-center justify-between text-[10px]">
                    <span className={`font-bold uppercase ${obs.entry_type === "concern" ? "text-red-600 bg-red-55/10 px-1 py-0.5 rounded" : "text-emerald-600"}`}>
                      {obs.entry_type.replace("_", " ")}
                    </span>
                    <span className="text-slate-400 font-mono">{new Date(obs.observed_at).toLocaleDateString()}</span>
                  </div>
                  <p className="text-xs text-slate-850 leading-relaxed">"{obs.body}"</p>
                  <p className="text-[10px] text-slate-400 font-mono">
                    Domain: {obs.domain} &bull; Context: {obs.context_note}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Developmental Milestone Tracker Matrix */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-indigo-600 uppercase tracking-wider border-b border-slate-100 pb-1.5">Developmental Milestone Matrix</h3>
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
                  {sampleReportJson.milestones.map((m, index) => (
                    <tr key={index} className="hover:bg-slate-50/50">
                      <td className="py-2.5 px-4 font-medium text-slate-700">{m.domain}</td>
                      <td className="py-2.5 px-4 text-slate-600">{m.title}</td>
                      <td className="py-2.5 px-4 text-center text-slate-500 font-mono">{m.age_range}</td>
                      <td className="py-2.5 px-4 text-right font-semibold">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase tracking-wider ${m.status === "achieved" ? "bg-emerald-100 text-emerald-800" : "bg-yellow-100 text-yellow-850"}`}>
                          {m.status.replace("_", " ")}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column - Aggregate Root Raw JSON Inspector */}
        <div className="lg:col-span-1 space-y-6">
          <div>
            <h2 className="text-xl font-bold text-slate-100">JSON snapshot</h2>
            <p className="text-xs text-slate-400 mt-1">This raw structure represents the exact aggregate root saved in the Postgres DB.</p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-4">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800">
              <span className="text-xs font-mono text-slate-400">report_json (JSONB)</span>
              <span className="text-[10px] bg-slate-850 text-indigo-400 px-1.5 py-0.5 rounded font-mono">Immutable</span>
            </div>
            <pre className="text-[10px] text-slate-300 font-mono bg-slate-950 p-4 rounded-xl border border-slate-900 overflow-x-auto h-[500px] leading-relaxed select-all">
              {JSON.stringify(sampleReportJson, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
