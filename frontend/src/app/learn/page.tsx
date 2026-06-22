"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useActiveChild } from "@/components/ActiveChildContext";
import { API_BASE_URL } from "@/config";
import {
  BookOpen,
  Award,
  Clock,
  Heart,
  Sparkles,
  ArrowRight,
  ChevronRight,
  Search,
  CheckCircle,
  HelpCircle,
  AlertCircle,
  Activity,
  Plus,
  BookMarked,
  X,
  MessageSquare
} from "lucide-react";

interface ActivityItem {
  id: string;
  title: string;
  summary: string;
  duration_minutes: number;
  materials: string[];
  instructions: string[];
  why_recommended: string;
  personalization_reasons?: string[];
}

interface GuideItem {
  id: string;
  title: string;
  summary: string;
  reading_time: number;
  body_markdown: string;
  why_recommended: string;
  personalization_reasons?: string[];
}

interface QuestionItem {
  id: string;
  question: string;
  follow_up_prompt: string;
}

interface ChildProfile {
  age_months: number;
  strong_domains: string[];
  underrepresented_domains: string[];
  recent_focus_themes: string[];
  persistent_concerns: string[];
  visit_discussion_topics: string[];
  growth_signals: string[];
}

interface Recommendations {
  child_profile: ChildProfile;
  activities: ActivityItem[];
  guides: GuideItem[];
  question: QuestionItem | null;
  next_observations: string[];
}

const STATIC_TOPICS = [
  {
    title: "Communication",
    description: "Building pre-verbal sounds, pointing gestures, turn-taking eye gaze, and vocabulary.",
    color: "bg-indigo-50 border-indigo-200 text-indigo-700 hover:bg-indigo-100/70"
  },
  {
    title: "Play",
    description: "Developing pretend play, stacking blocks, exploratory object manipulation, and social play.",
    color: "bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100/70"
  },
  {
    title: "Social Development",
    description: "Understanding shared attention, pointing to show interest, and responding to emotional cues.",
    color: "bg-rose-50 border-rose-200 text-rose-700 hover:bg-rose-100/70"
  },
  {
    title: "Motor Skills",
    description: "Fine motor grasp, finger isolation, block building, balance coordination, and walking milestones.",
    color: "bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100/70"
  },
  {
    title: "Preparing For Visits",
    description: "Compiling milestones, identifying tracking gaps, organizing concerns, and compiling doctor checklists.",
    color: "bg-teal-50 border-teal-200 text-teal-700 hover:bg-teal-100/70"
  },
  {
    title: "Milestones Guide",
    description: "Understanding chronological milestones, developmental windows, and observational tracking logic.",
    color: "bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100/70"
  }
];

export default function LearnPage() {
  const { activeChild, loading: contextLoading, fetchWithAuth } = useActiveChild();
  const [recs, setRecs] = useState<Recommendations | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedGuide, setSelectedGuide] = useState<GuideItem | null>(null);
  const [selectedActivity, setSelectedActivity] = useState<ActivityItem | null>(null);
  const [learningPath, setLearningPath] = useState<any | null>(null);
  const [learningPathLoading, setLearningPathLoading] = useState(true);

  const apiUrl = API_BASE_URL;

  const fetchRecommendations = useCallback(async () => {
    if (!activeChild) return;
    setLoading(true);
    try {
      const res = await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/recommendations`);
      if (res.ok) {
        const data = await res.json();
        setRecs(data);
      }
    } catch (err) {
      console.error("Error fetching recommendations:", err);
    } finally {
      setLoading(false);
    }
  }, [activeChild, apiUrl, fetchWithAuth]);

  const fetchLearningPath = useCallback(async () => {
    if (!activeChild) return;
    setLearningPathLoading(true);
    try {
      const res = await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/learning-path`);
      if (res.ok) {
        const data = await res.json();
        setLearningPath(data);
      }
    } catch (err) {
      console.error("Error fetching learning path:", err);
    } finally {
      setLearningPathLoading(false);
    }
  }, [activeChild, apiUrl, fetchWithAuth]);

  useEffect(() => {
    fetchRecommendations();
    fetchLearningPath();
  }, [fetchRecommendations, fetchLearningPath]);

  const handleViewWeekActivity = (weekActivity: { id: string; title: string; summary: string }) => {
    const fullAct = recs?.activities.find(a => a.id === weekActivity.id);
    if (fullAct) {
      setSelectedActivity(fullAct);
    } else {
      setSelectedActivity({
        id: weekActivity.id,
        title: weekActivity.title,
        summary: weekActivity.summary,
        duration_minutes: 15,
        materials: ["No special materials required"],
        instructions: [
          "Incorporate this activity goal into your daily play sessions.",
          "Practice consistently for 10-15 minutes.",
          "Observe your child's responses and log them in the journal."
        ],
        why_recommended: `To support development in the target skill.`
      });
    }
  };


  if (contextLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-660"></div>
      </div>
    );
  }

  if (!activeChild) {
    return (
      <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl text-center max-w-lg mx-auto mt-12 space-y-4">
        <h2 className="text-2xl font-bold text-slate-50">Select a Profile to Access Learning Hub</h2>
        <p className="text-base text-slate-350">Choose a child profile to retrieve personalized guide recommendations and play challenges.</p>
        <Link href="/children" className="inline-block px-5 py-2.5 bg-indigo-650 hover:bg-indigo-700 text-white font-semibold text-base rounded-xl transition-all">
          Manage Profiles
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-10 py-8 px-4 sm:px-6">
      
      {/* HEADER HERO */}
      <div className="border-b border-slate-800 pb-6 space-y-2">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-50">Parent Learning Hub</h1>
        <p className="text-base text-slate-350 font-semibold">
          Personalized guides, age-relevant home activities, and expert tips tailored to {activeChild.first_name}'s developmental journey.
        </p>
      </div>

      {/* 4-WEEK GROWTH JOURNEY PLAN */}
      {learningPathLoading ? (
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl animate-pulse space-y-4">
          <div className="h-6 bg-slate-800 rounded w-1/4"></div>
          <div className="h-4 bg-slate-800 rounded w-3/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-slate-850 rounded-2xl"></div>
            ))}
          </div>
        </div>
      ) : learningPath ? (
        <div className="bg-slate-900 border border-slate-800 p-6 sm:p-8 rounded-3xl space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="inline-flex items-center gap-1 text-[10px] font-bold text-indigo-400 bg-indigo-950/50 border border-indigo-900/60 px-2 py-0.5 rounded uppercase tracking-wider">
                  4-Week Growth Journey Plan
                </span>
                <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-950/50 border border-emerald-900/60 px-2 py-0.5 rounded uppercase tracking-wider">
                  {learningPath.domain.replace("_", " ")}
                </span>
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-100 pt-1">
                Focus Skill: {learningPath.target_skill_title || learningPath.target_skill.replace(/_/g, " ").split(" ").map((w: string) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(" ")}
              </h2>
              <p className="text-sm text-slate-350 font-semibold leading-relaxed">
                <strong>Why this focus:</strong> {learningPath.why_this_goal}
              </p>
            </div>
            {learningPath.current_evidence && (
              <div className="bg-slate-850 border border-slate-800 p-4 rounded-2xl max-w-sm shrink-0">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Current Status</span>
                <p className="text-xs text-slate-300 italic font-semibold leading-relaxed mt-1">
                  "{learningPath.current_evidence}"
                </p>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {learningPath.weeks.map((weekItem: any) => (
              <div
                key={weekItem.week}
                className="bg-slate-850 border border-slate-800/80 p-5 rounded-2xl flex flex-col justify-between hover:border-slate-700 transition-all relative overflow-hidden group"
              >
                {/* Visual Accent */}
                <div className="absolute top-0 left-0 w-full h-1 bg-indigo-600/40 group-hover:bg-indigo-500 transition-colors"></div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest">
                      Week {weekItem.week}
                    </span>
                  </div>
                  
                  <div className="space-y-1">
                    <h3 className="text-sm font-bold text-slate-150 leading-tight">
                      {weekItem.title}
                    </h3>
                    <p className="text-[11px] text-slate-400 leading-relaxed font-semibold">
                      {weekItem.goal}
                    </p>
                  </div>
                  
                  {weekItem.activity && (
                    <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl space-y-1">
                      <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">Play Session</span>
                      <h4 className="text-xs font-bold text-slate-200 line-clamp-1">
                        {weekItem.activity.title}
                      </h4>
                      <p className="text-[10px] text-slate-400 line-clamp-2 leading-snug">
                        {weekItem.activity.summary}
                      </p>
                      <button
                        onClick={() => handleViewWeekActivity(weekItem.activity)}
                        className="text-[10px] font-bold text-indigo-400 hover:text-indigo-300 transition-colors pt-1.5 flex items-center gap-0.5 cursor-pointer bg-transparent border-none p-0 align-baseline"
                      >
                        Play Guide <ChevronRight className="h-3 w-3" />
                      </button>
                    </div>
                  )}

                  <div className="text-[11px] text-slate-350 space-y-2 pt-1 font-semibold leading-relaxed border-t border-slate-800/50">
                    <p>
                      <strong className="text-slate-450 block uppercase text-[9px] tracking-wider mb-0.5">Observe:</strong> 
                      {weekItem.watch_for}
                    </p>
                    <p className="text-indigo-350">
                      <strong className="text-indigo-450 block uppercase text-[9px] tracking-wider mb-0.5">Record:</strong> 
                      {weekItem.what_to_log}
                    </p>
                  </div>
                </div>

                <div className="pt-5 mt-auto">
                  <Link
                    href={`/observations?body=${encodeURIComponent(`[Week ${weekItem.week} Focus Skill: ${learningPath.target_skill_title || learningPath.target_skill.replace("_", " ")}] We noticed: `)}`}
                    className="w-full py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 hover:text-indigo-400 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-1"
                  >
                    <Plus className="h-3.5 w-3.5" /> Log Progress
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-660"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          
          {/* MAIN COLUMN */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* 1. RECOMMENDED ACTIVITIES */}
            <div className="space-y-4">
              <h2 className="text-2xl font-extrabold text-slate-50 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-500" /> Recommended For {activeChild.first_name} This Week
              </h2>
              {recs && recs.activities.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {recs.activities.map((act) => (
                    <div
                      key={act.id}
                      className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between hover:border-slate-700 hover:shadow-xs transition-all"
                    >
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="inline-flex items-center gap-1 text-xs font-bold text-indigo-400 bg-indigo-950/50 border border-indigo-900/60 px-2.5 py-1 rounded-md">
                            <Clock className="h-3 w-3" /> {act.duration_minutes} min play
                          </span>
                          <span className="text-xs text-slate-400 bg-slate-800 border border-slate-750 px-2 py-0.5 rounded">
                            Activity
                          </span>
                        </div>
                        <h3 className="text-lg font-bold text-slate-100">{act.title}</h3>
                        <p className="text-sm text-slate-350 leading-relaxed font-semibold">
                          {act.summary}
                        </p>
                        <p className="text-xs text-indigo-400 italic bg-indigo-950/20 border border-indigo-950/40 p-2.5 rounded-lg leading-relaxed">
                          {act.why_recommended}
                        </p>
                        {act.personalization_reasons && act.personalization_reasons.length > 0 && (
                          <div className="pt-2 flex flex-wrap gap-1.5 items-center">
                            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Triggers:</span>
                            {act.personalization_reasons.map((reason: string, idx: number) => (
                              <span key={idx} className="text-[10px] font-bold text-indigo-300 bg-indigo-955/40 border border-indigo-900/50 px-2 py-0.5 rounded">
                                {reason}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => setSelectedActivity(act)}
                        className="mt-5 w-full py-2.5 bg-slate-800 hover:bg-slate-750 text-slate-100 hover:text-indigo-400 text-sm font-bold border border-slate-750 rounded-xl transition-all cursor-pointer flex items-center justify-center gap-1.5"
                      >
                        Show Play Guide <ChevronRight className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-center italic text-slate-350">
                  No activity suggestions compiled. Log more moments to customize suggestions.
                </div>
              )}
            </div>

            {/* 2. HELPFUL GUIDES */}
            <div className="space-y-4">
              <h2 className="text-2xl font-extrabold text-slate-50 flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-emerald-500" /> Helpful Guides
              </h2>
              {recs && recs.guides.length > 0 ? (
                <div className="space-y-4">
                  {recs.guides.map((guide) => (
                    <div
                      key={guide.id}
                      className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-700 transition-all"
                    >
                      <div className="space-y-2 max-w-xl">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-emerald-400 bg-emerald-950/50 border border-emerald-900/60 px-2.5 py-1 rounded-md">
                            {guide.reading_time} min read
                          </span>
                          <span className="text-xs text-slate-400 bg-slate-800 border border-slate-750 px-2.5 py-0.5 rounded">
                            Article
                          </span>
                        </div>
                        <h3 className="text-lg font-bold text-slate-100">{guide.title}</h3>
                        <p className="text-sm text-slate-350 leading-relaxed font-semibold">
                          {guide.summary}
                        </p>
                        <p className="text-xs text-emerald-400 font-semibold italic">
                          {guide.why_recommended}
                        </p>
                        {guide.personalization_reasons && guide.personalization_reasons.length > 0 && (
                          <div className="pt-2 flex flex-wrap gap-1.5 items-center">
                            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Triggers:</span>
                            {guide.personalization_reasons.map((reason: string, idx: number) => (
                              <span key={idx} className="text-[10px] font-bold text-emerald-300 bg-emerald-955/40 border border-emerald-900/50 px-2 py-0.5 rounded">
                                {reason}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => setSelectedGuide(guide)}
                        className="py-2.5 px-5 bg-indigo-650 hover:bg-indigo-700 text-white font-bold text-sm rounded-xl transition-all cursor-pointer shrink-0"
                      >
                        Read Article
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-center italic text-slate-350">
                  No educational guide articles match your child's age profile.
                </div>
              )}
            </div>

            {/* 5. TOPIC BROWSER */}
            <div className="space-y-4">
              <h2 className="text-2xl font-extrabold text-slate-50 flex items-center gap-2">
                <BookMarked className="h-5 w-5 text-indigo-400" /> Browse Development Topics
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {STATIC_TOPICS.map((topic, idx) => (
                  <div
                    key={idx}
                    className="p-5 border border-slate-800 bg-slate-900 rounded-2xl space-y-2 hover:border-slate-700 transition-all flex flex-col justify-between"
                  >
                    <div className="space-y-1">
                      <h3 className="text-base font-bold text-slate-150">{topic.title}</h3>
                      <p className="text-xs text-slate-350 leading-relaxed font-medium">{topic.description}</p>
                    </div>
                    <div className="pt-3 flex justify-start">
                      <span className="text-xs font-bold text-indigo-500 hover:text-indigo-400 transition-colors inline-flex items-center gap-1 cursor-pointer">
                        Explore topic <ChevronRight className="h-3 w-3" />
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* SIDEBAR COLUMN */}
          <div className="space-y-8">
            
            {/* 3. THINGS TO WATCH FOR */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl space-y-4">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Award className="h-5 w-5 text-amber-500" /> Things To Watch For
              </h2>
              <p className="text-xs text-slate-350 leading-relaxed font-medium">
                Keep an eye out for these behaviors during playtime or daily care. When you observe them, log a quick moment in the journal.
              </p>
              
              {recs && recs.next_observations.length > 0 ? (
                <div className="space-y-3 pt-2">
                  {recs.next_observations.map((item, idx) => (
                    <div key={idx} className="p-3 bg-slate-850 border border-slate-800 rounded-xl flex items-start gap-2.5">
                      <CheckCircle className="h-4.5 w-4.5 text-slate-500 mt-0.5 shrink-0" />
                      <div className="space-y-1.5">
                        <p className="text-xs font-bold text-slate-150 leading-tight">{item}</p>
                        <Link
                          href={`/observations?prompt=${encodeURIComponent(`We observed: ${item}`)}`}
                          className="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-0.5"
                        >
                          <Plus className="h-3.5 w-3.5" /> Log in journal
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">No checklist items queued for this age band.</p>
              )}
            </div>

            {/* 4. UPCOMING SKILLS (PLURAL DEVELOPMENT INFO) */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl space-y-4">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Activity className="h-5 w-5 text-rose-500" /> Upcoming Developmental Steps
              </h2>
              <p className="text-xs text-slate-350 leading-relaxed font-medium">
                Children develop at their own pace within wide windows. Here are normal next steps you may notice:
              </p>
              <div className="space-y-3 pt-2">
                <div className="p-3 bg-slate-850 border border-slate-800 rounded-xl space-y-1">
                  <h4 className="text-xs font-bold text-slate-150">Expressive Communication</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Moving from single words to simple two-word word structures ('more milk', 'big ball') and pointing to direct your focus.
                  </p>
                </div>
                <div className="p-3 bg-slate-850 border border-slate-800 rounded-xl space-y-1">
                  <h4 className="text-xs font-bold text-slate-150">Cooperative Social Play</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Enjoying building structures together, passing items back and forth, and coordinating intentions during play.
                  </p>
                </div>
              </div>
            </div>

          </div>

        </div>
      )}

      {/* ACTIVITY MODAL */}
      {selectedActivity && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-xs">
          <div className="bg-slate-900 border border-slate-800 max-w-lg w-full max-h-[85vh] overflow-y-auto rounded-3xl shadow-xl flex flex-col justify-between">
            <div className="p-6 space-y-6">
              {/* Header */}
              <div className="flex justify-between items-start gap-4">
                <div className="space-y-1">
                  <span className="text-xs text-indigo-400 font-bold bg-indigo-950 border border-indigo-900/60 px-2.5 py-1 rounded-md">
                    {selectedActivity.duration_minutes} min challenge
                  </span>
                  <h3 className="text-xl font-bold text-slate-100 pt-1">{selectedActivity.title}</h3>
                </div>
                <button
                  onClick={() => setSelectedActivity(null)}
                  className="p-1 text-slate-400 hover:text-slate-200 bg-slate-850 rounded-lg cursor-pointer"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Instructions */}
              <div className="space-y-4">
                {selectedActivity.materials.length > 0 && (
                  <div className="space-y-1">
                    <h4 className="text-xs font-semibold text-slate-350 uppercase tracking-wider">Materials needed:</h4>
                    <p className="text-sm text-slate-150 font-bold">{selectedActivity.materials.join(", ")}</p>
                  </div>
                )}

                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-350 uppercase tracking-wider">Instructions:</h4>
                  <ol className="list-decimal list-inside space-y-2 text-sm text-slate-100 leading-relaxed">
                    {selectedActivity.instructions.map((step, idx) => (
                      <li key={idx} className="pl-1">
                        <span className="font-bold">{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>

                <div className="p-4 bg-indigo-950/20 border border-indigo-900/40 rounded-xl space-y-1">
                  <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Why it helps:</h4>
                  <p className="text-xs text-slate-200 leading-relaxed font-semibold">
                    {selectedActivity.why_recommended}
                  </p>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-slate-800 p-5 bg-slate-855 flex justify-end gap-3 rounded-b-3xl">
              <button
                onClick={() => setSelectedActivity(null)}
                className="px-5 py-2.5 bg-slate-800 hover:bg-slate-750 text-slate-150 font-bold text-sm rounded-xl border border-slate-750 cursor-pointer"
              >
                Close
              </button>
              <Link
                href={`/observations?body=${encodeURIComponent(`Completed the ${selectedActivity.title} play game. Note child's response:`)}`}
                onClick={() => setSelectedActivity(null)}
                className="px-5 py-2.5 bg-indigo-650 hover:bg-indigo-700 text-white font-bold text-sm rounded-xl cursor-pointer"
              >
                Log Completion
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* GUIDE MODAL */}
      {selectedGuide && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-xs">
          <div className="bg-slate-900 border border-slate-800 max-w-2xl w-full max-h-[85vh] overflow-y-auto rounded-3xl shadow-xl flex flex-col justify-between">
            <div className="p-6 space-y-6">
              {/* Header */}
              <div className="flex justify-between items-start gap-4">
                <div className="space-y-1">
                  <span className="text-xs text-emerald-400 font-bold bg-emerald-950 border border-emerald-900/60 px-2.5 py-1 rounded-md">
                    {selectedGuide.reading_time} min read
                  </span>
                  <h3 className="text-xl font-bold text-slate-100 pt-1">{selectedGuide.title}</h3>
                </div>
                <button
                  onClick={() => setSelectedGuide(null)}
                  className="p-1 text-slate-400 hover:text-slate-200 bg-slate-850 rounded-lg cursor-pointer"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Body Content */}
              <div className="prose prose-slate max-w-none text-slate-100">
                <div className="p-4 bg-slate-850 border border-slate-800 rounded-xl text-xs text-slate-350 leading-relaxed font-semibold italic">
                  {selectedGuide.why_recommended}
                </div>
                <div className="mt-4 font-serif text-base leading-relaxed whitespace-pre-line space-y-4">
                  {selectedGuide.body_markdown.split("\n\n").map((para, idx) => {
                    if (para.startsWith("###")) {
                      return <h4 key={idx} className="text-lg font-bold text-slate-50 pt-2">{para.replace("###", "").trim()}</h4>;
                    } else if (para.startsWith("-")) {
                      return (
                        <ul key={idx} className="list-disc list-inside space-y-1.5 font-sans text-sm pl-2">
                          {para.split("\n").map((li, lidx) => (
                            <li key={lidx}>{li.replace("-", "").trim()}</li>
                          ))}
                        </ul>
                      );
                    }
                    return <p key={idx} className="text-slate-200">{para}</p>;
                  })}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-slate-800 p-5 bg-slate-855 flex justify-end rounded-b-3xl">
              <button
                onClick={() => setSelectedGuide(null)}
                className="px-5 py-2.5 bg-slate-800 hover:bg-slate-750 text-slate-150 font-bold text-sm rounded-xl border border-slate-750 cursor-pointer"
              >
                Done Reading
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
