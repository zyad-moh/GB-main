"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import {
  Target,
  Code,
  Loader2,
  AlertTriangle,
  Zap,
  TerminalSquare,
} from "lucide-react";

const API_BASE = "https://gb-main-production.up.railway.app";

// مكون فرعي لإضافة تأثير 3D حقيقي ومستقل لكل بطاقة مهارة
const TiltCard = ({ children, delay = 0 }) => {
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // حساب زاوية الميلان (حد أقصى 15 درجة للبطاقات الصغيرة ليكون التأثير واضحاً)
    const rotateX = (y / rect.height - 0.5) * -15;
    const rotateY = (x / rect.width - 0.5) * 15;

    setTilt({ x: rotateX, y: rotateY });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{
        opacity: 1,
        y: 0,
        scale: 1,
        rotateX: tilt.x,
        rotateY: tilt.y,
      }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{
        type: "spring",
        stiffness: 400,
        damping: 25,
        opacity: { delay },
        y: { delay },
        scale: { delay },
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ transformStyle: "preserve-3d", perspective: "1000px" }}
      className="w-full will-change-transform h-full"
    >
      <div style={{ transform: "translateZ(30px)" }} className="h-full">
        {children}
      </div>
    </motion.div>
  );
};

export default function SkillGapPage() {
  const [gapData, setGapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchGapSkills() {
      const projectId = localStorage.getItem("project_id");
      try {
        const res = await fetch(
          `${API_BASE}/api/v1/nlp/index/retun_gap_skills/${projectId}`,
          {
            headers: { accept: "application/json" },
          },
        );

        if (!res.ok) {
          throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();
        setGapData(data);
      } catch (err) {
        console.error("retun_gap_skills error:", err);
        setError(err.message || "Failed to fetch gap skills.");
      } finally {
        setLoading(false);
      }
    }

    fetchGapSkills();
  }, []);

  // Helper: try to extract radar-compatible data from API response (Kept for your future use)
  const extractRadarData = (data) => {
    if (!data) return [];
    if (Array.isArray(data)) {
      return data.map((item, i) => ({
        subject: item.subject || item.skill || item.name || `Skill ${i + 1}`,
        A: item.A || item.current || item.your_level || item.score || 0,
        B: item.B || item.target || item.required || item.benchmark || 100,
        fullMark: 100,
      }));
    }
    if (data.radarData) return extractRadarData(data.radarData);
    if (data.data) return extractRadarData(data.data);
    if (data.skills) return extractRadarData(data.skills);
    if (data.gaps) return extractRadarData(data.gaps);
    if (typeof data === "object" && !Array.isArray(data)) {
      return Object.entries(data).map(([key, value]) => ({
        subject: key,
        A:
          typeof value === "number" ? value : value.current || value.score || 0,
        B:
          typeof value === "number"
            ? 100
            : value.target || value.required || 100,
        fullMark: 100,
      }));
    }
    return [];
  };

  return (
    <div className="min-h-screen flex flex-col max-w-6xl mx-auto space-y-8 pb-12 pt-6 px-4">
      {/* Floating Header */}
      <motion.div
        className="w-full text-center z-10"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: [0, -8, 0] }}
        transition={{
          opacity: { duration: 0.8 },
          y: { duration: 4, repeat: Infinity, ease: "easeInOut" },
        }}
      >
        <div className="inline-flex items-center justify-center space-x-3 mb-3">
          <Target className="w-8 h-8 text-primary animate-pulse" />
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500 pb-1">
            Skill Gap Detector
          </h1>
        </div>
        <p className="text-muted-foreground text-lg max-w-xl mx-auto">
          Identify exact missing competencies relative to your target industry
          baseline.
        </p>
      </motion.div>

      <AnimatePresence mode="wait">
        {/* Loading State */}
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
              Analyzing Competency Gaps...
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
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", bounce: 0.6 }}
              className="w-20 h-20 rounded-full bg-red-500/10 flex items-center justify-center mb-6 border-2 border-red-500/30 shadow-[0_0_20px_rgba(239,68,68,0.2)]"
            >
              <AlertTriangle className="w-10 h-10 text-red-500" />
            </motion.div>
            <h3 className="text-2xl font-bold mb-3">
              Failed to Load Gap Analysis
            </h3>
            <p className="text-muted-foreground mb-3 max-w-md">{error}</p>
            <p className="text-sm text-muted-foreground/60 mb-8 font-medium">
              Make sure you have uploaded a resume first.
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => window.location.reload()}
              className="px-8 py-4 bg-primary text-primary-foreground rounded-xl text-md font-bold shadow-lg shadow-primary/20 transition-colors hover:bg-primary/90"
            >
              Retry Analysis
            </motion.button>
          </motion.div>
        )}

        {/* Success State */}
        {gapData && !loading && (
          <motion.div
            key="content"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel rounded-3xl p-8 md:p-10 border border-primary/10 shadow-xl bg-background/50 backdrop-blur-md relative overflow-hidden"
          >
            {/* Ambient Background Glow */}
            <div className="absolute -top-32 -right-32 w-64 h-64 bg-primary/10 rounded-full blur-3xl pointer-events-none" />

            <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-10 border-b border-border/50 pb-6 relative z-10">
              <div className="flex items-center">
                <div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mr-5 shadow-inner">
                  <Zap className="w-7 h-7 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl md:text-3xl font-extrabold text-foreground tracking-tight">
                    Missing Skills
                  </h2>
                  <p className="text-muted-foreground text-sm font-medium mt-1">
                    Detected competency gaps relative to your target role.
                  </p>
                </div>
              </div>

              <div className="mt-4 md:mt-0 px-4 py-2 bg-background/60 border border-border rounded-lg text-xs font-bold text-muted-foreground flex items-center shadow-sm">
                <TerminalSquare className="w-4 h-4 mr-2 text-primary" />
                {gapData.length} Gaps Detected
              </div>
            </div>

            {/* Skills Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5 relative z-10">
              {gapData.map((skill, index) => (
                <TiltCard key={index} delay={index * 0.05}>
                  <div className="group h-full border border-primary/10 bg-background/40 hover:bg-gradient-to-b hover:from-primary/10 hover:to-primary/5 hover:border-primary/30 transition-all duration-300 rounded-2xl px-5 py-6 flex flex-col items-center justify-center text-center shadow-sm hover:shadow-lg hover:shadow-primary/5 cursor-default relative overflow-hidden">
                    {/* Inner subtle glow on hover */}
                    <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

                    <div className="p-3 bg-background/80 rounded-full mb-4 border border-border/50 group-hover:border-primary/30 transition-colors">
                      <Code className="w-6 h-6 text-primary/80 group-hover:text-primary transition-colors" />
                    </div>

                    <span className="font-bold text-sm text-foreground/90 group-hover:text-foreground tracking-wide leading-tight">
                      {skill}
                    </span>
                  </div>
                </TiltCard>
              ))}
            </div>

            {/* Empty State Fallback */}
            {gapData.length === 0 && (
              <div className="py-12 text-center flex flex-col items-center justify-center">
                <Target className="w-12 h-12 text-primary/40 mb-4" />
                <h3 className="text-xl font-bold text-foreground">
                  Perfect Match!
                </h3>
                <p className="text-muted-foreground mt-2">
                  No skill gaps detected for this profile.
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
