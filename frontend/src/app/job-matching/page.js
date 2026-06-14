"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Search,
  MapPin,
  Briefcase,
  ExternalLink,
} from "lucide-react";

const API_BASE = "https://gb-main-production.up.railway.app";

export default function JobMatchingPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [searchTerm, setSearchTerm] = useState("Node.js Developer");
  const [location, setLocation] = useState("Cairo");
  const [country, setCountry] = useState("eg");

  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE}/api/v1/jobs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
        },
        body: JSON.stringify({
          what: searchTerm || "developer",
          where: location,
          country,
          page: 1,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server Error ${response.status}`);
      }

      const data = await response.json();

      setJobs(data?.data || []);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to fetch jobs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  return (
    <div className="h-full flex flex-col space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground mb-2">
          AI Job Search
        </h1>

        <p className="text-muted-foreground">
          Discover opportunities powered by AI job matching.
        </p>
      </div>

      {/* Search Section */}
      <div className="glass-panel p-6 rounded-2xl">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Job Title */}
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />

            <input
              type="text"
              placeholder="Job title..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-11 pr-4 py-3 rounded-xl bg-background border border-primary/20 focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>

          {/* Location */}
          <div className="relative flex-1">
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />

            <input
              type="text"
              placeholder="Location..."
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full pl-11 pr-4 py-3 rounded-xl bg-background border border-primary/20 focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>

          {/* Country */}
          <input
            type="text"
            placeholder="Country"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            className="w-full lg:w-32 px-4 py-3 rounded-xl bg-background border border-primary/20 focus:outline-none focus:ring-2 focus:ring-primary/40"
          />

          {/* Search Button */}
          <button
            onClick={loadJobs}
            disabled={loading}
            className="px-8 py-3 bg-primary text-black font-bold rounded-xl hover:opacity-90 transition-all disabled:opacity-50"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <span className="text-primary animate-pulse text-lg">
            Loading jobs...
          </span>
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="glass-panel p-6 rounded-2xl border border-red-500/20">
          <p className="text-red-500">{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && jobs.length === 0 && (
        <div className="glass-panel p-10 rounded-2xl text-center">
          <p className="text-muted-foreground">
            No jobs found. Try another search.
          </p>
        </div>
      )}

      {/* Jobs Grid */}
      {!loading && !error && jobs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 pb-10">
          {jobs.map((job, idx) => (
            <motion.div
              key={job.id || idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{
                y: -5,
                scale: 1.02,
              }}
              transition={{
                duration: 0.2,
              }}
              className="glass-panel rounded-2xl p-6 flex flex-col justify-between min-h-[260px]"
            >
              <div>
                {/* Job Title */}
                <h2 className="text-xl font-bold text-foreground mb-3 line-clamp-2">
                  {
                    job.title ||
                    job.job_title ||
                    "Untitled Job"
                  }
                </h2>

                {/* Company */}
                <div className="flex items-center gap-2 text-sm text-primary font-medium mb-2">
                  <Briefcase size={16} />
                  <span>
                    {job.company?.display_name ||
                      job.company ||
                      job.employer_name ||
                      "Unknown Company"}
                  </span>
                </div>

                {/* Location */}
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                  <MapPin size={16} />
                  <span>
                    {
                      job.location?.display_name ||
                      job.location ||
                      job.job_city ||
                      job.job_country ||
                      "Location not specified"
                    }
                  </span>
                </div>

                {/* Description */}
                <p className="text-sm text-muted-foreground line-clamp-4">
                  {job.description ||
                    job.job_description ||
                    "No description available."}
                </p>
              </div>

              {/* Action Button */}
              <a
                href={
                      job.redirect_url ||
                      job.job_apply_link ||
                      job.job_url ||
                      job.url ||
                      "#"
                    }
                target="_blank"
                rel="noopener noreferrer"
                className="mt-6 w-full py-3 bg-primary text-black font-bold rounded-xl flex items-center justify-center gap-2 hover:opacity-90 transition-all"
              >
                View Job
                <ExternalLink size={16} />
              </a>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
