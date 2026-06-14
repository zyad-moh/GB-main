"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { PlayCircle, TerminalSquare, Clock, Loader2, AlertTriangle, BookOpen, ArrowRight, Sparkles } from "lucide-react";

const API_BASE = "http://127.0.0.1:5000";

// مكون فرعي لإضافة تأثير 3D حقيقي ومستقل لكل بطاقة
const TiltCard = ({ children, delay }) => {
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // حساب زاوية الميلان (حد أقصى 10 درجات ليكون التأثير ناعماً)
    const rotateX = (y / rect.height - 0.5) * -10;
    const rotateY = (x / rect.width - 0.5) * 10;
    
    setTilt({ x: rotateX, y: rotateY });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 40, scale: 0.95 }}
      animate={{ 
        opacity: 1, 
        y: 0, 
        scale: 1,
        rotateX: tilt.x,
        rotateY: tilt.y
      }}
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

export default function LearningPage() {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchRecommendations() {
      const projectId = localStorage.getItem("project_id");
      try {
        const res = await fetch(`${API_BASE}/api/v1/nlp/index/retun_learning_recommendtion/${projectId}`, {
          headers: { accept: "application/json" },
        });

        if (!res.ok) {
          throw new Error(`Server error: ${res.status}`);
        }

        const rawData = await res.json();
        const parsedData = typeof rawData === "string" ? JSON.parse(rawData) : rawData;

        setRecommendations(parsedData);
      } catch (err) {
        console.error("retun_learning_recommendtion error:", err);
        setError(err.message || "Failed to fetch learning recommendations.");
      } finally {
        setLoading(false);
      }
    }

    fetchRecommendations();
  }, []);

  return (
    <div className="min-h-screen flex flex-col max-w-6xl mx-auto space-y-8 pb-12 pt-6 px-4">
      
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
          <Sparkles className="w-7 h-7 text-primary animate-pulse" />
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500 pb-1">
            Learning & Projects
          </h1>
        </div>
        <p className="text-muted-foreground text-lg max-w-xl mx-auto">
          Master the missing competencies identified by the AI matching engine.
        </p>
      </motion.div>

      <AnimatePresence mode="wait">
        {/* Loading State with Energy Pulse */}
        {loading && (
          <motion.div
            key="loading"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="h-80 flex flex-col items-center justify-center relative"
          >
            <div className="relative flex items-center justify-center mb-6">
              <motion.div
                className="absolute w-20 h-20 border-4 border-primary/20 border-t-primary rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
              />
              <motion.div
                className="absolute w-14 h-14 border-4 border-blue-500/20 border-b-blue-500 rounded-full"
                animate={{ rotate: -360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              />
              <Loader2 className="w-6 h-6 text-primary animate-pulse" />
            </div>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500 tracking-widest text-sm uppercase font-bold animate-pulse">
              Synthesizing Learning Paths...
            </span>
          </motion.div>
        )}

        {/* Error State */}
        {error && !loading && (
          <motion.div
            key="error"
            initial={{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}
            animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
            className="glass rounded-3xl p-12 flex flex-col items-center justify-center text-center border border-red-500/20 shadow-2xl max-w-2xl mx-auto w-full"
          >
            <motion.div 
              initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", bounce: 0.6 }}
              className="w-20 h-20 rounded-full bg-red-500/10 flex items-center justify-center mb-6 border-2 border-red-500/30 shadow-[0_0_20px_rgba(239,68,68,0.2)]"
            >
              <AlertTriangle className="w-10 h-10 text-red-500" />
            </motion.div>
            <h3 className="text-2xl font-bold mb-3">Failed to Load Recommendations</h3>
            <p className="text-muted-foreground mb-3 max-w-md">{error}</p>
            <p className="text-sm text-muted-foreground/60 mb-8 font-medium">Make sure you have uploaded a resume first.</p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => window.location.reload()}
              className="px-8 py-4 bg-primary text-primary-foreground rounded-xl text-md font-bold shadow-lg shadow-primary/20 transition-colors hover:bg-primary/90"
            >
              Initialize Retry Sequence
            </motion.button>
          </motion.div>
        )}

        {/* Success State */}
        {recommendations && !loading && (
          <motion.div
            key="content"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-10 w-full"
          >
            {Object.entries(recommendations).map(([skill, resources], idx) => (
              <TiltCard key={skill} delay={idx * 0.1}>
                <div className="glass-panel rounded-3xl p-8 lg:p-10 border border-primary/10 shadow-xl bg-background/50 backdrop-blur-md relative overflow-hidden group">
                  
                  {/* Hover Scan Effect */}
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-[scan_2s_ease-in-out_infinite] pointer-events-none" />

                  {/* Header */}
                  <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4 border-b border-border/50 pb-6">
                    <div>
                      <h2 className="text-3xl font-extrabold text-foreground flex items-center tracking-tight">
                        <div className="p-2 bg-primary/10 rounded-lg mr-4 border border-primary/20 shadow-inner">
                          <BookOpen className="w-7 h-7 text-primary" />
                        </div>
                        {skill}
                      </h2>
                      <p className="text-muted-foreground mt-3 text-sm md:text-base font-medium ml-1">
                        Curated neural pathways for mastering <span className="text-primary">{skill}</span>
                      </p>
                    </div>

                    <div className="self-start md:self-auto px-5 py-2.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-bold tracking-wide shadow-sm flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      Skill Path Active
                    </div>
                  </div>

                  {/* Resource Sections */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Coursera */}
                    <div className="glass rounded-2xl p-6 border border-border/50 hover:border-primary/30 transition-colors bg-background/40">
                      <div className="flex items-center mb-6">
                        <PlayCircle className="w-6 h-6 text-blue-500 mr-3" />
                        <h3 className="font-bold text-xl tracking-tight">Coursera</h3>
                      </div>
                      <div className="space-y-4">
                        {resources.coursera?.map((course, i) => (
                          <div
                            key={i}
                            className="p-4 rounded-xl bg-background/60 border border-border/50 hover:shadow-md hover:-translate-y-1 transition-all duration-300 group/item"
                          >
                            <p className="text-sm font-medium leading-relaxed group-hover/item:text-primary transition-colors">
                              {course}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Udemy */}
                    <div className="glass rounded-2xl p-6 border border-border/50 hover:border-primary/30 transition-colors bg-background/40">
                      <div className="flex items-center mb-6">
                        <BookOpen className="w-6 h-6 text-purple-500 mr-3" />
                        <h3 className="font-bold text-xl tracking-tight">Udemy</h3>
                      </div>
                      <div className="space-y-4">
                        {resources.udemy?.map((course, i) => (
                          <div
                            key={i}
                            className="p-4 rounded-xl bg-background/60 border border-border/50 hover:shadow-md hover:-translate-y-1 transition-all duration-300 group/item"
                          >
                            <p className="text-sm font-medium leading-relaxed group-hover/item:text-purple-500 transition-colors">
                              {course}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* GitHub */}
                    <div className="glass rounded-2xl p-6 border border-border/50 hover:border-primary/30 transition-colors bg-background/40">
                      <div className="flex items-center mb-6">
                        <TerminalSquare className="w-6 h-6 text-foreground mr-3" />
                        <h3 className="font-bold text-xl tracking-tight">GitHub Projects</h3>
                      </div>
                      <div className="space-y-4">
                        {resources.github_projects?.map((repo, i) => (
                          <a
                            key={i}
                            href={`https://github.com/${repo}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block p-4 rounded-xl bg-background/60 border border-border/50 hover:border-primary hover:bg-primary/5 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group/link"
                          >
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-bold text-foreground group-hover/link:text-primary transition-colors truncate pr-4">
                                {repo}
                              </p>
                              <ArrowRight className="w-4 h-4 text-primary opacity-50 group-hover/link:opacity-100 group-hover/link:translate-x-1 transition-all flex-shrink-0" />
                            </div>
                          </a>
                        ))}
                      </div>
                    </div>

                  </div>
                </div>
              </TiltCard>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Styles for internal scan animation */}
      <style jsx global>{`
        @keyframes scan {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(100%); }
        }
      `}</style>
    </div>
  );
}