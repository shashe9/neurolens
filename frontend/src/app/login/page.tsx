"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useActiveChild } from "@/components/ActiveChildContext";
import { AlertCircle } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { setToken, token } = useActiveChild();
  const router = useRouter();

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // If already logged in, redirect to dashboard immediately
  useEffect(() => {
    const savedToken = localStorage.getItem("neurolens_auth_token") || token;
    if (savedToken) {
      router.push("/dashboard");
    }
  }, [token, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email.trim() || !password.trim()) {
      setError("Please fill in all fields.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch(`${apiUrl}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.trim(),
          password: password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Invalid email or password");
      }

      const data = await response.json();
      
      // Save details to localStorage
      localStorage.setItem("neurolens_auth_token", data.access_token);
      localStorage.setItem("neurolens_parent_id", data.parent_id);
      
      // Update token in React state context
      setToken(data.access_token);
      
      // Redirect to dashboard
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to connect to the server. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex flex-col justify-center items-center relative py-12 px-4 sm:px-6 lg:px-8 overflow-hidden select-none">
      <div className="w-full max-w-md space-y-8 z-10 relative">
        {/* Brand Header */}
        <div className="text-center">
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-100 select-text">
            neurolens
          </h1>
          <p className="mt-3 text-base text-slate-300 select-text font-medium">
            Parent Observation & Clinician Preparation Portal
          </p>
        </div>

        {/* Clean Login Card */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 shadow-md relative overflow-hidden">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-medium animate-shake select-text flex items-center gap-2">
                <AlertCircle className="h-4 w-4 shrink-0" /> {error}
              </div>
            )}

            {/* Email Field */}
            <div className="space-y-2">
              <label htmlFor="email" className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="parent@example.com"
                className="w-full px-4 py-3 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-base placeholder-slate-650 focus:outline-none focus:border-slate-700 transition-all"
                disabled={isSubmitting}
              />
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Password
                </label>
              </div>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-4 py-3 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-base placeholder-slate-650 focus:outline-none focus:border-slate-700 transition-all"
                disabled={isSubmitting}
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 px-4 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-900 font-semibold text-base transition-all disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2 cursor-pointer"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-slate-900" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Authenticating...
                </>
              ) : (
                "Log In"
              )}
            </button>
          </form>
        </div>

        {/* Hint text for Judge Demo */}
        <p className="text-center text-sm text-slate-300 select-text font-medium">
          Demo credentials can be found in the 
          <code className="mx-1 px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-200">judge_demo_guide.md</code>
        </p>

        {/* Safety Disclaimer Footer */}
        <div className="pt-4 border-t border-slate-800/20 max-w-md mx-auto text-center text-xs text-slate-300 leading-relaxed select-text font-medium">
          Disclaimer: Neurolens is developmental observation tracking software. It does NOT diagnose autism or provide clinical recommendations. Diagnoses must always be conducted by qualified healthcare professionals.
        </div>
      </div>
    </div>
  );
}
