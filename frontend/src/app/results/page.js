"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Check, X, AlertTriangle, BookOpen, Download, ChevronRight, Loader2 } from "lucide-react";
import Link from "next/link";

const API_BASE = "https://rag-rag-v16-010-production-1b78.up.railway.app";

export default function ResultsPage() {
  const [skills, setSkills] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchSkills() {
      try {
        const res = await fetch(`${API_BASE}/api/v1/nlp/index/retun_skills/1`, {
          headers: { accept: "application/json" },
        });

        if (!res.ok) {
          throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();
        setSkills(data);
      } catch (err) {
        console.error("retun_skills error:", err);
        setError(err.message || "Failed to fetch skills data.");
      } finally {
        setLoading(false);
      }
    }

    fetchSkills();
  }, []);

  // Helper: try to extract arrays from whatever shape the API returns
  const extractSkillArrays = (data) => {
    if (!data) return { found: [], missing: [], other: [] };

    // If the API returns { found: [...], missing: [...] } structure
    if (data.found || data.missing || data.matched) {
      return {
        found: data.found || data.matched || [],
        missing: data.missing || data.gap || [],
        other: data.underdeveloped || data.other || [],
      };
    }

    // If it returns a flat array of skills
    if (Array.isArray(data)) {
      return { found: data, missing: [], other: [] };
    }

    // If it returns { data: ... } wrapper
    if (data.data) {
      return extractSkillArrays(data.data);
    }

    // If it returns { skills: [...] }
    if (data.skills) {
      if (Array.isArray(data.skills)) {
        return { found: data.skills, missing: [], other: [] };
      }
      return extractSkillArrays(data.skills);
    }

    // Fallback: display the raw keys
    return { found: [], missing: [], other: [], raw: data };
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Analysis Results</h1>
          <p className="text-muted-foreground mt-1">Skills extracted from your uploaded resume</p>
        </div>
        <div className="flex gap-3 mt-4 md:mt-0">
          <button className="inline-flex items-center rounded-full border border-border bg-background px-4 py-2 text-sm font-medium shadow-sm hover:bg-muted transition-colors">
            <Download className="mr-2 w-4 h-4" /> Export PDF
          </button>
          <Link href="/cv-analyzer" className="inline-flex items-center rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90 transition-colors">
            New Scan
          </Link>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center justify-center py-32"
        >
          <Loader2 className="w-12 h-12 text-primary animate-spin mb-6" />
          <p className="text-primary tracking-widest text-sm uppercase font-bold animate-pulse">
            Extracting Skills Vector...
          </p>
        </motion.div>
      )}

      {/* Error State */}
      {error && !loading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-3xl p-12 flex flex-col items-center justify-center text-center"
        >
          <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mb-6 border border-red-500/50">
            <AlertTriangle className="w-10 h-10 text-red-500" />
          </div>
          <h3 className="text-2xl font-bold mb-2">Failed to Load Skills</h3>
          <p className="text-muted-foreground mb-6 max-w-md">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg text-sm font-bold transition-colors hover:bg-foreground hover:text-background"
          >
            Retry
          </button>
        </motion.div>
      )}

      {/* Success State */}
      {skills && !loading && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Left Column: Overview */}
          <div className="lg:col-span-1 space-y-8">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass rounded-3xl p-8 flex flex-col items-center text-center shadow-xl border-t-4 border-t-primary"
            >
              <h2 className="text-xl font-bold mb-6">Skills Overview</h2>
              {(() => {
                const parsed = extractSkillArrays(skills);
                const total = parsed.found.length + parsed.missing.length + parsed.other.length;
                const score = total > 0 ? Math.round((parsed.found.length / total) * 100) : 0;
                return (
                  <>
                    <div className="relative w-48 h-48 flex items-center justify-center">
                      <svg className="absolute inset-0 w-full h-full transform -rotate-90">
                        <circle
                          cx="96" cy="96" r="88"
                          className="stroke-muted fill-none stroke-[12px]"
                        />
                        <circle
                          cx="96" cy="96" r="88"
                          className="stroke-primary fill-none stroke-[12px] transition-all duration-1000 ease-out"
                          strokeDasharray="552.9"
                          strokeDashoffset={552.9 - (552.9 * score) / 100}
                          strokeLinecap="round"
                        />
                      </svg>
                      <div className="flex flex-col items-center">
                        <span className="text-5xl font-extrabold">{total}<span className="text-lg text-muted-foreground ml-1">skills</span></span>
                        <span className="text-sm text-primary font-medium mt-1">{parsed.found.length} matched</span>
                      </div>
                    </div>
                  </>
                );
              })()}
            </motion.div>

            {/* Quick Nav */}
            <div className="glass rounded-3xl p-6">
              <h3 className="text-lg font-bold mb-4 border-b border-border pb-2">Deep Dive</h3>
              <div className="space-y-3">
                <Link href="/skill-gap" className="flex items-center justify-between p-3 rounded-xl hover:bg-muted transition-colors group">
                  <span className="font-medium">Skill Gap Analysis</span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </Link>
                <Link href="/learning" className="flex items-center justify-between p-3 rounded-xl hover:bg-muted transition-colors group">
                  <span className="font-medium">Learning Paths</span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </Link>
              </div>
            </div>
          </div>

          {/* Right Column: Skills Display */}
          <div className="lg:col-span-2 space-y-8">
            {(() => {
              const parsed = extractSkillArrays(skills);

              return (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="glass rounded-3xl p-6 md:p-8"
                >
                  <h2 className="text-2xl font-bold mb-6">Extracted Skills</h2>

                  <div className="space-y-6">
                    {/* Found Skills */}
                    {parsed.found.length > 0 && (
                      <div>
                        <h3 className="font-semibold flex items-center text-green-500 mb-3">
                          <Check className="w-5 h-5 mr-2" /> Matched Skills ({parsed.found.length})
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {parsed.found.map((skill, i) => (
                            <span key={i} className="px-3 py-1 rounded-full text-sm font-medium bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20">
                              {typeof skill === 'string' ? skill : skill.name || JSON.stringify(skill)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Missing Skills */}
                    {parsed.missing.length > 0 && (
                      <div>
                        <h3 className="font-semibold flex items-center text-red-500 mb-3">
                          <X className="w-5 h-5 mr-2" /> Missing Critical Skills ({parsed.missing.length})
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {parsed.missing.map((skill, i) => (
                            <span key={i} className="px-3 py-1 rounded-full text-sm font-medium bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20">
                              {typeof skill === 'string' ? skill : skill.name || JSON.stringify(skill)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Other Skills */}
                    {parsed.other.length > 0 && (
                      <div>
                        <h3 className="font-semibold flex items-center text-yellow-500 mb-3">
                          <AlertTriangle className="w-5 h-5 mr-2" /> Needs Improvement ({parsed.other.length})
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {parsed.other.map((skill, i) => (
                            <span key={i} className="px-3 py-1 rounded-full text-sm font-medium bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 border border-yellow-500/20">
                              {typeof skill === 'string' ? skill : skill.name || JSON.stringify(skill)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Raw fallback if we couldn't parse the structure */}
                    {parsed.raw && (
                      <div>
                        <h3 className="font-semibold flex items-center text-primary mb-3">
                          <BookOpen className="w-5 h-5 mr-2" /> Raw API Response
                        </h3>
                        <pre className="bg-background/50 border border-border rounded-xl p-4 text-xs overflow-x-auto text-foreground whitespace-pre-wrap">
                          {JSON.stringify(parsed.raw, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}
