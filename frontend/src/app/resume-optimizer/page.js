"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Check, X, FileText, Zap, Loader2, AlertTriangle, Target } from "lucide-react";

// مكون فرعي لإضافة تأثير 3D حقيقي ومستقل لكل بطاقة اقتراح
const TiltCard = ({ children, delay = 0 }) => {
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // زاوية الميلان
    const rotateX = (y / rect.height - 0.5) * -10;
    const rotateY = (x / rect.width - 0.5) * 10;
    
    setTilt({ x: rotateX, y: rotateY });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ 
        opacity: 1, 
        y: 0, 
        scale: 1,
        rotateX: tilt.x,
        rotateY: tilt.y
      }}
      exit={{ opacity: 0, scale: 0.9, rotateX: 0, rotateY: 0 }}
      transition={{ 
        type: "spring", 
        stiffness: 300, 
        damping: 20,
        opacity: { delay },
        y: { delay }
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ transformStyle: "preserve-3d", perspective: "1000px" }}
      className="w-full will-change-transform"
    >
      <div style={{ transform: "translateZ(20px)" }}>
        {children}
      </div>
    </motion.div>
  );
};

export default function ResumeOptimizerPage() {
  // =========================
  // Resume State
  // =========================
  const [resume, setResume] = useState({
    summary:
      "Dedicated software engineer looking for a job to write code. Have experience in React and Node.js.",
    experience: [
      {
        id: 1,
        role: "Frontend Developer",
        company: "TechCorp",
        desc: "Worked on UI components and fixed bugs in the main app.",
      },
      {
        id: 2,
        role: "Intern",
        company: "StartupInc",
        desc: "Helped the team with various web tasks.",
      },
    ],
  });

  const [suggestions, setSuggestions] = useState([]);

  // =========================
  // ATS STATE
  // =========================
  const [atsData, setAtsData] = useState(null);
  const [atsLoading, setAtsLoading] = useState(true);
  const [atsError, setAtsError] = useState(null);

  // =========================
  // FETCH ATS API
  // =========================
  useEffect(() => {
    async function fetchATS() {
      const projectId = localStorage.getItem("project_id");
      try {
        const res = await fetch(
          `https://gb-main-production.up.railway.app/api/v1/nlp/index/retun_ats_score_recommendtion/${projectId}`,
          {
            method: "GET",
            headers: { accept: "application/json" },
          }
        );

        if (!res.ok) {
          throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();
        setAtsData(data);

        // Map API → UI format
        const mappedSuggestions = (data?.[1] || []).map((item, i) => ({
          id: `ats-${i}`,
          targetType: "ats",
          issue: item.title,
          suggestion: item.actions?.join(" "),
          status: "pending",
        }));

        setSuggestions(mappedSuggestions);
      } catch (err) {
        console.error("ATS error:", err);
        setAtsError(err.message || "Failed to load ATS data");
      } finally {
        setAtsLoading(false);
      }
    }

    fetchATS();
  }, []);

  const score = atsData?.[0] || 0;

  // =========================
  // ACTION HANDLER
  // =========================
  const handleAction = (sug, action) => {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === sug.id ? { ...s, status: action } : s))
    );
  };

  const activeSuggestions = suggestions.filter((s) => s.status === "pending");

  return (
    <div className="min-h-screen flex flex-col max-w-7xl mx-auto space-y-8 pb-12 pt-6 px-4">
      
      {/* Floating Header */}
      <motion.div
        className="w-full text-center z-10"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: [0, -8, 0] }}
        transition={{ 
          opacity: { duration: 0.8 },
          y: { duration: 4, repeat: Infinity, ease: "easeInOut" } 
        }}
      >
        <div className="inline-flex items-center justify-center space-x-3 mb-3">
          <Zap className="w-7 h-7 text-primary animate-pulse" />
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500 pb-1">
            Smart Resume Optimizer
          </h1>
        </div>
        <p className="text-muted-foreground text-lg max-w-xl mx-auto">
          ATS-powered resume intelligence system
        </p>
      </motion.div>

      {/* Main Content Layout */}
      <div className="flex flex-col lg:flex-row gap-8 flex-1 w-full">
        
        {/* LEFT PANEL - LIVE PREVIEW */}
        <motion.div 
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full lg:w-1/2 glass p-8 rounded-3xl border border-primary/10 shadow-xl bg-background/50 backdrop-blur-md relative overflow-hidden"
        >
          {/* Subtle background glow */}
          <div className="absolute -top-24 -left-24 w-48 h-48 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
          
          <div className="flex items-center mb-8 border-b border-border/50 pb-4">
            <FileText className="w-6 h-6 text-primary mr-3" />
            <h2 className="text-2xl font-bold tracking-tight">Live Preview</h2>
          </div>

          <div className="space-y-8 relative z-10">
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-primary mb-3">Summary</h3>
              <p className="text-sm leading-relaxed text-foreground/80 bg-background/40 p-4 rounded-xl border border-border/50">
                {resume.summary}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-primary mb-3">Experience</h3>
              <div className="space-y-4">
                {resume.experience.map((exp) => (
                  <div key={exp.id} className="bg-background/40 p-4 rounded-xl border border-border/50 hover:border-primary/30 transition-colors">
                    <div className="font-bold text-md text-foreground flex justify-between items-center mb-1">
                      <span>{exp.role}</span>
                      <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded-md">{exp.company}</span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-2">{exp.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* RIGHT PANEL - ATS ENGINE */}
        <div className="w-full lg:w-1/2 flex flex-col space-y-6">
          
          {/* ATS Score Display */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel p-6 rounded-3xl border border-primary/20 shadow-lg bg-gradient-to-br from-background/50 to-primary/5 flex justify-between items-center"
          >
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-primary/10 rounded-xl">
                <Target className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h2 className="text-foreground font-bold tracking-wide">ATS Score Validation</h2>
                <p className="text-xs text-muted-foreground mt-1">Real-time parser matching</p>
              </div>
            </div>
            <div className="flex items-baseline space-x-1">
              <span className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500">
                {atsLoading ? "--" : score}
              </span>
              <span className="text-lg font-bold text-muted-foreground">/ 100</span>
            </div>
          </motion.div>

          {/* Loading State */}
          {atsLoading && (
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex-1 flex flex-col items-center justify-center py-12 glass rounded-3xl border border-border/50"
            >
               <div className="relative flex items-center justify-center mb-4">
                  <motion.div
                    className="absolute w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                  />
                  <Loader2 className="w-6 h-6 text-primary animate-pulse" />
                </div>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500 tracking-widest text-xs uppercase font-bold animate-pulse">
                  Scanning Document...
                </span>
            </motion.div>
          )}

          {/* Error State */}
          {atsError && !atsLoading && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
              className="glass rounded-3xl p-8 flex flex-col items-center justify-center text-center border border-red-500/20 bg-red-500/5 shadow-lg"
            >
              <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mb-4 border-2 border-red-500/30">
                <AlertTriangle className="w-8 h-8 text-red-500" />
              </div>
              <h3 className="text-xl font-bold mb-2">Analysis Failed</h3>
              <p className="text-sm text-muted-foreground mb-4">{atsError}</p>
            </motion.div>
          )}

          {/* Suggestions List */}
          {!atsLoading && !atsError && (
            <div className="flex-1 space-y-4">
              <AnimatePresence mode="popLayout">
                {activeSuggestions.length === 0 && !atsLoading ? (
                  <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="py-12 text-center glass rounded-3xl border border-primary/20"
                  >
                     <Sparkles className="w-10 h-10 text-primary mx-auto mb-4 opacity-50" />
                     <p className="text-foreground font-bold">All caught up!</p>
                     <p className="text-sm text-muted-foreground mt-2">No pending ATS improvements found.</p>
                  </motion.div>
                ) : (
                  activeSuggestions.map((sug, idx) => (
                    <TiltCard key={sug.id} delay={idx * 0.1}>
                      <div className="glass p-5 rounded-2xl border border-primary/20 bg-background/60 hover:bg-background/80 transition-colors shadow-sm group">
                        
                        <div className="flex items-start justify-between mb-3">
                          <h3 className="font-bold text-foreground leading-tight pr-4">
                            {sug.issue}
                          </h3>
                          <span className="flex-shrink-0 px-2 py-1 bg-red-500/10 text-red-500 text-[10px] font-bold uppercase rounded-md border border-red-500/20">
                            Issue
                          </span>
                        </div>

                        <p className="text-sm text-muted-foreground mb-5 leading-relaxed">
                          {sug.suggestion}
                        </p>

                        <div className="flex gap-3">
                          <button
                            onClick={() => handleAction(sug, "applied")}
                            className="flex-1 flex items-center justify-center bg-primary text-primary-foreground py-2.5 rounded-xl text-sm font-bold shadow-md shadow-primary/20 hover:bg-primary/90 hover:-translate-y-0.5 transition-all"
                          >
                            <Check className="w-4 h-4 mr-2" />
                            Apply Fix
                          </button>

                          <button
                            onClick={() => handleAction(sug, "dismissed")}
                            className="flex-1 flex items-center justify-center bg-background/50 border border-border/80 text-foreground py-2.5 rounded-xl text-sm font-bold hover:border-red-500/50 hover:text-red-400 hover:-translate-y-0.5 transition-all"
                          >
                            <X className="w-4 h-4 mr-2" />
                            Dismiss
                          </button>
                        </div>
                      </div>
                    </TiltCard>
                  ))
                )}
              </AnimatePresence>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
