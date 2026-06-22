/**
 * Centralized API base URL config for Neurolens frontend.
 * Precedence of resolution:
 * 1. NEXT_PUBLIC_API_BASE_URL (Primary env injection e.g. on Vercel)
 * 2. NEXT_PUBLIC_API_URL (Optional fallback)
 * 3. "http://localhost:8000" (Default local backend port)
 */
export const API_BASE_URL = 
  process.env.NEXT_PUBLIC_API_BASE_URL || 
  process.env.NEXT_PUBLIC_API_URL || 
  "http://localhost:8000";
