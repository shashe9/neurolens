"use client";

export default function Milestones() {
  const ageRanges = ["18-24 Months", "24-36 Months"];
  const domains = [
    {
      name: "Communication",
      icon: "🗣️",
      items: [
        {
          id: "m1",
          title: "Points to show someone what he wants",
          description: "Points to a toy, food, or object to draw attention, and looks back to confirm you see it.",
          range: "18-24 Months",
          source: "CDC developmental milestones (2022)",
          status: "achieved"
        },
        {
          id: "m2",
          title: "Says at least two words together",
          description: "Combines two words to make a phrase, such as 'more milk' or 'go outside' (excluding repeating phrases).",
          range: "18-24 Months",
          source: "AAP Clinician Evidence Guide (2021)",
          status: "in_progress"
        }
      ]
    },
    {
      name: "Social Emotional",
      icon: "❤️",
      items: [
        {
          id: "m3",
          title: "Looks at your face when you talk to him",
          description: "Maintains eye contact during dialogue and responds to vocal transitions.",
          range: "18-24 Months",
          source: "CDC developmental milestones (2022)",
          status: "achieved"
        },
        {
          id: "m4",
          title: "Notices when others are hurt or upset",
          description: "Looks concerned, pauses play, or approaches to comfort someone showing distress.",
          range: "24-36 Months",
          source: "CDC developmental milestones (2022)",
          status: "not_started"
        }
      ]
    },
    {
      name: "Gross Motor",
      icon: "🏃‍♂️",
      items: [
        {
          id: "m5",
          title: "Kicks a ball forward",
          description: "Swings foot to kick a small ball forward without losing balance.",
          range: "18-24 Months",
          source: "CDC developmental milestones (2022)",
          status: "achieved"
        },
        {
          id: "m6",
          title: "Runs easily without falling",
          description: "Can accelerate, change direction, and stop safely.",
          range: "18-24 Months",
          source: "AAP Clinician Evidence Guide (2021)",
          status: "achieved"
        }
      ]
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header and Age filters */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Review Developmental Milestones</h1>
          <p className="text-xs text-slate-400 mt-1">Review behaviors aligned with evidence-based clinician criteria to populate the status matrix.</p>
        </div>
        <div className="flex gap-2">
          {ageRanges.map((range, index) => (
            <button key={range} className={`px-4 py-2 text-xs font-semibold rounded-xl border transition-all ${index === 0 ? "bg-indigo-500/10 text-indigo-400 border-indigo-500/30 shadow-lg" : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-300"}`}>
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Domain Grid list */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {domains.map((domain) => (
          <div key={domain.name} className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-6">
            {/* Domain Header */}
            <div className="flex items-center gap-3 pb-3 border-b border-slate-800">
              <span className="text-2xl">{domain.icon}</span>
              <h2 className="font-bold text-slate-200">{domain.name}</h2>
            </div>

            {/* Milestones list */}
            <div className="space-y-4">
              {domain.items.map((milestone) => (
                <div key={milestone.id} className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-3 hover:border-slate-700/60 transition-colors">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-200">{milestone.title}</h3>
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed">{milestone.description}</p>
                  </div>

                  {/* Evidence Source footer */}
                  <div className="text-[10px] text-slate-500 font-mono italic">
                    Source: {milestone.source}
                  </div>

                  {/* Action Selector */}
                  <div className="flex items-center justify-between pt-1 border-t border-slate-900">
                    <span className="text-[10px] uppercase font-bold text-slate-500">{milestone.range}</span>
                    <select defaultValue={milestone.status} className="bg-slate-900 border border-slate-800 text-xs rounded-lg px-2.5 py-1 text-slate-300 outline-none focus:border-indigo-500">
                      <option value="not_started">⚪ Not Started</option>
                      <option value="in_progress">🟡 In Progress</option>
                      <option value="achieved">🟢 Achieved</option>
                    </select>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
