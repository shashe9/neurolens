"use client";

import React, { useState, useEffect } from "react";
import { useActiveChild, Child } from "@/components/ActiveChildContext";
import { 
  Trash2, 
  Plus, 
  User,
  CheckCircle,
  HelpCircle,
  ArrowRight,
  Edit2
} from "lucide-react";

export default function ChildrenManagement() {
  const { activeChild, activeParentId, childrenList, selectActiveChild, refreshContext, fetchWithAuth } = useActiveChild();

  const [archivedChildren, setArchivedChildren] = useState<Child[]>([]);
  const [showArchived, setShowArchived] = useState(false);
  const [loadingArchived, setLoadingArchived] = useState(false);

  // Form State
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [dob, setDob] = useState("");
  const [gender, setGender] = useState("");
  const [editingChild, setEditingChild] = useState<Child | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Archive Confirmation State
  const [archiveConfirmId, setArchiveConfirmId] = useState<string | null>(null);

  // Baseline Questionnaire State
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);
  const [questionnaireChild, setQuestionnaireChild] = useState<Child | null>(null);
  const [questionnaireStep, setQuestionnaireStep] = useState(0);
  const [answers, setAnswers] = useState({
    speaks_words: null as boolean | null,
    points_to_objects: null as boolean | null,
    responds_to_name: null as boolean | null,
    walks_independently: null as boolean | null,
    intended_purpose_play: null as boolean | null,
  });

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const matchMilestoneId = (milestones: any[], key: string): string | null => {
    if (!milestones || milestones.length === 0) return null;
    let query = "";
    if (key === "speaks_words") {
      query = "single words";
    } else if (key === "points_to_objects") {
      query = "points to ask";
    } else if (key === "responds_to_name") {
      query = "looks at your face";
    } else if (key === "walks_independently") {
      query = "walks forward";
    } else if (key === "intended_purpose_play") {
      query = "intended purpose";
    }
    
    const found = milestones.find((m: any) => m.title.toLowerCase().includes(query.toLowerCase()));
    return found ? found.id : null;
  };

  const handleAnswer = (value: boolean) => {
    const keys = [
      "speaks_words",
      "points_to_objects",
      "responds_to_name",
      "walks_independently",
      "intended_purpose_play"
    ];
    const currentKey = keys[questionnaireStep];
    
    setAnswers(prev => ({
      ...prev,
      [currentKey]: value
    }));

    if (questionnaireStep < 4) {
      setQuestionnaireStep(prev => prev + 1);
    } else {
      const updatedAnswers = {
        ...answers,
        [currentKey]: value
      };
      submitQuestionnaireData(updatedAnswers);
    }
  };

  const submitQuestionnaireData = async (completedAnswers: typeof answers) => {
    if (!questionnaireChild) return;
    try {
      const msRes = await fetchWithAuth(`${apiUrl}/milestones`);
      let milestones: any[] = [];
      if (msRes.ok) {
        milestones = await msRes.json();
      }
      
      const milestone_seeds: Record<string, string> = {};
      const keys = ["speaks_words", "points_to_objects", "responds_to_name", "walks_independently", "intended_purpose_play"];
      
      keys.forEach(key => {
        const mId = matchMilestoneId(milestones, key);
        if (mId) {
          const isObserved = completedAnswers[key as keyof typeof answers];
          milestone_seeds[mId] = isObserved ? "observed" : "not_observed";
        }
      });

      const response = await fetchWithAuth(`${apiUrl}/onboarding/questionnaire`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          child_id: questionnaireChild.id,
          snapshot: completedAnswers,
          milestone_seeds
        })
      });

      if (!response.ok) {
        throw new Error("Failed to save questionnaire baseline");
      }

      setShowQuestionnaire(false);
      await refreshContext();
    } catch (err: any) {
      alert(err.message || "Failed to submit questionnaire.");
    }
  };

  const fetchArchived = async () => {
    if (!activeParentId) return;
    setLoadingArchived(true);
    try {
      const res = await fetchWithAuth(`${apiUrl}/children?parent_id=${activeParentId}&include_archived=true`);
      if (res.ok) {
        const data: Child[] = await res.json();
        const archived = data.filter((c) => !!c.deleted_at);
        setArchivedChildren(archived);
      }
    } catch (err) {
      console.error("Failed to load archived children:", err);
    } finally {
      setLoadingArchived(false);
    }
  };

  useEffect(() => {
    if (showArchived) {
      fetchArchived();
    }
  }, [showArchived, activeParentId, childrenList]);

  const resetForm = () => {
    setFirstName("");
    setLastName("");
    setDob("");
    setGender("");
    setEditingChild(null);
    setErrorMsg(null);
  };

  const startEdit = (child: Child) => {
    setEditingChild(child);
    setFirstName(child.first_name);
    setLastName(child.last_name);
    setDob(child.date_of_birth);
    setGender(child.gender || "");
    setErrorMsg(null);
    setSuccessMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!firstName.trim() || !lastName.trim() || !dob) {
      setErrorMsg("First name, last name, and date of birth are required.");
      return;
    }

    try {
      const payload = {
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        date_of_birth: dob,
        gender: gender.trim() || null,
        parent_id: activeParentId,
      };

      let res;
      if (editingChild) {
        res = await fetchWithAuth(`${apiUrl}/children/${editingChild.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            first_name: payload.first_name,
            last_name: payload.last_name,
            date_of_birth: payload.date_of_birth,
            gender: payload.gender,
          }),
        });
      } else {
        res = await fetchWithAuth(`${apiUrl}/children`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to save child profile.");
      }

      const savedChild: Child = await res.json();
      setSuccessMsg(
        editingChild
          ? "Child profile updated successfully!"
          : `Created child profile for ${savedChild.first_name}!`
      );

      if (!editingChild) {
        setTimeout(() => selectActiveChild(savedChild.id), 100);
        setQuestionnaireChild(savedChild);
        setAnswers({
          speaks_words: null,
          points_to_objects: null,
          responds_to_name: null,
          walks_independently: null,
          intended_purpose_play: null,
        });
        setQuestionnaireStep(0);
        setShowQuestionnaire(true);
      }

      resetForm();
      await refreshContext();

      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to process child profile.");
    }
  };

  const handleArchive = async (childId: string) => {
    if (!activeParentId) return;
    try {
      const res = await fetchWithAuth(`${apiUrl}/children/${childId}?deleted_by=${activeParentId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to archive child profile.");
      }

      setArchiveConfirmId(null);
      await refreshContext();
      if (showArchived) fetchArchived();
    } catch (err: any) {
      alert(err.message || "Failed to archive child.");
    }
  };

  const handleRestore = async (childId: string) => {
    try {
      const res = await fetchWithAuth(`${apiUrl}/children/${childId}/restore`, {
        method: "POST",
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to restore child profile.");
      }

      await refreshContext();
      if (showArchived) fetchArchived();
    } catch (err: any) {
      alert(err.message || "Failed to restore child.");
    }
  };

  const calculateAgeMonths = (dobString: string) => {
    const dob = new Date(dobString);
    const now = new Date();
    const yearsDiff = now.getFullYear() - dob.getFullYear();
    const monthsDiff = now.getMonth() - dob.getMonth();
    let ageMonths = yearsDiff * 12 + monthsDiff;
    if (now.getDate() < dob.getDate()) ageMonths -= 1;
    return ageMonths >= 0 ? `${ageMonths} months old` : "0 months";
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-6">
      
      {/* Page Title */}
      <div className="text-left space-y-2">
        <h1 className="text-4xl font-bold text-slate-900 leading-tight">
          Manage Child Profiles
        </h1>
        <p className="text-lg text-slate-500">
          Create and select child profiles to configure age-based milestone tracking.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Form Column */}
        <div className="lg:col-span-1">
          <div className="bg-white border border-slate-200 p-6 rounded-2xl space-y-6 sticky top-24 text-left shadow-sm">
            <div>
              <h2 className="text-xl font-semibold text-slate-800">
                {editingChild ? "Edit Profile" : "Add Profile"}
              </h2>
              <p className="text-sm text-slate-500 mt-1">
                Enter your child's profile details.
              </p>
            </div>

            {errorMsg && (
              <div className="p-4 bg-rose-50 border border-rose-100 text-rose-700 text-sm rounded-xl">
                {errorMsg}
              </div>
            )}

            {successMsg && (
              <div className="p-4 bg-emerald-50 border border-emerald-100 text-emerald-700 text-sm rounded-xl">
                {successMsg}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1">
                <label className="block text-sm font-semibold text-slate-600">First Name</label>
                <input
                  type="text"
                  placeholder="e.g. Timmy"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full bg-white border border-slate-200 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-base text-slate-800 outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="block text-sm font-semibold text-slate-600">Last Name</label>
                <input
                  type="text"
                  placeholder="e.g. Carter"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full bg-white border border-slate-200 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-base text-slate-800 outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="block text-sm font-semibold text-slate-600">Date of Birth</label>
                <input
                  type="date"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                  className="w-full bg-white border border-slate-200 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-base text-slate-800 outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="block text-sm font-semibold text-slate-600">Gender (Optional)</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="w-full bg-white border border-slate-200 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-base text-slate-800 outline-none"
                >
                  <option value="">Not Specified</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                  <option value="Prefer Not to Say">Prefer Not to Say</option>
                </select>
              </div>

              <div className="flex gap-2 pt-2">
                {editingChild && (
                  <button
                    type="button"
                    onClick={resetForm}
                    className="flex-1 py-3 border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-600 font-semibold text-base rounded-xl transition-all"
                  >
                    Cancel
                  </button>
                )}
                <button
                  type="submit"
                  className="flex-1 py-3 bg-indigo-650 hover:bg-indigo-750 text-white font-semibold text-base rounded-xl transition-all shadow-sm"
                >
                  {editingChild ? "Save" : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Children List */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-2xl font-semibold text-slate-100 text-left">Active Profiles</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {childrenList.map((c) => {
              const isActive = activeChild?.id === c.id;
              const initials = `${c.first_name[0] || ""}${c.last_name[0] || ""}`.toUpperCase();
              const isConfirmingArchive = archiveConfirmId === c.id;

              return (
                <div
                  key={c.id}
                  className={`p-6 rounded-2xl border transition-all text-left flex flex-col justify-between ${
                    isActive
                      ? "bg-indigo-50/15 border-indigo-200 shadow-sm"
                      : "bg-white border-slate-200 hover:border-slate-300 shadow-xs"
                  }`}
                >
                  {isConfirmingArchive ? (
                    <div className="space-y-4">
                      <p className="text-base font-bold text-rose-600">Archive profile for {c.first_name}?</p>
                      <p className="text-sm text-slate-500 leading-relaxed">
                        Observations and summaries linked to {c.first_name} will remain saved but will be hidden.
                      </p>
                      <div className="flex justify-end gap-2 pt-1">
                        <button
                          onClick={() => setArchiveConfirmId(null)}
                          className="px-3 py-1.5 text-sm font-semibold text-slate-500 hover:text-slate-700"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleArchive(c.id)}
                          className="px-4 py-1.5 bg-rose-600 hover:bg-rose-700 text-white text-sm font-semibold rounded-lg"
                        >
                          Archive
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div className="h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center font-bold text-base text-slate-700">
                            {initials}
                          </div>
                          <div>
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-semibold text-slate-800 text-lg">{c.first_name} {c.last_name}</span>
                              {isActive && (
                                <span className="text-sm bg-indigo-50 text-indigo-750 border border-indigo-100 px-2 py-0.5 rounded-lg font-semibold select-none">
                                  Active
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-slate-500 mt-1">
                              {calculateAgeMonths(c.date_of_birth)} &bull; {c.gender || "Not specified"}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 opacity-50 hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => startEdit(c)}
                            className="p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-50"
                            title="Edit Profile"
                          >
                            <Edit2 className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => setArchiveConfirmId(c.id)}
                            className="p-1.5 text-rose-500 hover:text-rose-600 rounded-lg hover:bg-slate-50"
                            title="Archive Profile"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>

                      {!isActive && (
                        <div className="mt-2 pt-3 border-t border-slate-100 flex justify-end">
                          <button
                            onClick={() => selectActiveChild(c.id)}
                            className="text-sm text-indigo-650 hover:text-indigo-750 font-semibold flex items-center gap-1"
                          >
                            Switch to active <ArrowRight className="h-4 w-4" />
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Archived Profiles Section */}
          <div className="pt-4 border-t border-slate-200 text-left">
            <button
              onClick={() => setShowArchived(!showArchived)}
              className="text-sm text-slate-500 hover:text-slate-800 font-semibold flex items-center gap-1 focus:outline-none"
            >
              <span>{showArchived ? "▼" : "▶"}</span> Show Archived Profiles
            </button>

            {showArchived && (
              <div className="mt-4 pl-4 space-y-3">
                {loadingArchived ? (
                  <p className="text-sm text-slate-400 italic">Loading archives...</p>
                ) : archivedChildren.length === 0 ? (
                  <p className="text-sm text-slate-400 italic">No archived profiles found.</p>
                ) : (
                  <div className="space-y-3 max-w-md">
                    {archivedChildren.map((c) => (
                      <div
                        key={c.id}
                        className="p-4 bg-white border border-slate-200 rounded-xl flex items-center justify-between text-sm shadow-xs"
                      >
                        <div>
                          <span className="text-sm font-semibold text-slate-500 line-through">
                            {c.first_name} {c.last_name}
                          </span>
                          <span className="text-sm text-slate-400 block mt-0.5">
                            DOB: {new Date(c.date_of_birth).toLocaleDateString()}
                          </span>
                        </div>
                        <button
                          onClick={() => handleRestore(c.id)}
                          className="px-3 py-1.5 border border-slate-200 hover:bg-slate-50 bg-white text-sm font-semibold rounded-lg text-slate-600"
                        >
                          Restore Profile
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Baseline Snapshot wizard modal (Cleaned up from glows) */}
      {showQuestionnaire && questionnaireChild && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/65 backdrop-blur-xs no-print">
          <div className="bg-white border border-slate-200 p-8 rounded-2xl max-w-md w-full shadow-lg space-y-6 relative text-left">
            
            <div className="text-center space-y-2">
              <span className="text-sm uppercase tracking-wide font-bold text-indigo-700 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
                Initial Child Snapshot
              </span>
              <h3 className="text-2xl font-bold text-slate-900 mt-2">
                Welcome, {questionnaireChild.first_name}!
              </h3>
              <p className="text-sm text-slate-500">
                Help us personalize Neurolens for {questionnaireChild.first_name}'s developmental journey.
              </p>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden border border-slate-200">
              <div 
                className="bg-indigo-600 h-full transition-all duration-300"
                style={{ width: `${((questionnaireStep + 1) / 5) * 100}%` }}
              />
            </div>

            {/* Steps */}
            <div className="py-4 space-y-2 min-h-[140px] flex flex-col justify-center text-center">
              {questionnaireStep === 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-slate-400">Step 1 of 5 &bull; Communication</p>
                  <p className="text-base text-slate-800 leading-relaxed font-semibold">
                    Does {questionnaireChild.first_name} communicate using several single words besides "mama" or "dada"?
                  </p>
                </div>
              )}
              {questionnaireStep === 1 && (
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-slate-400">Step 2 of 5 &bull; Feelings & Friendships</p>
                  <p className="text-base text-slate-800 leading-relaxed font-semibold">
                    Does {questionnaireChild.first_name} point to ask for something or get help?
                  </p>
                </div>
              )}
              {questionnaireStep === 2 && (
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-slate-400">Step 3 of 5 &bull; Attention</p>
                  <p className="text-base text-slate-800 leading-relaxed font-semibold">
                    Does {questionnaireChild.first_name} look at your face or respond when you call their name?
                  </p>
                </div>
              )}
              {questionnaireStep === 3 && (
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-slate-400">Step 4 of 5 &bull; Movement</p>
                  <p className="text-base text-slate-800 leading-relaxed font-semibold">
                    Does {questionnaireChild.first_name} walk forward independently?
                  </p>
                </div>
              )}
              {questionnaireStep === 4 && (
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-slate-400">Step 5 of 5 &bull; Play Behavior</p>
                  <p className="text-base text-slate-800 leading-relaxed font-semibold">
                    Does {questionnaireChild.first_name} try to use items for their intended purpose? (e.g., drinks from a cup, rolls a toy car, pretends to brush hair)
                  </p>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={() => handleAnswer(false)}
                className="flex-1 py-3 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-650 font-semibold text-base rounded-xl transition-all"
              >
                No / Not Yet
              </button>
              <button
                onClick={() => handleAnswer(true)}
                className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-750 text-white font-semibold text-base rounded-xl transition-all shadow-sm"
              >
                Yes
              </button>
            </div>

            <div className="flex justify-between items-center text-sm text-slate-500 pt-3 border-t border-slate-100">
              <button
                onClick={() => {
                  if (questionnaireStep > 0) setQuestionnaireStep(questionnaireStep - 1);
                }}
                disabled={questionnaireStep === 0}
                className="hover:text-slate-800 disabled:opacity-30 disabled:pointer-events-none transition-colors"
              >
                &larr; Back
              </button>
              <button
                onClick={() => setShowQuestionnaire(false)}
                className="hover:text-slate-800 transition-colors underline"
              >
                Skip Setup
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
