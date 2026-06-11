"use client";

import React, { useState, useEffect } from "react";
import { useActiveChild, Child } from "@/components/ActiveChildContext";

export default function ChildrenManagement() {
  const { activeChild, activeParentId, childrenList, selectActiveChild, refreshContext } = useActiveChild();

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

  // Delete/Archive Confirmation State
  const [archiveConfirmId, setArchiveConfirmId] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Fetch archived children
  const fetchArchived = async () => {
    if (!activeParentId) return;
    setLoadingArchived(true);
    try {
      const res = await fetch(`${apiUrl}/children?parent_id=${activeParentId}&include_archived=true`);
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

  // Form Reset
  const resetForm = () => {
    setFirstName("");
    setLastName("");
    setDob("");
    setGender("");
    setEditingChild(null);
    setErrorMsg(null);
  };

  // Set form for editing
  const startEdit = (child: Child) => {
    setEditingChild(child);
    setFirstName(child.first_name);
    setLastName(child.last_name);
    setDob(child.date_of_birth);
    setGender(child.gender || "");
    setErrorMsg(null);
    setSuccessMsg(null);
  };

  // Add/Edit Submit Handler
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
        // Edit Child PUT
        res = await fetch(`${apiUrl}/children/${editingChild.id}`, {
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
        // Create Child POST
        res = await fetch(`${apiUrl}/children`, {
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

      // Auto resolve selection on creation
      if (!editingChild) {
        // Auto select newly created child
        setTimeout(() => selectActiveChild(savedChild.id), 100);
      }

      resetForm();
      await refreshContext();

      // Clear success message
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to process child profile.");
    }
  };

  // Archive Child
  const handleArchive = async (childId: string) => {
    if (!activeParentId) return;
    try {
      const res = await fetch(`${apiUrl}/children/${childId}?deleted_by=${activeParentId}`, {
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

  // Restore Child
  const handleRestore = async (childId: string) => {
    try {
      const res = await fetch(`${apiUrl}/children/${childId}/restore`, {
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
    return ageMonths >= 0 ? `${ageMonths} months` : "0 months";
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
          Manage Child Profiles
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Create, edit, and archive child records. Archived children and their observations remain saved for clinical review histories.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Form Column */}
        <div className="lg:col-span-1">
          <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl space-y-6 sticky top-24 backdrop-blur-sm">
            <div>
              <h2 className="text-lg font-bold text-slate-100">
                {editingChild ? "Edit Child Profile" : "Add New Child Profile"}
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Configure profile parameters. First name, last name, and date of birth are required.
              </p>
            </div>

            {errorMsg && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-xl">
                ⚠️ {errorMsg}
              </div>
            )}

            {successMsg && (
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-xl">
                ✅ {successMsg}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">First Name</label>
                <input
                  type="text"
                  placeholder="e.g. Timmy"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-sm text-slate-100 outline-none transition-colors"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Last Name</label>
                <input
                  type="text"
                  placeholder="e.g. Carter"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-sm text-slate-100 outline-none transition-colors"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Date of Birth</label>
                <input
                  type="date"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-sm text-slate-100 outline-none transition-colors"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Gender (Optional)</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors"
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
                    className="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs rounded-xl transition-all"
                  >
                    Cancel
                  </button>
                )}
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-gradient-to-r from-indigo-500 to-violet-500 text-white font-semibold text-xs rounded-xl shadow-lg hover:brightness-110 active:scale-[0.98] transition-all"
                >
                  {editingChild ? "Save Changes" : "Create Profile"}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Children List Column */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-lg font-bold text-slate-100">Active Profiles</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {childrenList.map((c) => {
              const isActive = activeChild?.id === c.id;
              const initials = `${c.first_name[0] || ""}${c.last_name[0] || ""}`.toUpperCase();
              const isConfirmingArchive = archiveConfirmId === c.id;

              return (
                <div
                  key={c.id}
                  className={`p-5 rounded-2xl border transition-all ${
                    isActive
                      ? "bg-slate-900/40 border-indigo-500/50 shadow-md shadow-indigo-500/[0.03]"
                      : "bg-slate-900/20 border-slate-850 hover:border-slate-800"
                  }`}
                >
                  {isConfirmingArchive ? (
                    <div className="space-y-3">
                      <p className="text-xs font-semibold text-red-400">⚠️ Archive profile for {c.first_name}?</p>
                      <p className="text-[11px] text-slate-400 leading-relaxed">
                        Observations, visits, and reports linked to {c.first_name} remain archived in the database but will be hidden from current selection filters.
                      </p>
                      <div className="flex justify-end gap-2 pt-1">
                        <button
                          onClick={() => setArchiveConfirmId(null)}
                          className="px-2.5 py-1 text-[10px] text-slate-400 hover:text-slate-200"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleArchive(c.id)}
                          className="px-3.5 py-1 bg-red-600 hover:bg-red-500 text-white text-[10px] font-semibold rounded-lg"
                        >
                          Confirm Archive
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center font-bold text-xs text-white">
                          {initials}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-slate-200">{c.first_name} {c.last_name}</span>
                            {isActive && (
                              <span className="text-[9px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/25 px-1.5 py-0.5 rounded font-semibold select-none">
                                Active
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-400 mt-1">
                            {calculateAgeMonths(c.date_of_birth)} &bull; {c.gender || "Not specified"}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => startEdit(c)}
                          className="p-1 text-[10px] text-slate-400 hover:text-slate-200"
                          title="Edit Child Profile"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => setArchiveConfirmId(c.id)}
                          className="p-1 text-[10px] text-red-400 hover:text-red-300"
                          title="Archive Profile"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  )}

                  {!isActive && !isConfirmingArchive && (
                    <div className="mt-4 pt-3 border-t border-slate-800/40 flex justify-end">
                      <button
                        onClick={() => selectActiveChild(c.id)}
                        className="text-[10px] text-indigo-400 hover:text-indigo-350 hover:underline font-semibold"
                      >
                        Switch to active &rarr;
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Archived Section */}
          <div className="pt-4 border-t border-slate-850">
            <button
              onClick={() => setShowArchived(!showArchived)}
              className="text-xs text-slate-400 hover:text-slate-200 font-semibold flex items-center gap-1.5"
            >
              <span>{showArchived ? "▼" : "▶"}</span> Show Archived Profiles
            </button>

            {showArchived && (
              <div className="mt-4 pl-4 space-y-3">
                {loadingArchived ? (
                  <p className="text-xs text-slate-500">Loading archives...</p>
                ) : archivedChildren.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">No archived profiles found.</p>
                ) : (
                  <div className="space-y-2 max-w-md">
                    {archivedChildren.map((c) => (
                      <div
                        key={c.id}
                        className="p-3 bg-slate-900/20 border border-slate-850 rounded-xl flex items-center justify-between text-xs"
                      >
                        <div>
                          <span className="font-semibold text-slate-400 line-through">
                            {c.first_name} {c.last_name}
                          </span>
                          <span className="text-[10px] text-slate-500 block">
                            DOB: {new Date(c.date_of_birth).toLocaleDateString()}
                          </span>
                        </div>
                        <button
                          onClick={() => handleRestore(c.id)}
                          className="px-2.5 py-1 border border-slate-800 hover:border-slate-700 bg-slate-900 text-[10px] text-indigo-400 font-semibold rounded-lg transition-all"
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
    </div>
  );
}
