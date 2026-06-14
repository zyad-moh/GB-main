const API_BASE = "http://localhost:5000/api/v1";

export const interviewApi = {
  // === Practice Interview (inter.py) ===

  startPractice: async ({ role, difficulty, interview_type }) => {
    const res = await fetch(`${API_BASE}/interview/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role, difficulty, interview_type }),
    });
    return res.json();
  },

  submitAnswer: async ({ session_id, answer }) => {
    const res = await fetch(`${API_BASE}/interview/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, answer }),
    });
    return res.json();
  },

  getReport: async (session_id) => {
    const res = await fetch(`${API_BASE}/interview/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id }),
    });
    return res.json();
  },

  getSessions: async () => {
    const res = await fetch(`${API_BASE}/interview/sessions`);
    return res.json();
  },

  // === Email-based Interview (interview.py) ===

  triggerInterview: async (payload) => {
    const res = await fetch(`${API_BASE}/interview/trigger`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to create interview");
    return res.json();
  },

  getInterview: async (id) => {
    const res = await fetch(`${API_BASE}/interview/${id}`);
    if (!res.ok) throw new Error("Interview not found");
    return res.json();
  },

  resumeInterview: async (id, forceResume = false) => {
    const res = await fetch(`${API_BASE}/interview/${id}/resume`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ force_resume: forceResume }),
    });
    return res.json();
  },

  retryInterview: async (id) => {
    const res = await fetch(`${API_BASE}/interview/${id}/retry`, {
      method: "POST",
    });
    return res.json();
  },

  submitAnswers: async (id, answers) => {
    const res = await fetch(`${API_BASE}/interview/${id}/submit-answers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers }),
    });
    return res.json();
  },
};

export const emailApi = {
  getStatus: async () => {
    const res = await fetch(`${API_BASE}/email-ingestion/status`);
    return res.json();
  },

  pollNow: async () => {
    const res = await fetch(`${API_BASE}/email-ingestion/poll-now`, {
      method: "POST",
    });
    return res.json();
  },
};