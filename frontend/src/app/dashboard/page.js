"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  PlusCircle,
  LayoutDashboard,
  FileSearch,
  Briefcase,
  Target,
  Zap,
  BookOpen,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import Link from "next/link";

const API_BASE = "https://gb-main-production.up.railway.app";

// مكون فرعي لإضافة تأثير 3D حقيقي ومستقل
const TiltCard = ({ children, delay = 0, tiltForce = 15 }) => {
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const rotateX = (y / rect.height - 0.5) * -tiltForce;
    const rotateY = (x / rect.width - 0.5) * tiltForce;
    
    setTilt({ x: rotateX, y: rotateY });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ 
        opacity: 1, 
        y: 0, 
        rotateX: tilt.x,
        rotateY: tilt.y
      }}
      transition={{ 
        type: "spring", 
        stiffness: 400, 
        damping: 30,
        opacity: { delay },
        y: { delay }
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ transformStyle: "preserve-3d", perspective: "1500px" }}
      className="w-full h-full will-change-transform cursor-pointer"
    >
      <div style={{ transform: "translateZ(20px)" }} className="h-full">
        {children}
      </div>
    </motion.div>
  );
};

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState({
    atsScore: 0,
    gapsCount: 0,
    loading: true,
    error: null,
  });

  useEffect(() => {
    async function fetchDashboardStats() {
      const projectId = localStorage.getItem("project_id");
      
      if (!projectId) {
        setDashboardData(prev => ({ ...prev, loading: false, error: "No Project ID found." }));
        return;
      }

      try {
        // جلب المهارات المفقودة (نفس الرابط من الكود السابق)
        const gapsReq = fetch(`${API_BASE}/api/v1/nlp/index/retun_gap_skills/${projectId}`, {
          headers: { accept: "application/json" }
        });

        // جلب درجة الـ ATS (يرجى التأكد من الرابط هنا إذا كان مختلفاً عن ats_score)
        const atsReq = fetch(`${API_BASE}/api/v1/nlp/index/ats_score/${projectId}`, {
          headers: { accept: "application/json" }
        }).catch(() => null); // نمنع توقف التنفيذ إذا فشل هذا الرابط

        const [gapsRes, atsRes] = await Promise.all([gapsReq, atsReq]);

        let gapsCount = 0;
        let atsScore = 0;

        if (gapsRes.ok) {
          const gapsData = await gapsRes.json();
          // حساب عدد المهارات المفقودة بناءً على شكل الرد
          gapsCount = Array.isArray(gapsData) ? gapsData.length : 
                      (gapsData?.data?.length || Object.keys(gapsData || {}).length || 0);
        }

        if (atsRes && atsRes.ok) {
          const atsData = await atsRes.json();
          atsScore = typeof atsData === "number" ? atsData : (atsData?.score || atsData?.ats_score || 0);
        }

        setDashboardData({
          atsScore,
          gapsCount,
          loading: false,
          error: null
        });

      } catch (err) {
        console.error("Dashboard data fetch error:", err);
        setDashboardData(prev => ({
          ...prev,
          loading: false,
          error: err.message || "Failed to load dashboard metrics"
        }));
      }
    }

    fetchDashboardStats();
  }, []);

  const routes = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "CV Analyzer", path: "/cv-analyzer", icon: FileSearch },
    { name: "Job Matching", path: "/job-matching", icon: Briefcase },
    { name: "Skill Gap Detector", path: "/skill-gap", icon: Target },
    { name: "Resume Optimizer", path: "/resume-optimizer", icon: Zap },
    { name: "Learning & Projects", path: "/learning", icon: BookOpen },
  ];

  const stats = [
    {
      title: "Average Match Score",
      value: dashboardData.loading ? "..." : `${dashboardData.atsScore}%`,
      desc: "Based on your latest scan",
      color: "text-green-500",
      glowColor: "shadow-green-500/20"
    },
    {
      title: "Identified Gaps",
      value: dashboardData.loading ? "..." : dashboardData.gapsCount,
      desc: "Skills to improve",
      color: "text-red-500",
      glowColor: "shadow-red-500/20"
    },
    {
      title: "Total Resumes Analyzed",
      value: "1",
      desc: "Current Active Session",
      color: "text-blue-500",
      glowColor: "shadow-blue-500/20"
    },
  ];

  return (
    <div className="min-h-screen flex flex-col max-w-7xl mx-auto space-y-8 pb-12 pt-6 px-4">
      {/* Header */}
      <motion.div
        className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 z-10"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500 pb-1">
            Dashboard
          </h1>
          <p className="text-muted-foreground text-lg mt-1 font-medium">
            Welcome back. Track your resume performance and skill growth.
          </p>
        </div>
        <Link
          href="/cv-analyzer"
          className="mt-6 md:mt-0 inline-flex items-center rounded-xl bg-primary px-6 py-3.5 text-sm font-bold text-primary-foreground shadow-lg shadow-primary/20 hover:bg-primary/90 hover:-translate-y-1 transition-all group"
        >
          <PlusCircle className="mr-2 w-5 h-5 group-hover:rotate-90 transition-transform" /> 
          New Analysis
        </Link>
      </motion.div>

      {/* Error Alert */}
      <AnimatePresence>
        {dashboardData.error && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }} 
            animate={{ opacity: 1, height: "auto" }} 
            exit={{ opacity: 0, height: 0 }}
            className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-2xl flex items-center mb-6"
          >
            <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0" />
            <span className="text-sm font-medium">{dashboardData.error}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 relative z-10">
        {stats.map((stat, i) => (
          <TiltCard key={i} delay={i * 0.1} tiltForce={10}>
            <div className={`glass-panel rounded-3xl p-8 flex flex-col h-full border border-primary/10 bg-background/50 backdrop-blur-md shadow-lg transition-shadow hover:${stat.glowColor}`}>
              {dashboardData.loading && (
                <div className="absolute top-6 right-6">
                  <Loader2 className="w-5 h-5 text-muted-foreground animate-spin" />
                </div>
              )}
              
              <h3 className="text-muted-foreground font-bold text-sm tracking-wide uppercase mb-3">
                {stat.title}
              </h3>

              <div className={`text-5xl font-extrabold tracking-tighter ${stat.color} mb-3`}>
                {stat.value}
              </div>

              <p className="text-sm font-medium text-muted-foreground mt-auto">
                {stat.desc}
              </p>
            </div>
          </TiltCard>
        ))}
      </div>

      {/* Quick Navigation Links */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-5 relative z-10">
        {routes.map((route, i) => {
          const Icon = route.icon;

          return (
            <TiltCard key={i} delay={0.2 + (i * 0.05)} tiltForce={15}>
              <Link
                href={route.path}
                className="glass-panel rounded-3xl p-6 flex flex-col items-center justify-center text-center group h-full border border-primary/10 bg-background/40 hover:bg-primary/5 hover:border-primary/30 transition-all shadow-sm hover:shadow-md"
              >
                <div className="p-4 bg-background/80 rounded-2xl mb-4 border border-border/50 group-hover:border-primary/30 group-hover:bg-primary/10 transition-colors">
                  <Icon className="w-7 h-7 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>

                <span className="text-sm font-bold text-foreground/80 group-hover:text-primary transition-colors">
                  {route.name}
                </span>
              </Link>
            </TiltCard>
          );
        })}
      </div>
    </div>
  );
}
