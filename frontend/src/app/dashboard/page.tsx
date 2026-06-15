"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useActiveChild } from "@/components/ActiveChildContext";
import { 
  Sparkles, 
  Calendar, 
  ArrowRight,
  Heart,
  Plus,
  Compass,
  TrendingUp,
  HelpCircle,
  Clock,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  MessageSquare,
  BookOpen,
  Award,
  CheckCircle,
  X
} from "lucide-react";

interface Snapshot {
  child_name: string;
  age_months: number;
  tracking_start_date: string;
  most_observed_area: string;
  growth_highlight: string;
  watch_item: string;
  next_appointment: string;
}

interface GrowthStory {
  title: string;
  story: string;
  word_count: number;
}

interface Observation {
  id: string;
  body: string;
  notes?: string;
  observed_at: string;
  entry_type: "general" | "concern" | "milestone";
  domain_id: number | null;
}

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

interface Recommendations {
  child_profile: any;
  activities: ActivityItem[];
  guides: GuideItem[];
  question: QuestionItem | null;
  next_observations: string[];
}

interface TimelineEvent {
  id: string;
  type: string;
  date: string;
  title: string;
  description: string;
  metadata: {
    domain?: string;
    location?: string;
    observer_relation?: string;
    quality_score?: number;
    age_range?: string;
    notes?: string;
    activity_id?: string;
    attempted?: boolean;
    completed?: boolean;
    observed_change?: string;
    clinician_name?: string;
    priority?: string;
    concern_level?: string;
    recommendation_id?: string;
    type?: string;
    helpful?: boolean;
    is_first?: boolean;
  };
}

export default function Dashboard() {
  const { activeChild, loading: contextLoading, fetchWithAuth } = useActiveChild();

  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [growthStory, setGrowthStory] = useState<GrowthStory | null>(null);
  const [changes, setChanges] = useState<string[]>([]);
  const [questions, setQuestions] = useState<string[]>([]);
  const [recentObservations, setRecentObservations] = useState<Observation[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  
  const [loadingData, setLoadingData] = useState(true);
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(null);
  
  const [recs, setRecs] = useState<Recommendations | null>(null);
  const [selectedGuide, setSelectedGuide] = useState<GuideItem | null>(null);
  const [selectedActivity, setSelectedActivity] = useState<ActivityItem | null>(null);

  // Closed-loop activity outcome state
  const [outcomeAttempted, setOutcomeAttempted] = useState(true);
  const [outcomeCompleted, setOutcomeCompleted] = useState(true);
  const [outcomeNotes, setOutcomeNotes] = useState("");
  const [outcomeChange, setOutcomeChange] = useState("");
  const [outcomeSubmitting, setOutcomeSubmitting] = useState(false);
  const [showOutcomeForm, setShowOutcomeForm] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchDashboardData = useCallback(async () => {
    if (!activeChild) return;
    setLoadingData(true);
    try {
      // 1. Fetch child snapshot
      const snapRes = await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/snapshot`);
      const snapData = snapRes.ok ? await snapRes.json() : null;
      setSnapshot(snapData);

      // 2. Fetch growth story
      const storyRes = await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/growth-story`);
      const storyData = storyRes.ok ? await storyRes.json() : null;
      setGrowthStory(storyData);

      // 3. Fetch monthly change summary
      const changeRes = await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/monthly-change`);
      const changeData = changeRes.ok ? await changeRes.json() : [];
      setChanges(changeData);

      // 4. Fetch monthly questions
      const qRes = await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/monthly-questions`);
      const qData = qRes.ok ? await qRes.json() : [];
      setQuestions(qData);

      // Fetch recommendations
      const recsRes = await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/recommendations`);
      const recsData = recsRes.ok ? await recsRes.json() : null;
      setRecs(recsData);

      // 5. Fetch recent observations
      const obsRes = await fetchWithAuth(`${apiUrl}/children/${activeChild.id}/observations`);
      const obsData = obsRes.ok ? await obsRes.json() : [];
      setRecentObservations(obsData.slice(0, 3));

      // 6. Fetch companion timeline
      const timelineRes = await fetchWithAuth(`${apiUrl}/insights/${activeChild.id}/companion-timeline`);
      const timelineData = timelineRes.ok ? await timelineRes.json() : [];
      setTimeline(timelineData);
    } catch (err) {
      console.error("Error fetching dashboard details:", err);
    } finally {
      setLoadingData(false);
    }
  }, [activeChild, apiUrl, fetchWithAuth]);

  // Click & acceptance trackers
  const logRecommendationClick = async (recId: string, recType: string) => {
    if (!activeChild) return;
    try {
      await fetchWithAuth(`${apiUrl}/recommendations/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          child_id: activeChild.id,
          recommendation_id: recId,
          recommendation_type: recType,
          opened: true
        })
      });
      fetchDashboardData();
    } catch (err) {
      console.error("Error logging rec click:", err);
    }
  };

  const logRecommendationHelpful = async (recId: string, recType: string, helpful: boolean) => {
    if (!activeChild) return;
    try {
      await fetchWithAuth(`${apiUrl}/recommendations/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          child_id: activeChild.id,
          recommendation_id: recId,
          recommendation_type: recType,
          helpful: helpful
        })
      });
      alert("Thank you for your feedback!");
    } catch (err) {
      console.error("Error logging helpfulness:", err);
    }
  };

  const handleOutcomeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeChild || !selectedActivity) return;
    setOutcomeSubmitting(true);
    try {
      const res = await fetchWithAuth(`${apiUrl}/recommendations/activity-outcomes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          child_id: activeChild.id,
          activity_id: selectedActivity.id,
          attempted: outcomeAttempted,
          completed: outcomeCompleted,
          parent_notes: outcomeNotes,
          observed_change: outcomeChange
        })
      });
      if (res.ok) {
        // Mark recommendation as completed
        await fetchWithAuth(`${apiUrl}/recommendations/feedback`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            child_id: activeChild.id,
            recommendation_id: selectedActivity.id,
            recommendation_type: "activity",
            completed: outcomeCompleted
          })
        });

        // Reset
        setOutcomeNotes("");
        setOutcomeChange("");
        setShowOutcomeForm(false);
        setSelectedActivity(null);
        fetchDashboardData();
      }
    } catch (err) {
      console.error("Error submitting outcome:", err);
    } finally {
      setOutcomeSubmitting(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (contextLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-650"></div>
      </div>
    );
  }

  if (!activeChild) {
    return (
      <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl text-center max-w-lg mx-auto mt-12 space-y-4 shadow-sm">
        <h2 className="text-2xl font-bold text-slate-50">No Child Profile Selected</h2>
        <p className="text-base text-slate-350">Please make sure you have added a child profile to get started.</p>
        <Link href="/children" className="inline-block mt-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-650 text-white font-semibold text-base rounded-xl transition-all">
          Manage Profiles
        </Link>
      </div>
    );
  }

  const getDomainName = (domainId: number | null) => {
    if (!domainId) return "General";
    switch (domainId) {
      case 1: return "Communication";
      case 2: return "Movement";
      case 3: return "Hands & Fingers";
      case 4: return "Feelings & Friendships";
      case 5: return "Thinking & Learning";
      default: return "Daily Activities";
    }
  };

  const getArrowIcon = (text: string) => {
    if (text.startsWith("↑")) {
      return <span className="text-emerald-600 font-bold mr-2">↑</span>;
    } else if (text.startsWith("↓")) {
      return <span className="text-rose-600 font-bold mr-2">↓</span>;
    } else {
      return <span className="text-slate-300 font-bold mr-2">→</span>;
    }
  };

  const cleanChangeText = (text: string) => {
    if (text.startsWith("↑") || text.startsWith("↓") || text.startsWith("→")) {
      return text.slice(1).trim();
    }
    return text;
  };

  const formattedStartDate = snapshot?.tracking_start_date 
    ? new Date(snapshot.tracking_start_date).toLocaleDateString("en-US", { month: "short", year: "numeric" })
    : "";

  return (
    <div className="max-w-6xl mx-auto space-y-8 py-8 px-4 sm:px-6">
      
      {/* 1. CHILD SNAPSHOT HERO SECTION */}
      {snapshot && (
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl shadow-sm space-y-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
            <div className="text-left">
              <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-50 leading-tight">
                {snapshot.child_name}
              </h1>
              <p className="text-base text-slate-350 font-semibold mt-1">
                {snapshot.age_months} months old &bull; Tracking since {formattedStartDate}
              </p>
            </div>
            {/* Quick CTAs */}
            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/observations"
                className="px-5 py-3 bg-indigo-600 hover:bg-indigo-650 text-white font-bold text-sm rounded-xl transition-all flex items-center gap-2 shadow-xs cursor-pointer"
              >
                <Plus className="h-4 w-4" /> Add Today's Moment
              </Link>
              <Link
                href="/milestones"
                className="px-5 py-3 border border-slate-750 bg-slate-850 hover:bg-slate-800 text-slate-100 font-bold text-sm rounded-xl transition-all flex items-center gap-2 cursor-pointer"
              >
                <Compass className="h-4 w-4" /> Growth Journey
              </Link>
            </div>
          </div>

          {/* Snapshot Stats/Highlights Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-350 uppercase tracking-wider block">Most Observed Area</span>
              <p className="text-lg font-bold text-indigo-600">{snapshot.most_observed_area}</p>
            </div>

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-350 uppercase tracking-wider block">Recent Growth Highlight</span>
              <p className="text-lg font-bold text-slate-100 leading-snug">{snapshot.growth_highlight}</p>
            </div>

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-350 uppercase tracking-wider block">Current Watch Item</span>
              <p className="text-lg font-bold text-slate-100 leading-snug">{snapshot.watch_item}</p>
            </div>

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-350 uppercase tracking-wider block">Next Appointment</span>
              <p className="text-lg font-bold text-slate-100">{snapshot.next_appointment}</p>
            </div>
          </div>
        </div>
      )}
      {loadingData ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-650"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* LEFT & CENTER COLUMN: COMPANION TIMELINE */}
          <div className="lg:col-span-2 space-y-8">
            
            <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl shadow-sm space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-rose-950/20 border border-rose-900/60 rounded-xl text-rose-455 shrink-0">
                    <Heart className="h-6 w-6 text-rose-400" />
                  </div>
                  <div className="text-left">
                    <h2 className="text-2xl font-extrabold text-slate-50">
                      This Month with {snapshot?.child_name ? snapshot.child_name.split(" ")[0] : "Your Child"}
                    </h2>
                    <p className="text-sm text-slate-350">A developmental narrative compiled from your recent moments.</p>
                  </div>
                </div>
              </div>

              {/* Chronological Timeline */}
              {timeline.length > 0 ? (
                <div className="relative pl-6 border-l border-slate-800 space-y-8 text-left">
                  {timeline.map((event) => {
                    const dateStr = new Date(event.date).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    });
                    
                    let badgeClass = "bg-slate-800/40 text-slate-300 border border-slate-800";
                    let typeLabel = "Moment";
                    let IconComponent = MessageSquare;

                    if (event.type === "achievement") {
                      badgeClass = "bg-emerald-50 text-emerald-700 border border-emerald-250";
                      typeLabel = "First Milestone";
                      IconComponent = Award;
                    } else if (event.type === "milestone") {
                      badgeClass = "bg-emerald-50 text-emerald-700 border border-emerald-250";
                      typeLabel = "Milestone";
                      IconComponent = CheckCircle;
                    } else if (event.type === "concern") {
                      badgeClass = "bg-rose-50 text-rose-700 border border-rose-250";
                      typeLabel = "Concern Thread";
                      IconComponent = AlertCircle;
                    } else if (event.type === "activity_attempt") {
                      badgeClass = "bg-amber-50 text-amber-700 border border-amber-250";
                      typeLabel = "Activity Play";
                      IconComponent = Compass;
                    } else if (event.type === "visit") {
                      badgeClass = "bg-indigo-50 text-indigo-700 border border-indigo-250";
                      typeLabel = "Pediatrician Visit";
                      IconComponent = Calendar;
                    } else if (event.type === "recommendation_accepted") {
                      badgeClass = "bg-indigo-50 text-indigo-700 border border-indigo-250";
                      typeLabel = "Accepted Advice";
                      IconComponent = BookOpen;
                    }

                    return (
                      <div key={event.id} className="relative space-y-2 group">
                        {/* Dot anchor */}
                        <div className="absolute -left-[32px] mt-1.5 p-1 bg-slate-900 border border-slate-800 rounded-full group-hover:border-slate-700 transition-colors">
                          <IconComponent className="h-3.5 w-3.5 text-slate-350" />
                        </div>
                        
                        <div className="bg-slate-850 border border-slate-800 p-5 rounded-2xl space-y-3 shadow-xs hover:border-slate-700 transition-all">
                          <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                              <span className={`px-2.5 py-0.5 text-xs font-bold rounded-md border ${badgeClass}`}>
                                {typeLabel}
                              </span>
                              {event.metadata.domain && (
                                <span className="text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded font-semibold">
                                  {event.metadata.domain}
                                </span>
                              )}
                            </div>
                            <span className="text-xs text-slate-350 font-bold">{dateStr}</span>
                          </div>

                          <h3 className="text-base font-bold text-slate-100">{event.title}</h3>
                          <p className="text-sm text-slate-200 leading-relaxed font-semibold">
                            {event.description}
                          </p>

                          {/* Extra Tags */}
                          {(event.metadata.location || event.metadata.observer_relation || event.metadata.observed_change) && (
                            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800">
                              {event.metadata.location && (
                                <span className="text-xs text-slate-350 bg-slate-800/50 px-2.5 py-1 rounded">
                                  📍 {event.metadata.location}
                                </span>
                              )}
                              {event.metadata.observer_relation && (
                                <span className="text-xs text-slate-350 bg-slate-800/50 px-2.5 py-1 rounded">
                                  👤 {event.metadata.observer_relation}
                                </span>
                              )}
                              {event.metadata.observed_change && (
                                <span className="text-xs text-emerald-400 bg-emerald-950/10 px-2.5 py-1 rounded font-semibold">
                                  🌱 Change noticed: {event.metadata.observed_change}
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-10 bg-slate-850 border border-slate-800 rounded-2xl text-center space-y-4">
                  <p className="text-base text-slate-350 italic font-medium">
                    No timeline moments logged this month yet.
                  </p>
                  <p className="text-sm text-slate-400 max-w-sm mx-auto">
                    Start by writing a brief journal entry or verifying achieved milestones to build your child's developmental story feed.
                  </p>
                  <Link
                    href="/observations"
                    className="inline-block px-5 py-2.5 bg-indigo-600 hover:bg-indigo-650 text-white font-bold text-sm rounded-xl transition-all"
                  >
                    Log Today's Moment
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* RIGHT COLUMN: TRY THIS WEEK & WHAT CHANGED */}
          <div className="space-y-8">
            
            {/* TRY THIS WEEK (RECOMMENDATIONS) SECTION */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl shadow-sm space-y-6 text-left">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-indigo-950/20 border border-indigo-900/60 rounded-xl text-indigo-400 shrink-0">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-xl font-extrabold text-slate-50">Try This Week</h2>
                  <p className="text-xs text-slate-350">Personalized weekly prompts.</p>
                </div>
              </div>

              {recs ? (
                <div className="space-y-5">
                  {/* Card 1: Play Challenge */}
                  <div className="bg-slate-850 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-slate-700 transition-all space-y-3">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-indigo-400">Play Challenge</span>
                        {recs.activities[0] && (
                          <span className="text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded font-bold">
                            {recs.activities[0].duration_minutes}m
                          </span>
                        )}
                      </div>
                      {recs.activities[0] ? (
                        <>
                          <h3 className="text-sm font-bold text-slate-100">{recs.activities[0].title}</h3>
                          <p className="text-xs text-slate-350 leading-relaxed font-semibold">{recs.activities[0].summary}</p>
                          <p className="text-xs text-indigo-400 italic bg-indigo-950/25 p-2 rounded-lg leading-relaxed mt-1 font-semibold">
                            {recs.activities[0].why_recommended}
                          </p>
                          {recs.activities[0].personalization_reasons && recs.activities[0].personalization_reasons.length > 0 && (
                            <div className="pt-1 flex flex-wrap gap-1 items-center">
                              <span className="text-[9px] uppercase font-bold text-slate-500 tracking-wider">Triggers:</span>
                              {recs.activities[0].personalization_reasons.map((reason, idx) => (
                                <span key={idx} className="text-[9px] font-bold text-indigo-300 bg-indigo-955/40 border border-indigo-900/50 px-1.5 py-0.5 rounded">
                                  {reason}
                                </span>
                              ))}
                            </div>
                          )}
                        </>
                      ) : (
                        <p className="text-xs text-slate-400 italic">No activity suggestions available.</p>
                      )}
                    </div>
                    {recs.activities[0] && (
                      <button
                        onClick={() => {
                          logRecommendationClick(recs.activities[0].id, "activity");
                          setSelectedActivity(recs.activities[0]);
                        }}
                        className="w-full py-2 bg-indigo-650 hover:bg-indigo-650 text-white text-xs font-bold rounded-lg transition-colors cursor-pointer"
                      >
                        Try Play Game
                      </button>
                    )}
                  </div>

                  {/* Card 2: Parent Guide */}
                  <div className="bg-slate-850 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-slate-700 transition-all space-y-3">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-emerald-400">Parent Guide</span>
                        {recs.guides[0] && (
                          <span className="text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded font-bold">
                            {recs.guides[0].reading_time}m read
                          </span>
                        )}
                      </div>
                      {recs.guides[0] ? (
                        <>
                          <h3 className="text-sm font-bold text-slate-100">{recs.guides[0].title}</h3>
                          <p className="text-xs text-slate-350 leading-relaxed font-semibold">{recs.guides[0].summary}</p>
                          <p className="text-xs text-emerald-400 italic bg-emerald-950/15 p-2 rounded-lg leading-relaxed mt-1 font-semibold">
                            {recs.guides[0].why_recommended}
                          </p>
                          {recs.guides[0].personalization_reasons && recs.guides[0].personalization_reasons.length > 0 && (
                            <div className="pt-1 flex flex-wrap gap-1 items-center">
                              <span className="text-[9px] uppercase font-bold text-slate-500 tracking-wider">Triggers:</span>
                              {recs.guides[0].personalization_reasons.map((reason, idx) => (
                                <span key={idx} className="text-[9px] font-bold text-emerald-300 bg-emerald-955/40 border border-emerald-900/50 px-1.5 py-0.5 rounded">
                                  {reason}
                                </span>
                              ))}
                            </div>
                          )}
                        </>
                      ) : (
                        <p className="text-xs text-slate-400 italic">No guide suggestions available.</p>
                      )}
                    </div>
                    {recs.guides[0] && (
                      <button
                        onClick={() => {
                          logRecommendationClick(recs.guides[0].id, "guide");
                          setSelectedGuide(recs.guides[0]);
                        }}
                        className="w-full py-2 bg-slate-800 hover:bg-slate-750 text-slate-100 text-xs font-bold rounded-lg border border-slate-750 transition-colors cursor-pointer"
                      >
                        Read Article
                      </button>
                    )}
                  </div>

                  {/* Card 3: Things to Watch For */}
                  <div className="bg-slate-850 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-slate-700 transition-all space-y-3">
                    <div className="space-y-2">
                      <span className="text-xs font-bold text-amber-500 block">Things to Watch For</span>
                      {recs.next_observations && recs.next_observations.length > 0 ? (
                        <>
                          <h3 className="text-sm font-bold text-slate-100">Observe & Log</h3>
                          <p className="text-xs text-slate-350 leading-relaxed font-semibold">
                            Keep an eye out for: <span className="text-slate-200 font-bold">"{recs.next_observations[0]}"</span>
                          </p>
                        </>
                      ) : recs.question ? (
                        <>
                          <h3 className="text-sm font-bold text-slate-100">Observation Prompt</h3>
                          <p className="text-xs text-slate-350 leading-relaxed font-semibold">{recs.question.question}</p>
                        </>
                      ) : (
                        <p className="text-xs text-slate-400 italic">No prompts at this time.</p>
                      )}
                    </div>
                    {recs.next_observations && recs.next_observations.length > 0 ? (
                      <Link
                        href={`/observations?prompt=${encodeURIComponent(`We observed: ${recs.next_observations[0]}`)}`}
                        onClick={() => logRecommendationClick(recs.next_observations[0], "question")}
                        className="w-full py-2 bg-slate-800 hover:bg-slate-750 text-indigo-400 text-xs font-bold rounded-lg border border-slate-750 transition-colors cursor-pointer block text-center"
                      >
                        Log Observation
                      </Link>
                    ) : recs.question ? (
                      <Link
                        href={`/observations?prompt=${encodeURIComponent(recs.question?.question || "")}`}
                        onClick={() => recs.question && logRecommendationClick(recs.question.id, "question")}
                        className="w-full py-2 bg-slate-800 hover:bg-slate-750 text-indigo-400 text-xs font-bold rounded-lg border border-slate-750 transition-colors cursor-pointer block text-center"
                      >
                        Log Observation
                      </Link>
                    ) : null}
                  </div>
                </div>
              ) : (
                <div className="p-6 bg-slate-850 border border-slate-800 rounded-xl text-center">
                  <p className="text-xs text-slate-350 italic">Generating weekly recommendations...</p>
                </div>
              )}
            </div>

            {/* WHAT CHANGED SINCE LAST MONTH SECTION */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl shadow-sm space-y-6 text-left">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-emerald-950/20 border border-emerald-900/60 rounded-xl text-emerald-400 shrink-0">
                  <TrendingUp className="h-5 w-5 text-emerald-400" />
                </div>
                <div>
                  <h2 className="text-xl font-extrabold text-slate-50">What Changed</h2>
                  <p className="text-xs text-slate-350">Comparing logs month-over-month.</p>
                </div>
              </div>

              {changes.length > 0 ? (
                <div className="space-y-3">
                  {changes.map((change, idx) => (
                    <div key={idx} className="flex items-start p-3 bg-slate-850 rounded-xl border border-slate-800">
                      <div className="mt-0.5 shrink-0">
                        {getArrowIcon(change)}
                      </div>
                      <p className="text-xs font-bold text-slate-200">
                        {cleanChangeText(change)}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 bg-slate-850 border border-slate-800 rounded-xl text-center">
                  <p className="text-xs text-slate-350 italic font-semibold">Add more observations to unlock comparisons between months.</p>
                </div>
              )}
            </div>

            {/* MONTHLY GROWTH STORY SUMMARY IN SIDEBAR */}
            {growthStory && (
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl shadow-sm text-left space-y-3">
                <h3 className="text-base font-bold text-rose-455 flex items-center gap-2">
                  <Heart className="h-4 w-4 text-rose-400" /> {growthStory.title}
                </h3>
                <p className="text-xs text-slate-350 font-semibold leading-relaxed font-serif line-clamp-6">
                  "{growthStory.story}"
                </p>
                <button
                  onClick={() => alert(growthStory.story)}
                  className="text-xs text-indigo-400 font-bold hover:underline"
                >
                  Read Full Story
                </button>
              </div>
            )}
            
          </div>
        </div>
      )}

      {/* ACTIVITY PLAY GAME MODAL WITH CLOSED-LOOP OUTCOME TRACKING */}
      {selectedActivity && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-xs">
          <div className="bg-slate-900 border border-slate-800 max-w-lg w-full max-h-[85vh] overflow-y-auto rounded-3xl shadow-xl flex flex-col justify-between text-left">
            {!showOutcomeForm ? (
              /* Play Instructions Pane */
              <div className="p-6 space-y-6">
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

                <div className="space-y-4">
                  {selectedActivity.materials && selectedActivity.materials.length > 0 && (
                    <div className="space-y-1">
                      <h4 className="text-xs font-semibold text-slate-350 uppercase tracking-wider">Materials needed:</h4>
                      <p className="text-sm text-slate-150 font-bold">{selectedActivity.materials.join(", ")}</p>
                    </div>
                  )}

                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-slate-350 uppercase tracking-wider">Instructions:</h4>
                    <ol className="list-decimal list-inside space-y-2 text-sm text-slate-100 leading-relaxed">
                      {selectedActivity.instructions && selectedActivity.instructions.map((step, idx) => (
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

                {/* Footer Buttons */}
                <div className="border-t border-slate-800 pt-4 flex justify-end gap-3">
                  <button
                    onClick={() => setSelectedActivity(null)}
                    className="px-5 py-2.5 bg-slate-800 hover:bg-slate-750 text-slate-150 font-bold text-sm rounded-xl border border-slate-750 cursor-pointer"
                  >
                    Close
                  </button>
                  <button
                    onClick={() => setShowOutcomeForm(true)}
                    className="px-5 py-2.5 bg-indigo-650 hover:bg-indigo-700 text-white font-bold text-sm rounded-xl cursor-pointer"
                  >
                    Log Play Session Outcome
                  </button>
                </div>
              </div>
            ) : (
              /* Success Outcome Form Pane */
              <form onSubmit={handleOutcomeSubmit} className="p-6 space-y-6">
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <h3 className="text-lg font-bold text-slate-100">How did the game go?</h3>
                    <p className="text-xs text-slate-350 mt-1">Record feedback to personalize future weekly activities.</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowOutcomeForm(false)}
                    className="p-1 text-slate-400 hover:text-slate-200 bg-slate-850 rounded-lg cursor-pointer"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <div className="space-y-4">
                  {/* Status checklist */}
                  <div className="flex items-center gap-6">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={outcomeAttempted}
                        onChange={(e) => setOutcomeAttempted(e.target.checked)}
                        className="rounded border-slate-800 text-indigo-600 bg-slate-850 h-4 w-4"
                      />
                      <span className="text-sm text-slate-100 font-bold">We attempted it</span>
                    </label>

                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={outcomeCompleted}
                        onChange={(e) => setOutcomeCompleted(e.target.checked)}
                        className="rounded border-slate-800 text-indigo-600 bg-slate-850 h-4 w-4"
                      />
                      <span className="text-sm text-slate-100 font-bold">We completed it</span>
                    </label>
                  </div>

                  {/* Play notes */}
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-350 uppercase tracking-wider block">Play Notes / Observations</label>
                    <textarea
                      value={outcomeNotes}
                      onChange={(e) => setOutcomeNotes(e.target.value)}
                      placeholder="e.g. He enjoyed the game and pointed three times at the hidden blocks."
                      className="w-full bg-slate-850 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:outline-none focus:border-slate-700 min-h-[70px] font-bold"
                    />
                  </div>

                  {/* Observed behavioral change */}
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-350 uppercase tracking-wider block">Observed behavioral change</label>
                    <textarea
                      value={outcomeChange}
                      onChange={(e) => setOutcomeChange(e.target.value)}
                      placeholder="e.g. Showed more direct joint attention and looked back at me to celebrate."
                      className="w-full bg-slate-850 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:outline-none focus:border-slate-700 min-h-[70px] font-bold"
                    />
                  </div>
                </div>

                <div className="border-t border-slate-800 pt-4 flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setShowOutcomeForm(false)}
                    className="px-5 py-2.5 bg-slate-800 hover:bg-slate-750 text-slate-150 font-bold text-sm rounded-xl border border-slate-750 cursor-pointer"
                  >
                    Back to Instructions
                  </button>
                  <button
                    type="submit"
                    disabled={outcomeSubmitting}
                    className="px-5 py-2.5 bg-indigo-650 hover:bg-indigo-700 text-white font-bold text-sm rounded-xl cursor-pointer disabled:opacity-50"
                  >
                    {outcomeSubmitting ? "Submitting..." : "Save Outcome"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* GUIDE MODAL */}
      {selectedGuide && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-xs">
          <div className="bg-slate-900 border border-slate-800 max-w-2xl w-full max-h-[85vh] overflow-y-auto rounded-3xl shadow-xl flex flex-col justify-between text-left">
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
            <div className="border-t border-slate-800 p-5 bg-slate-855 flex justify-between items-center rounded-b-3xl">
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-350 font-bold">Was this article helpful?</span>
                <button
                  onClick={() => logRecommendationHelpful(selectedGuide.id, "guide", true)}
                  className="px-2.5 py-1 bg-emerald-950/20 text-emerald-450 hover:bg-emerald-900/40 rounded text-xs font-bold transition-all border border-emerald-900/40 cursor-pointer"
                >
                  Yes
                </button>
                <button
                  onClick={() => logRecommendationHelpful(selectedGuide.id, "guide", false)}
                  className="px-2.5 py-1 bg-rose-950/20 text-rose-400 hover:bg-rose-900/40 rounded text-xs font-bold transition-all border border-rose-900/40 cursor-pointer"
                >
                  No
                </button>
              </div>
              <button
                onClick={() => {
                  setSelectedGuide(null);
                  logRecommendationClick(selectedGuide.id, "guide");
                }}
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
