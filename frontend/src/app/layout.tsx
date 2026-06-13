import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ActiveChildProvider } from "@/components/ActiveChildContext";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

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
          {/* Custom Navbar */}
          <Navbar />

          {/* Content Area */}
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
          
          {/* Custom Footer */}
          <Footer />
        </ActiveChildProvider>
      </body>
    </html>
  );
}
