"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bot,
  User,
  Send,
  Loader2,
  Play,
  Calendar,
  Trophy,
  Target,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  XCircle,
  MessageSquare,
  Mail,
  ChevronDown,
  Sparkles,
  RotateCcw,
  Clock,
  Briefcase,
  ExternalLink,
  Video,
} from "lucide-react";
import { interviewApi } from "@/lib/agent_api";

/* ───────── Constants ───────── */
const ROLES = [
  "AI Engineer",
  "Machine Learning Engineer",
  "Backend Engineer",
  "Frontend Developer",
  "Data Analyst",
  "Data Scientist",
  "Full Stack Developer",
  "DevOps Engineer",
];
const DIFFICULTIES = ["Junior", "Mid-Level", "Senior"];
const TYPES = ["Technical", "Behavioral", "Mixed"];

/* ───────── Bold Text Renderer ───────── */
function RichText({ text }) {
  if (!text) return null;
  return (
    <span>
      {text.split("\n").map((line, i) => (
        <span key={i}>
          {line.split(/(\*\*.*?\*\*)/).map((part, j) =>
            part.startsWith("**") && part.endsWith("**") ? (
              <strong key={j} className="font-semibold">{part.slice(2, -2)}</strong>
            ) : (
              part
            )
          )}
          {i < text.split("\n").length - 1 && <br />}
        </span>
      ))}
    </span>
  );
}

/* ════════════════════════════════════════ */
/*             MAIN PAGE                   */
/* ════════════════════════════════════════ */
export default function AIInterviewAgent() {
  // ── Phase: setup → chatting → report
  const [phase, setPhase] = useState("setup");

  // Setup
  const [role, setRole] = useState(ROLES[0]);
  const [difficulty, setDifficulty] = useState(DIFFICULTIES[1]);
  const [interviewType, setInterviewType] = useState(TYPES[2]);

  // Chat
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [starting, setStarting] = useState(false);
  const [questionInfo, setQuestionInfo] = useState({ current: 0, total: 0 });

  // Report
  const [report, setReport] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);

  // Upcoming Interviews (from MongoDB)
  const [upcomingInterviews, setUpcomingInterviews] = useState([]);
  const [loadingUpcoming, setLoadingUpcoming] = useState(true);

  // Import Email
  const [showImport, setShowImport] = useState(false);
  const [emailText, setEmailText] = useState("");
  const [importing, setImporting] = useState(false);

  const chatEndRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Fetch upcoming interviews on mount
  useEffect(() => {
    fetchUpcoming();
  }, []);

  const fetchUpcoming = async () => {
    setLoadingUpcoming(true);
    try {
      const sessions = await interviewApi.getSessions();
      // Filter to active (not finished) sessions
      if (Array.isArray(sessions)) {
        setUpcomingInterviews(sessions);
      }
    } catch {
      // Silently fail — upcoming is optional
    } finally {
      setLoadingUpcoming(false);
    }
  };

  /* ─── Start Interview ─── */
  const handleStart = async () => {
    setStarting(true);
    try {
      const data = await interviewApi.startPractice({
        role,
        difficulty,
        interview_type: interviewType,
      });
      if (data.error) {
        alert(data.error);
        return;
      }
      setSessionId(data.session_id);
      setQuestionInfo({ current: 1, total: data.total_questions || 7 });
      setMessages([
        {
          sender: "bot",
          text: `Hello! 👋 I'll be conducting your **${difficulty} ${role}** interview today.\nThis will be a **${interviewType.toLowerCase()}** interview with **${data.total_questions || 7} questions**.\n\nLet's begin!\n\n**Question 1:**\n${data.question}`,
        },
      ]);
      setPhase("chatting");
      setReport(null);
    } catch (err) {
      console.error(err);
      alert("Failed to start interview. Is the backend running?");
    } finally {
      setStarting(false);
    }
  };

  /* ─── Send Answer ─── */
  const handleSend = async () => {
    if (!input.trim() || !sessionId || sending) return;
    const currentAnswer = input;
    setInput("");
    setSending(true);
    setMessages((prev) => [...prev, { sender: "user", text: currentAnswer }]);

    try {
      const data = await interviewApi.submitAnswer({
        session_id: sessionId,
        answer: currentAnswer,
      });
      if (data.error) {
        setMessages((prev) => [...prev, { sender: "bot", text: `⚠️ ${data.error}` }]);
        return;
      }

      const parts = [];
      parts.push(data.correct ? "✅ **Correct**" : "❌ **Incorrect**");
      parts.push(`📊 Score: **${data.score ?? 0}/10**`);
      if (data.feedback) parts.push(`💡 ${data.feedback}`);

      const newMsgs = [{ sender: "bot", text: parts.join("\n") }];

      if (data.finished) {
        newMsgs.push({
          sender: "bot",
          text: `🏁 **Interview Complete!**\nTotal Score: **${data.total_score}/${(data.total_questions || 7) * 10}**\n\nGenerating your detailed report...`,
        });
        setPhase("report");
        fetchReport(sessionId);
      } else if (data.next_question) {
        const qNum = data.current || questionInfo.current + 1;
        setQuestionInfo((prev) => ({ ...prev, current: qNum }));
        newMsgs.push({
          sender: "bot",
          text: `**Question ${qNum}:**\n${data.next_question}`,
        });
      }

      setMessages((prev) => [...prev, ...newMsgs]);
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  /* ─── Fetch Report ─── */
  const fetchReport = async (sid) => {
    setLoadingReport(true);
    try {
      const data = await interviewApi.getReport(sid || sessionId);
      if (!data.error) setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingReport(false);
    }
  };

  /* ─── Reset ─── */
  const handleReset = () => {
    setPhase("setup");
    setSessionId(null);
    setMessages([]);
    setReport(null);
    setQuestionInfo({ current: 0, total: 0 });
    setInput("");
    fetchUpcoming();
  };

  /* ─── Import Email ─── */
  const handleImportEmail = async () => {
    if (!emailText.trim()) return;
    setImporting(true);
    try {
      const data = await interviewApi.triggerInterview({
        subject: "Interview Invitation",
        body: emailText,
        from_email: "import@user.com",
      });
      if (data.interview_id) {
        alert(`✅ Interview imported! ID: ${data.interview_id}`);
        setEmailText("");
        setShowImport(false);
        fetchUpcoming();
      }
    } catch {
      alert("Failed to import. Backend may not support this feature.");
    } finally {
      setImporting(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  /* ═══════════════════ RENDER ═══════════════════ */
  return (
    <div className="space-y-6 pb-8">
      {/* ══════ PAGE HEADER ══════ */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-1">
          <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center shadow-[0_0_20px_rgba(0,240,255,0.2)]">
            <Bot className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">
              AI Interview <span className="text-primary">Agent</span>
            </h1>
            <p className="text-muted-foreground text-sm">
              Your AI-powered interview preparation companion
            </p>
          </div>
        </div>
      </motion.div>

      {/* ══════════════════════════════════════════════ */}
      {/*  SETUP PHASE: Practice Setup → Upcoming Below  */}
      {/* ══════════════════════════════════════════════ */}
      {phase === "setup" && (
        <>
          {/* ── SECTION 1: Start Practice Interview (PRIMARY) ── */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-panel rounded-2xl border border-border/50 p-6"
          >
            <div className="flex items-center gap-2 mb-6">
              <Target className="w-5 h-5 text-primary" />
              <h2 className="text-lg font-bold">Start Practice Interview</h2>
            </div>

            <div className="grid gap-5 md:grid-cols-3">
              {/* Role */}
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Target Role
                </label>
                <div className="relative">
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full appearance-none bg-background border border-border rounded-xl px-4 py-3 text-sm font-medium cursor-pointer focus:ring-1 focus:ring-primary/50 focus:border-primary/50 transition-all"
                  >
                    {ROLES.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                </div>
              </div>

              {/* Difficulty */}
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Difficulty Level
                </label>
                <div className="flex gap-2">
                  {DIFFICULTIES.map((d) => (
                    <button
                      key={d}
                      onClick={() => setDifficulty(d)}
                      className={`flex-1 py-3 rounded-xl text-xs font-semibold transition-all border ${
                        difficulty === d
                          ? "bg-primary/15 border-primary/50 text-primary shadow-[0_0_15px_rgba(0,240,255,0.15)]"
                          : "bg-background border-border text-muted-foreground hover:border-primary/30"
                      }`}
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>

              {/* Type */}
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Interview Type
                </label>
                <div className="flex gap-2">
                  {TYPES.map((t) => (
                    <button
                      key={t}
                      onClick={() => setInterviewType(t)}
                      className={`flex-1 py-3 rounded-xl text-xs font-semibold transition-all border ${
                        interviewType === t
                          ? "bg-primary/15 border-primary/50 text-primary shadow-[0_0_15px_rgba(0,240,255,0.15)]"
                          : "bg-background border-border text-muted-foreground hover:border-primary/30"
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Start Button */}
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={handleStart}
              disabled={starting}
              className="mt-6 w-full py-4 rounded-xl bg-primary text-primary-foreground font-bold text-base flex items-center justify-center gap-3 shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all disabled:opacity-50"
            >
              {starting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating Questions...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Start AI Interview
                </>
              )}
            </motion.button>

            <p className="text-xs text-muted-foreground text-center mt-3">
              AI will generate 7 questions tailored to your role and difficulty level
            </p>
          </motion.div>

          {/* ── SECTION 2: Upcoming Interviews + Import (SECONDARY) ── */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid gap-6 lg:grid-cols-2"
          >
            {/* Upcoming Interviews */}
            <div className="glass-panel rounded-2xl border border-border/50 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Calendar className="w-5 h-5 text-primary" />
                <h2 className="text-lg font-bold">Upcoming Interviews</h2>
              </div>

              {loadingUpcoming ? (
                <div className="flex items-center justify-center h-32">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                </div>
              ) : upcomingInterviews.length > 0 ? (
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {upcomingInterviews.map((interview, i) => (
                    <motion.div
                      key={interview.session_id || i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="flex items-center justify-between p-3.5 rounded-xl bg-background/50 border border-border/40 hover:border-primary/30 transition-all"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                          <Briefcase className="w-4 h-4 text-primary" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold">{interview.role}</p>
                          <p className="text-xs text-muted-foreground">
                            {interview.difficulty} • {interview.interview_type}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span
                          className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                            interview.finished
                              ? "bg-green-400/10 text-green-400 border border-green-400/30"
                              : "bg-yellow-400/10 text-yellow-400 border border-yellow-400/30"
                          }`}
                        >
                          {interview.finished ? "Completed" : `${interview.answered}/${interview.total_questions} answered`}
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center h-32 rounded-xl border border-dashed border-border/60 text-muted-foreground text-sm">
                  <div className="text-center">
                    <Clock className="w-8 h-8 mx-auto mb-2 opacity-40" />
                    <p>No upcoming interviews detected.</p>
                    <p className="text-xs mt-1 opacity-60">
                      Start a practice or import an invitation
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Import Email Card */}
            <div className="glass-panel rounded-2xl border border-border/50 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Mail className="w-5 h-5 text-primary" />
                <h2 className="text-lg font-bold">Import Interview Invitation</h2>
              </div>

              <p className="text-sm text-muted-foreground mb-4">
                Paste a real interview email and the AI will extract company, role, date, time, and meeting link automatically.
              </p>

              <textarea
                value={emailText}
                onChange={(e) => setEmailText(e.target.value)}
                placeholder={"Dear Ahmed,\n\nWe'd like to invite you to an interview for the AI Engineer position at Google on June 15, 2026 at 3:00 PM.\n\nMeeting Link: https://meet.google.com/abc-defg-hij\n\nBest regards,\nGoogle HR Team"}
                rows={6}
                className="w-full bg-background border border-border rounded-xl px-4 py-3 text-sm resize-none focus:ring-1 focus:ring-primary/50 focus:border-primary/50 transition-all mb-3"
              />

              <button
                onClick={handleImportEmail}
                disabled={importing || !emailText.trim()}
                className="w-full py-3 rounded-xl bg-primary/10 border border-primary/30 text-primary text-sm font-semibold hover:bg-primary/20 transition-all disabled:opacity-40 flex items-center justify-center gap-2"
              >
                {importing ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                {importing ? "Importing..." : "Import & Create Prep Session"}
              </button>
            </div>
          </motion.div>
        </>
      )}

      {/* ══════════════════════════════════════════════ */}
      {/*  CHATTING / REPORT PHASE: AI Interview Chat   */}
      {/* ══════════════════════════════════════════════ */}
      {(phase === "chatting" || phase === "report") && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel rounded-2xl border border-border/50"
        >
          {/* Chat Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-border/40">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center">
                <MessageSquare className="w-4 h-4 text-primary" />
              </div>
              <div>
                <h2 className="text-base font-bold">AI Interview Chat</h2>
                <p className="text-xs text-muted-foreground">
                  {difficulty} {role} • {interviewType}
                  {questionInfo.total > 0 &&
                    ` • Q${Math.min(questionInfo.current, questionInfo.total)}/${questionInfo.total}`}
                </p>
              </div>
            </div>
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border text-sm text-muted-foreground hover:text-foreground hover:border-primary/30 transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              New Interview
            </button>
          </div>

          {/* Chat Messages */}
          <div className="h-[500px] overflow-y-auto px-6 py-4 flex flex-col gap-4">
            {messages
              .filter((m) => m.text)
              .map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                  className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-5 py-3.5 ${
                      message.sender === "user"
                        ? "bg-primary text-primary-foreground rounded-br-md"
                        : "bg-card border border-border/60 rounded-bl-md"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1.5">
                      {message.sender === "user" ? (
                        <User className="w-3.5 h-3.5" />
                      ) : (
                        <Bot className="w-3.5 h-3.5 text-primary" />
                      )}
                      <span className="text-xs font-semibold opacity-70">
                        {message.sender === "user" ? "You" : "AI Interviewer"}
                      </span>
                    </div>
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">
                      <RichText text={message.text} />
                    </div>
                  </div>
                </motion.div>
              ))}

            {sending && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                <div className="bg-card border border-border/60 rounded-2xl rounded-bl-md px-5 py-3.5 flex items-center gap-3">
                  <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  <span className="text-sm text-muted-foreground">AI is evaluating your answer...</span>
                </div>
              </motion.div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Chat Input */}
          {phase === "chatting" && (
            <div className="px-6 py-4 border-t border-border/40">
              <div className="flex gap-3">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your answer..."
                  disabled={sending}
                  className="flex-1 bg-background border border-border rounded-xl px-4 py-3.5 text-sm focus:ring-1 focus:ring-primary/50 focus:border-primary/50 transition-all disabled:opacity-50"
                />
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSend}
                  disabled={sending || !input.trim()}
                  className="px-6 rounded-xl bg-primary text-primary-foreground flex items-center gap-2 font-semibold text-sm shadow-lg shadow-primary/25 disabled:opacity-40 transition-all"
                >
                  <Send className="w-4 h-4" />
                  Send
                </motion.button>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* ══════════════════════════════════════════════ */}
      {/*  REPORT PHASE: Detailed Interview Report      */}
      {/* ══════════════════════════════════════════════ */}
      {phase === "report" && (
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {loadingReport ? (
            <div className="glass-panel rounded-2xl border border-border/50 p-12 flex flex-col items-center justify-center">
              <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
              <p className="text-muted-foreground font-medium">AI is generating your detailed report...</p>
              <p className="text-xs text-muted-foreground mt-1">Analyzing your answers across all questions</p>
            </div>
          ) : report ? (
            <div className="space-y-6">
              {/* Score Row */}
              <div className="grid gap-4 md:grid-cols-4">
                {/* Overall Score */}
                <div className="glass-panel rounded-2xl border border-border/50 p-6 text-center">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                    Overall Score
                  </p>
                  <div className="relative w-24 h-24 mx-auto mb-3">
                    <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" strokeWidth="8" className="text-border/30" />
                      <circle
                        cx="50" cy="50" r="42" fill="none" stroke="currentColor" strokeWidth="8"
                        strokeDasharray={`${(report.overall_score / 10) * 264} 264`}
                        strokeLinecap="round"
                        className="text-primary"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-2xl font-black">{report.overall_score?.toFixed(1) || "0"}</span>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">out of 10</p>
                </div>

                {/* Decision */}
                <div className="glass-panel rounded-2xl border border-border/50 p-6 text-center flex flex-col items-center justify-center">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Decision</p>
                  <div
                    className={`text-lg font-bold px-4 py-2 rounded-xl ${
                      report.decision === "Strong Hire" || report.decision === "Hire"
                        ? "text-green-400 bg-green-400/10 border border-green-400/30"
                        : report.decision === "Hold"
                          ? "text-yellow-400 bg-yellow-400/10 border border-yellow-400/30"
                          : "text-red-400 bg-red-400/10 border border-red-400/30"
                    }`}
                  >
                    {report.decision || "N/A"}
                  </div>
                </div>

                {/* Readiness */}
                <div className="md:col-span-2 glass-panel rounded-2xl border border-border/50 p-6">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                    Readiness Level
                  </p>
                  <p className="text-base font-semibold text-foreground mb-3">{report.readiness || "N/A"}</p>
                  {report.feedback && (
                    <p className="text-sm text-muted-foreground leading-relaxed">💡 {report.feedback}</p>
                  )}
                </div>
              </div>

              {/* Score Breakdown */}
              {report.scores && Object.keys(report.scores).length > 0 && (
                <div className="glass-panel rounded-2xl border border-border/50 p-6">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                    Score Breakdown
                  </p>
                  <div className="grid gap-3 md:grid-cols-2">
                    {Object.entries(report.scores).map(([key, val]) => (
                      <div key={key} className="flex items-center gap-3">
                        <span className="text-sm text-muted-foreground capitalize w-40">
                          {key.replace(/_/g, " ")}
                        </span>
                        <div className="flex-1 h-2.5 bg-border/30 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${(val / 10) * 100}%` }}
                            transition={{ duration: 1, delay: 0.5 }}
                            className="h-full bg-primary rounded-full"
                          />
                        </div>
                        <span className="text-sm font-semibold w-10 text-right">
                          {typeof val === "number" ? val.toFixed(1) : val}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Strengths & Weaknesses */}
              <div className="grid gap-4 md:grid-cols-2">
                <div className="glass-panel rounded-2xl border border-border/50 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <TrendingUp className="w-5 h-5 text-green-400" />
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Strengths</p>
                  </div>
                  <div className="space-y-2">
                    {(report.strengths || []).map((s, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 shrink-0" />
                        <span>{s}</span>
                      </div>
                    ))}
                    {(!report.strengths || report.strengths.length === 0) && (
                      <p className="text-sm text-muted-foreground">No strengths identified</p>
                    )}
                  </div>
                </div>

                <div className="glass-panel rounded-2xl border border-border/50 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <TrendingDown className="w-5 h-5 text-red-400" />
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Areas for Improvement
                    </p>
                  </div>
                  <div className="space-y-2">
                    {(report.weaknesses || []).map((w, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        <XCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                        <span>{w}</span>
                      </div>
                    ))}
                    {(!report.weaknesses || report.weaknesses.length === 0) && (
                      <p className="text-sm text-muted-foreground">No weaknesses identified</p>
                    )}
                  </div>
                </div>
              </div>

              {/* New Interview Button */}
              <div className="text-center">
                <motion.button
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={handleReset}
                  className="px-8 py-3.5 rounded-xl bg-primary text-primary-foreground font-bold flex items-center gap-3 mx-auto shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all"
                >
                  <RotateCcw className="w-5 h-5" />
                  Start New Interview
                </motion.button>
              </div>
            </div>
          ) : (
            <div className="glass-panel rounded-2xl border border-border/50 p-12 text-center">
              <Trophy className="w-12 h-12 text-primary mx-auto mb-4 opacity-40" />
              <p className="text-muted-foreground">Complete the interview to see your report.</p>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}