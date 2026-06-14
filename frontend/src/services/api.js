// src/services/api.js

/**
 * MOCK API SERVICE - CareerAI
 * 
 * This file acts as the boundary between the frontend UI and the
 * future backend ML/Python APIs. All functions return Promises to 
 * simulate network asynchronous behavior.
 */

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const careerService = {
  
  /**
   * Fetch high-level dashboard metrics and charts data
   */
  async getDashboardStats() {
    await delay(800); // Simulate network latency
    return {
      status: "success",
      data: {
        resumeStrength: 82, 
        resumeStrengthTrend: "+4.2%",
        skillGapScore: 65,
        skillGapTrend: "-12.0%",
        matchRate: 74,
        matchRateTrend: "+8.5%",
        
        // Mock data for Recharts - Bar Chart
        skillGapAnalysis: [
          { name: 'JavaScript', target: 90, current: 85 },
          { name: 'Python', target: 80, current: 40 },
          { name: 'AWS', target: 70, current: 20 },
          { name: 'React', target: 95, current: 90 },
          { name: 'CI/CD', target: 60, current: 10 }
        ],
        
        // Mock data for Recharts - Line Chart
        resumeEvolution: [
          { month: 'Jan', score: 45 },
          { month: 'Feb', score: 52 },
          { month: 'Mar', score: 61 },
          { month: 'Apr', score: 68 },
          { month: 'May', score: 75 },
          { month: 'Jun', score: 82 }
        ],

        // Suggestions
        aiSuggestions: [
          { id: 1, title: "Add Cloud Computing Skills", priority: "High", action: "View Courses" },
          { id: 2, title: "Quantify Work Experience", priority: "Medium", action: "Optimize Resume" }
        ]
      }
    };
  },

  /**
   * Upload a resume file for NLP processing using the real API backend.
   * Accepts FormData to match backend expectations.
   */
  async uploadResume(formData) {
    if (!(formData instanceof FormData)) {
      throw new Error("Expected FormData for uploadResume");
    }

    try {
      const response = await fetch("https://rag-rag-v16-010-production.up.railway.app/api/v1/data/upload/1", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed with status: ${response.status}`);
      }

      const result = await response.json();
      const file = formData.get("resume") || formData.get("file");
      const fileName = file && file.name ? file.name : "document";
      
      return {
        status: "success",
        message: result.message || `File '${fileName}' successfully parsed and analyzed.`,
        parsedId: result.id || result.parsedId || "RES-" + Math.floor(Math.random() * 10000),
        rawData: result // Keep raw data for future processing
      };
    } catch (error) {
      console.error("Upload API Error:", error);
      throw error;
    }
  },

  /**
   * Fetch matching jobs from the Python similarity engine
   */
  async getJobMatches(filters = {}) {
    await delay(1200);

    let allJobs = [
      {
        id: "j1",
        title: "Frontend Next.js Developer",
        company: "Vercel Enterprise",
        location: "Remote (Worldwide)",
        matchScore: 94,
        salary: "$120K - $140K",
        tags: ["Next.js", "React", "TypeScript", "Tailwind"],
        desc: "Looking for an expert React developer to architect enterprise scale platforms.",
        industry: "Software Engineering",
        exp: "Mid Level"
      },
      {
        id: "j2",
        title: "Fullstack ML Engineer",
        company: "OpenAI Corp",
        location: "San Francisco, CA",
        matchScore: 62,
        salary: "$180K - $220K",
        tags: ["Python", "TensorFlow", "React", "AWS"],
        desc: "Help build the future of AI interfaces bridging Python models to web UI.",
        industry: "Data Science",
        exp: "Senior"
      },
      {
        id: "j3",
        title: "Product Engineer",
        company: "Stripe",
        location: "New York, NY",
        matchScore: 88,
        salary: "$150K - $190K",
        tags: ["Node.js", "React", "SQL"],
        desc: "Build new product surfaces for global payment processing.",
        industry: "Software Engineering",
        exp: "Senior"
      },
      {
        id: "j4",
        title: "Junior Data Analyst",
        company: "Spotify",
        location: "Remote (Worldwide)",
        matchScore: 71,
        salary: "$80K - $100K",
        tags: ["SQL", "Python", "Tableau"],
        desc: "Analyze user listening trends to improve the recommendation engine.",
        industry: "Data Science",
        exp: "Entry Level"
      }
    ];

    let filteredJobs = allJobs;

    // Filter by Location
    if (filters.location && filters.location !== "All Locations") {
      filteredJobs = filteredJobs.filter(j => j.location === filters.location);
    }

    // Filter by Industry
    if (filters.industry) {
      filteredJobs = filteredJobs.filter(j => j.industry === filters.industry);
    }

    // Filter by Experience Level
    if (filters.experienceLevels && filters.experienceLevels.length > 0) {
      filteredJobs = filteredJobs.filter(j => filters.experienceLevels.includes(j.exp));
    }

    return {
      status: "success",
      data: filteredJobs
    };
  },

  /**
   * Fetch spider/radar chart skill gaps and recommendations
   */
  async getSkillGaps() {
    await delay(900);
    return {
      status: "success",
      data: {
        radarData: [
          { subject: 'Frontend', A: 95, B: 80, fullMark: 100 },
          { subject: 'Backend', A: 60, B: 90, fullMark: 100 },
          { subject: 'Cloud/DevOps', A: 30, B: 75, fullMark: 100 },
          { subject: 'Database', A: 70, B: 80, fullMark: 100 },
          { subject: 'AI/ML', A: 10, B: 50, fullMark: 100 }
        ],
        courseRecommendations: [
          { id: "c1", title: "AWS Certified Architect", provider: "Coursera", hours: "40", match: "High" }
        ]
      }
    };
  }
};
