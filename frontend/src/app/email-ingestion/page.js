"use client";

import {
  emailApi,
} from "@/lib/agent_api";
import {
  useEffect,
  useState,
} from "react";

export default function EmailIngestion() {
  const [status, setStatus] =
    useState(null);

  const loadStatus = async () => {
    const data =
      await emailApi.getStatus();

    setStatus(data);
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const pollNow = async () => {
    await emailApi.pollNow();
    loadStatus();
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">
        Email Ingestion
      </h1>

      <div className="bg-slate-900 p-6 rounded-xl">
        <pre>
          {JSON.stringify(
            status,
            null,
            2
          )}
        </pre>

        <button
          onClick={pollNow}
          className="mt-4 px-5 py-2 rounded bg-cyan-500"
        >
          Poll Gmail Now
        </button>
      </div>
    </div>
  );
}