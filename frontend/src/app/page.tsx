"use client";

import React from "react";
import Link from "next/link";
import { useActiveChild } from "@/components/ActiveChildContext";
import { User, BookOpen, CheckSquare, Calendar, FileText, ShieldAlert, ArrowRight } from "lucide-react";

export default function Home() {
  const { childrenList, selectActiveChild, activeChild } = useActiveChild();

  const calculateAgeMonths = (dobString: string) => {
    const dob = new Date(dobString);
    const now = new Date();
    const yearsDiff = now.getFullYear() - dob.getFullYear();
    const monthsDiff = now.getMonth() - dob.getMonth();
    let ageMonths = yearsDiff * 12 + monthsDiff;
    if (now.getDate() < dob.getDate()) ageMonths -= 1;
    return ageMonths >= 0 ? `${ageMonths} Months` : "0 Months";
  };

  return (
    <div className="flex flex-col items-center justify-center py-12 lg:py-20 space-y-16 max-w-5xl mx-auto px-6">
      {/* Hero Header */}
      <div className="text-center max-w-3xl space-y-6">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-slate-100 leading-tight">
          Your Child's Developmental Journal
        </h1>
        <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
          A soft space to write down your child's daily moments, notice patterns naturally, and prepare simple summaries for pediatric visits.
        </p>
      </div>

      {/* Parent Value Proposition Section */}
      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Column: Empathetic Logging */}
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl space-y-4 flex flex-col justify-between shadow-sm">
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-indigo-500" /> Daily Moments
            </h3>
            <p className="text-base text-slate-350 leading-relaxed font-medium">
              Write naturally about what you observe in your child's play, speech, or interactions. Keep a gentle diary of their early milestones in your own words.
            </p>
          </div>
        </div>

        {/* Right Column: Pediatrician Collaboration */}
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl space-y-4 flex flex-col justify-between shadow-sm">
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <FileText className="h-5 w-5 text-indigo-500" /> Simple Visit Prep
            </h3>
            <p className="text-base text-slate-350 leading-relaxed font-medium">
              Prepare a warm reflection of your child's journey to share with your doctor, helping you discuss what's been on your mind clearly.
            </p>
          </div>
        </div>
      </div>

      {/* Visual Workflow Grid */}
      <div className="w-full max-w-4xl space-y-6">
        <h2 className="text-sm font-bold tracking-wide text-indigo-400 text-center uppercase">
          The Neurolens Journey
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center flex flex-col items-center justify-between shadow-sm">
            <User className="h-8 w-8 text-indigo-500 mb-3" />
            <p className="text-base font-bold text-slate-100">Your Child</p>
            <p className="text-base text-slate-300 mt-2 leading-relaxed">Set up child profile</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center flex flex-col items-center justify-between shadow-sm">
            <BookOpen className="h-8 w-8 text-indigo-500 mb-3" />
            <p className="text-base font-bold text-slate-100">Journal</p>
            <p className="text-base text-slate-300 mt-2 leading-relaxed">Log moments</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center flex flex-col items-center justify-between shadow-sm">
            <CheckSquare className="h-8 w-8 text-indigo-500 mb-3" />
            <p className="text-base font-bold text-slate-100">Journey</p>
            <p className="text-base text-slate-300 mt-2 leading-relaxed">View areas</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center flex flex-col items-center justify-between shadow-sm">
            <Calendar className="h-8 w-8 text-indigo-500 mb-3" />
            <p className="text-base font-bold text-slate-100">Visit Prep</p>
            <p className="text-base text-slate-300 mt-2 leading-relaxed">Note concerns</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center flex flex-col items-center justify-between shadow-sm">
            <FileText className="h-8 w-8 text-indigo-500 mb-3" />
            <p className="text-base font-bold text-slate-100">Summary</p>
            <p className="text-base text-slate-300 mt-2 leading-relaxed">Assemble prep</p>
          </div>
        </div>
      </div>

      {/* Profile Selector */}
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-sm">
        <h3 className="text-xl font-bold text-slate-100 mb-6 text-center">Select Child Profile</h3>
        <div className="space-y-4">
          {childrenList.length === 0 ? (
            <div className="text-center py-6 text-base text-slate-300 leading-relaxed font-medium">
              No profiles found. Let's create one!
            </div>
          ) : (
            childrenList.map((c) => {
              const initials = `${c.first_name[0] || ""}${c.last_name[0] || ""}`.toUpperCase();
              const isSelected = activeChild?.id === c.id;

              return (
                <Link
                  key={c.id}
                  href="/dashboard"
                  onClick={() => selectActiveChild(c.id)}
                  className={`flex items-center justify-between p-4 rounded-xl group transition-all duration-200 border ${
                    isSelected
                      ? "bg-slate-850 border-slate-750"
                      : "bg-slate-900 hover:bg-slate-850 border-slate-800"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-full bg-slate-800 flex items-center justify-center font-bold text-sm text-slate-100">
                      {initials}
                    </div>
                    <div className="text-left">
                      <p className="font-semibold text-slate-100 group-hover:text-indigo-600 transition-colors">
                        {c.first_name} {c.last_name}
                      </p>
                      <p className="text-sm text-slate-300">
                        {calculateAgeMonths(c.date_of_birth)} &bull; {c.gender || "Not specified"}
                      </p>
                    </div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-slate-300 group-hover:translate-x-1 transition-transform" />
                </Link>
              );
            })
          )}
          
          <Link
            href="/children"
            className="w-full py-4 px-4 border border-dashed border-slate-750 hover:border-slate-650 rounded-xl text-slate-300 text-base font-semibold flex items-center justify-center gap-2 hover:bg-slate-950 transition-all"
          >
            <span>+</span> Configure & Switch Profiles
          </Link>
        </div>
      </div>

      {/* Safety Notice Disclaimer */}
      <div className="w-full max-w-2xl p-6 bg-slate-900 border border-slate-800 text-slate-300 rounded-2xl flex items-start gap-4 shadow-sm">
        <ShieldAlert className="h-6 w-6 text-amber-600 shrink-0 mt-0.5" />
        <div className="text-left space-y-1">
          <h4 className="text-sm font-bold uppercase tracking-wider text-slate-100">
            A Gentle Note
          </h4>
          <p className="text-base leading-relaxed text-slate-300 font-medium">
            Neurolens is a developmental journal to help you notice patterns and prepare for pediatric visits. It is not diagnostic, does not evaluate autism risk, and does not provide clinical assessments. Always consult a qualified pediatrician.
          </p>
        </div>
      </div>
    </div>
  );
}
