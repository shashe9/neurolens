import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { ActiveChildProvider } from "@/components/ActiveChildContext";
import { HeaderChildProfile } from "@/components/HeaderChildProfile";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Neurolens | Clinician Preparation Platform",
  description: "Aggregating developmental observations, milestones, and visit priority context to generate clinician reports.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-screen bg-slate-950 text-slate-50 flex flex-col font-sans">
        <ActiveChildProvider>
          {/* Glassmorphic Navbar */}
          <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
              <div className="flex items-center gap-8">
                <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent hover:opacity-95 transition-opacity">
                  <span>neurolens</span>
                  <span className="text-xs px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/25">V1</span>
                </Link>
                <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
                  <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
                  <Link href="/observations" className="hover:text-white transition-colors">Log Observation</Link>
                  <Link href="/milestones" className="hover:text-white transition-colors">Review Milestones</Link>
                  <Link href="/visit" className="hover:text-white transition-colors">Prepare Visit</Link>
                  <Link href="/report" className="hover:text-white transition-colors">Generate Report</Link>
                </nav>
              </div>
              
              <HeaderChildProfile />
            </div>
          </header>

          {/* Content Area */}
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
        </ActiveChildProvider>

        {/* Footer */}
        <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p>&copy; {new Date().getFullYear()} Neurolens. All rights reserved.</p>
            <p className="text-slate-600">This platform provides developmental context tracking and clinician preparation. It does not perform autism screening or diagnostics.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
