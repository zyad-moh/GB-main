"use client";

import { useState, useEffect, useRef } from "react";
import { motion, useInView, useMotionValue, useTransform, animate } from "framer-motion";
import Link from "next/link";
import { ThemeToggle } from "@/components/ThemeToggle";
import {
  Briefcase,
  Cpu,
  FileSearch,
  Target,
  Zap,
  BookOpen,
  Brain,
  ArrowRight,
  ChevronDown,
  Upload,
  BarChart3,
  ShieldCheck,
  TrendingUp,
  Sparkles,
  MessageSquare,
  ClipboardCheck,
  Award,
  ExternalLink,
  Menu,
  X,
} from "lucide-react";

/* ───────── Animated Counter ───────── */
function AnimatedCounter({ target, suffix = "", duration = 2 }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const count = useMotionValue(0);
  const rounded = useTransform(count, (v) => Math.floor(v).toLocaleString());
  const [display, setDisplay] = useState("0");

  useEffect(() => {
    if (!isInView) return;
    const controls = animate(count, target, { duration, ease: "easeOut" });
    const unsub = rounded.on("change", (v) => setDisplay(v));
    return () => { controls.stop(); unsub(); };
  }, [isInView, target, count, rounded, duration]);

  return (
    <span ref={ref}>
      {display}{suffix}
    </span>
  );
}

/* ───────── Floating Particle ───────── */
function FloatingParticle({ size, x, y, delay, duration }) {
  return (
    <motion.div
      className="absolute rounded-full bg-primary/20 blur-sm"
      style={{ width: size, height: size }}
      initial={{ x, y, opacity: 0 }}
      animate={{
        x: [x, x + 40, x - 30, x],
        y: [y, y - 60, y + 30, y],
        opacity: [0, 0.6, 0.4, 0],
      }}
      transition={{ duration, repeat: Infinity, delay, ease: "easeInOut" }}
    />
  );
}

/* ───────── Section Wrapper with Animate on Scroll ───────── */
function Section({ children, className = "", id }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <motion.section
      ref={ref}
      id={id}
      initial={{ opacity: 0, y: 60 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.7, ease: "easeOut" }}
      className={className}
    >
      {children}
    </motion.section>
  );
}

/* ═══════════ MAIN HOME PAGE ═══════════ */
export default function Home() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const container = document.querySelector(".landing-wrapper") || window;
    const handleScroll = () => {
      const top = container === window ? window.scrollY : container.scrollTop;
      setScrolled(top > 20);
    };
    container.addEventListener("scroll", handleScroll, { passive: true });
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  /* ─── Data ─── */
  const features = [
    { icon: FileSearch, title: "Resume Analysis", desc: "Deep AI-powered analysis of your resume structure, content quality, and keyword optimization." },
    { icon: ShieldCheck, title: "ATS Optimization", desc: "Ensure your resume passes Applicant Tracking Systems with smart formatting and keyword alignment." },
    { icon: Target, title: "Skill Gap Detection", desc: "Identify missing skills by comparing your profile against industry requirements and job postings." },
    { icon: BookOpen, title: "Learning Recommendations", desc: "Get curated courses, projects, and resources tailored to bridge your identified skill gaps." },
    { icon: Briefcase, title: "Job Matching", desc: "AI-matched job opportunities ranked by compatibility with your skills, experience, and goals." },
    { icon: Brain, title: "AI Interview Agent", desc: "Practice with an intelligent interviewer that adapts questions based on your target role and resume." },
  ];

  const workflow = [
    { icon: Upload, title: "Upload Resume", desc: "Drop your resume and let the engine begin." },
    { icon: FileSearch, title: "Resume Analysis", desc: "AI parses structure and content quality." },
    { icon: ShieldCheck, title: "ATS Evaluation", desc: "Score against tracking system standards." },
    { icon: Target, title: "Skill Gap Detection", desc: "Compare skills to market demands." },
    { icon: BookOpen, title: "Learning Recommendations", desc: "Curated courses to fill gaps." },
    { icon: Briefcase, title: "Job Matching", desc: "Find roles that fit your profile." },
    { icon: Brain, title: "AI Interview", desc: "Practice with adaptive AI interviewer." },
    { icon: TrendingUp, title: "Career Growth", desc: "Track progress and level up." },
  ];

  const interviewFeatures = [
    { icon: MessageSquare, title: "Automated Interview Questions", desc: "AI generates role-specific questions from your resume and target position." },
    { icon: Cpu, title: "AI Evaluation", desc: "Real-time assessment of your answers with detailed scoring metrics." },
    { icon: ClipboardCheck, title: "Performance Reports", desc: "Comprehensive reports highlighting strengths, weaknesses, and improvement areas." },
    { icon: Award, title: "Personalized Feedback", desc: "Actionable tips and best-practice responses tailored to your experience level." },
  ];

  const stats = [
    { value: 12400, label: "Resumes Analyzed", suffix: "+" },
    { value: 8600, label: "Jobs Matched", suffix: "+" },
    { value: 34200, label: "Skill Gaps Detected", suffix: "+" },
    { value: 5800, label: "AI Interviews Conducted", suffix: "+" },
  ];

  /* ─── Animations ─── */
  const fadeUp = { hidden: { opacity: 0, y: 30 }, visible: (i = 0) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.6 } }) };
  const stagger = { hidden: {}, visible: { transition: { staggerChildren: 0.1 } } };

  return (
    <div className="relative">
      {/* ───────── NAVBAR ───────── */}
      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 120, damping: 20 }}
        className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-300 ${
          scrolled
            ? "glass border-b border-border/40 shadow-lg shadow-primary/5"
            : "bg-transparent"
        }`}
      >
        <div className="container mx-auto max-w-7xl px-4 md:px-8 h-16 md:h-20 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center group-hover:bg-primary/20 transition-all shadow-[0_0_15px_rgba(0,240,255,0.2)]">
              <Cpu className="w-5 h-5 text-primary" />
            </div>
            <span className="text-lg font-bold tracking-tight text-foreground">
              AI Career <span className="text-primary">Coach</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-3">
            <ThemeToggle />
            <Link
              href="/login"
              className="px-5 py-2.5 rounded-xl border border-primary/40 text-primary font-semibold text-sm hover:bg-primary/10 transition-all duration-300 hover:border-primary/70 hover:shadow-[0_0_20px_rgba(0,240,255,0.15)]"
            >
              Login
            </Link>
            <Link
              href="/signup"
              className="px-5 py-2.5 rounded-xl bg-primary text-primary-foreground font-semibold text-sm hover:opacity-90 transition-all duration-300 shadow-lg shadow-primary/25 hover:shadow-primary/40 hover:-translate-y-0.5"
            >
              Sign Up
            </Link>
          </div>

          {/* Mobile Menu Toggle */}
          <div className="flex md:hidden items-center space-x-2">
            <ThemeToggle />
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-foreground hover:bg-primary/10 transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass border-t border-border/40"
          >
            <div className="container mx-auto px-4 py-4 flex flex-col space-y-3">
              <Link href="/login" onClick={() => setMobileMenuOpen(false)} className="w-full py-3 rounded-xl border border-primary/40 text-primary font-semibold text-sm text-center hover:bg-primary/10 transition-all">
                Login
              </Link>
              <Link href="/signup" onClick={() => setMobileMenuOpen(false)} className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-sm text-center hover:opacity-90 transition-all shadow-lg shadow-primary/25">
                Sign Up
              </Link>
            </div>
          </motion.div>
        )}
      </motion.nav>

      {/* ───────── HERO ───────── */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
        {/* Background Effects */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          {/* Gradient Orbs */}
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-accent/10 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: "1s" }} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[150px]" />

          {/* Grid Pattern */}
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: `linear-gradient(var(--primary) 1px, transparent 1px), linear-gradient(90deg, var(--primary) 1px, transparent 1px)`,
              backgroundSize: "60px 60px",
            }}
          />

          {/* Floating Particles */}
          <FloatingParticle size={8} x={100} y={200} delay={0} duration={6} />
          <FloatingParticle size={6} x={300} y={100} delay={1} duration={8} />
          <FloatingParticle size={10} x={600} y={300} delay={2} duration={7} />
          <FloatingParticle size={5} x={800} y={150} delay={0.5} duration={9} />
          <FloatingParticle size={7} x={200} y={400} delay={3} duration={6} />
          <FloatingParticle size={9} x={700} y={500} delay={1.5} duration={8} />
        </div>

        <div className="relative z-10 container mx-auto max-w-5xl px-4 md:px-8 text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-full glass border border-primary/20 mb-8"
          >
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary">Powered by Advanced AI</span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="text-4xl sm:text-5xl md:text-7xl font-extrabold tracking-tight leading-tight mb-6"
          >
            <span className="text-foreground">Welcome to </span>
            <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-accent to-primary bg-[length:200%_auto] animate-[gradient-shift_3s_linear_infinite]">
              AI Career Coach
            </span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Your intelligent career companion for resume optimization, skill development, job matching, and AI-powered interview preparation.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.6 }}
            className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4"
          >
            <Link
              href="/signup"
              className="group px-8 py-4 rounded-2xl bg-primary text-primary-foreground font-bold text-base shadow-xl shadow-primary/25 hover:shadow-primary/40 hover:-translate-y-1 transition-all duration-300 flex items-center space-x-2"
            >
              <span>Get Started</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <a
              href="#features"
              className="group px-8 py-4 rounded-2xl border border-primary/30 text-foreground font-bold text-base hover:bg-primary/5 hover:border-primary/60 transition-all duration-300 flex items-center space-x-2 hover:shadow-[0_0_30px_rgba(0,240,255,0.1)]"
            >
              <span>Explore Features</span>
              <ChevronDown className="w-5 h-5 group-hover:translate-y-1 transition-transform" />
            </a>
          </motion.div>

          {/* Glowing Line */}
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 1.5, delay: 1 }}
            className="mt-16 mx-auto w-full max-w-md h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent"
          />
        </div>
      </section>

      {/* ───────── FEATURES ───────── */}
      <Section id="features" className="py-24 md:py-32 px-4 md:px-8">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <motion.span variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} className="inline-block text-primary text-sm font-bold uppercase tracking-widest mb-4">
              Platform Features
            </motion.span>
            <motion.h2 variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={1} className="text-3xl md:text-5xl font-extrabold tracking-tight text-foreground mb-4">
              Everything You Need to <span className="text-primary">Accelerate</span> Your Career
            </motion.h2>
            <motion.p variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={2} className="text-muted-foreground text-lg max-w-2xl mx-auto">
              A comprehensive suite of AI-powered tools designed to optimize every stage of your career journey.
            </motion.p>
          </div>

          <motion.div
            variants={stagger}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-60px" }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {features.map((f, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                custom={i}
                whileHover={{ y: -8, scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300, damping: 25 }}
                className="group glass-panel rounded-3xl p-8 border border-primary/10 hover:border-primary/30 transition-all duration-300 hover:shadow-[0_0_40px_rgba(0,240,255,0.08)] cursor-default"
              >
                <div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mb-5 group-hover:bg-primary/20 group-hover:border-primary/40 transition-all group-hover:shadow-[0_0_20px_rgba(0,240,255,0.2)]">
                  <f.icon className="w-7 h-7 text-primary" />
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </Section>

      {/* ───────── HOW IT WORKS ───────── */}
      <Section id="how-it-works" className="py-24 md:py-32 px-4 md:px-8 relative">
        {/* Background accent */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-0 w-full h-px bg-gradient-to-r from-transparent via-primary/10 to-transparent" />
        </div>

        <div className="container mx-auto max-w-5xl relative z-10">
          <div className="text-center mb-16">
            <motion.span variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} className="inline-block text-primary text-sm font-bold uppercase tracking-widest mb-4">
              Workflow
            </motion.span>
            <motion.h2 variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={1} className="text-3xl md:text-5xl font-extrabold tracking-tight text-foreground mb-4">
              How It <span className="text-primary">Works</span>
            </motion.h2>
            <motion.p variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={2} className="text-muted-foreground text-lg max-w-xl mx-auto">
              From resume upload to career growth — a seamless, AI-driven pipeline.
            </motion.p>
          </div>

          <div className="relative">
            {/* Vertical Timeline Line */}
            <div className="absolute left-6 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-primary/40 via-primary/20 to-transparent hidden sm:block" />

            {workflow.map((step, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-40px" }}
                custom={i}
                className={`relative flex items-start mb-10 last:mb-0 ${
                  i % 2 === 0 ? "md:flex-row" : "md:flex-row-reverse"
                }`}
              >
                {/* Timeline Node */}
                <div className="absolute left-6 md:left-1/2 -translate-x-1/2 z-10">
                  <motion.div
                    whileInView={{ scale: [0, 1.2, 1] }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1, duration: 0.5 }}
                    className="w-12 h-12 rounded-full bg-primary/10 border-2 border-primary/40 flex items-center justify-center shadow-[0_0_20px_rgba(0,240,255,0.2)]"
                  >
                    <step.icon className="w-5 h-5 text-primary" />
                  </motion.div>
                </div>

                {/* Content Card */}
                <div className={`ml-20 sm:ml-20 md:ml-0 md:w-[calc(50%-40px)] ${i % 2 === 0 ? "md:pr-12 md:text-right" : "md:pl-12 md:text-left"}`}>
                  <div className="glass-panel rounded-2xl p-5 border border-primary/10 hover:border-primary/30 transition-all duration-300 hover:shadow-[0_0_30px_rgba(0,240,255,0.06)]">
                    <span className="text-xs font-bold text-primary uppercase tracking-wider">Step {i + 1}</span>
                    <h3 className="text-base font-bold text-foreground mt-1">{step.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{step.desc}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* ───────── AI INTERVIEW HIGHLIGHT ───────── */}
      <Section id="interview" className="py-24 md:py-32 px-4 md:px-8 relative overflow-hidden">
        {/* Premium Background */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-primary/8 rounded-full blur-[150px]" />
          <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-accent/5 rounded-full blur-[120px]" />
        </div>

        <div className="container mx-auto max-w-7xl relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left — Text */}
            <div>
              <motion.span variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} className="inline-block text-primary text-sm font-bold uppercase tracking-widest mb-4">
                Premium Feature
              </motion.span>
              <motion.h2 variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={1} className="text-3xl md:text-5xl font-extrabold tracking-tight text-foreground mb-6 leading-tight">
                AI Interview <span className="text-primary">Agent</span>
              </motion.h2>
              <motion.p variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={2} className="text-muted-foreground text-lg leading-relaxed mb-8">
                Our most advanced feature — an intelligent interviewer that simulates real-world interviews, evaluates your responses in real-time, and provides actionable insights to boost your confidence and performance.
              </motion.p>
              <motion.div variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={3}>
                <Link
                  href="/signup"
                  className="group inline-flex items-center space-x-2 px-8 py-4 rounded-2xl bg-primary text-primary-foreground font-bold shadow-xl shadow-primary/25 hover:shadow-primary/40 hover:-translate-y-1 transition-all duration-300"
                >
                  <span>Try AI Interview</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </motion.div>
            </div>

            {/* Right — Feature Cards */}
            <motion.div
              variants={stagger}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-60px" }}
              className="grid grid-cols-1 sm:grid-cols-2 gap-5"
            >
              {interviewFeatures.map((f, i) => (
                <motion.div
                  key={i}
                  variants={fadeUp}
                  custom={i}
                  whileHover={{ y: -6, scale: 1.03 }}
                  transition={{ type: "spring", stiffness: 300, damping: 25 }}
                  className="group glass-panel rounded-2xl p-6 border border-primary/10 hover:border-primary/30 transition-all duration-300 hover:shadow-[0_0_40px_rgba(0,240,255,0.1)]"
                >
                  <div className="w-12 h-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center mb-4 group-hover:bg-primary/20 group-hover:shadow-[0_0_15px_rgba(0,240,255,0.25)] transition-all">
                    <f.icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-sm font-bold text-foreground mb-1">{f.title}</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">{f.desc}</p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </Section>

      {/* ───────── STATISTICS ───────── */}
      <Section id="stats" className="py-24 md:py-32 px-4 md:px-8">
        <div className="container mx-auto max-w-5xl">
          <div className="glass-panel rounded-3xl p-10 md:p-16 border border-primary/10 relative overflow-hidden">
            {/* Glow */}
            <div className="absolute inset-0 pointer-events-none">
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-4 relative z-10">
              {stats.map((stat, i) => (
                <motion.div
                  key={i}
                  variants={fadeUp}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  custom={i}
                  className="text-center"
                >
                  <div className="text-3xl md:text-4xl font-extrabold text-primary mb-2">
                    <AnimatedCounter target={stat.value} suffix={stat.suffix} duration={2.5} />
                  </div>
                  <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </Section>

      {/* ───────── CTA SECTION ───────── */}
      <Section className="py-24 md:py-32 px-4 md:px-8">
        <div className="container mx-auto max-w-3xl text-center">
          <motion.h2 variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} className="text-3xl md:text-5xl font-extrabold tracking-tight text-foreground mb-6">
            Ready to <span className="text-primary">Transform</span> Your Career?
          </motion.h2>
          <motion.p variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={1} className="text-muted-foreground text-lg mb-10 max-w-xl mx-auto">
            Join thousands of professionals using AI to unlock their full career potential.
          </motion.p>
          <motion.div variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }} custom={2}>
            <Link
              href="/signup"
              className="group inline-flex items-center space-x-2 px-10 py-5 rounded-2xl bg-primary text-primary-foreground font-bold text-lg shadow-xl shadow-primary/25 hover:shadow-primary/40 hover:-translate-y-1 transition-all duration-300"
            >
              <span>Get Started Free</span>
              <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>
        </div>
      </Section>

      {/* ───────── FOOTER ───────── */}
      <footer className="border-t border-border/40 py-12 px-4 md:px-8">
        <div className="container mx-auto max-w-7xl">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
            {/* Brand */}
            <div className="md:col-span-2">
              <Link href="/" className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center shadow-[0_0_15px_rgba(0,240,255,0.2)]">
                  <Cpu className="w-5 h-5 text-primary" />
                </div>
                <span className="text-lg font-bold tracking-tight text-foreground">
                  AI Career <span className="text-primary">Coach</span>
                </span>
              </Link>
              <p className="text-sm text-muted-foreground max-w-sm leading-relaxed">
                Your intelligent career companion — powered by advanced AI to optimize every step of your professional journey.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="text-sm font-bold text-foreground uppercase tracking-wider mb-4">Platform</h4>
              <ul className="space-y-2">
                {[
                  { label: "About", href: "#" },
                  { label: "Features", href: "#features" },
                  { label: "How It Works", href: "#how-it-works" },
                  { label: "Interview Agent", href: "#interview" },
                ].map((link) => (
                  <li key={link.label}>
                    <a href={link.href} className="text-sm text-muted-foreground hover:text-primary transition-colors">
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Connect */}
            <div>
              <h4 className="text-sm font-bold text-foreground uppercase tracking-wider mb-4">Connect</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">Contact</a>
                </li>
                <li>
                  <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-primary transition-colors inline-flex items-center space-x-1">
                    <ExternalLink className="w-4 h-4" />
                    <span>GitHub</span>
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-border/40 pt-6 flex flex-col md:flex-row justify-between items-center text-sm text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} AI Career Coach. All rights reserved.</p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <span className="hover:text-primary cursor-pointer transition-colors">Privacy Policy</span>
              <span className="hover:text-primary cursor-pointer transition-colors">Terms of Service</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
