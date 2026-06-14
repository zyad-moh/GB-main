"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { interviewApi } from "@/lib/agent_api";

export default function InterviewDetails() {
  const params = useParams();
  const interviewId = params?.id;
  const [data, setData] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [error, setError] = useState(null);

  const loadInterview = async () => {
    if (!interviewId) return;

    try {
      setError(null);
      const interview = await interviewApi.getInterview(
        interviewId
      );

      setData(interview);

      if (interview.questions) {
        setAnswers(
          new Array(interview.questions.length).fill("")
        );
      }
    } catch (err) {
      console.error(err);
      setError(err?.message ?? "Unable to load interview.");
    }
  };

  useEffect(() => {
    loadInterview();
  }, [interviewId]);

  const submitAnswers = async () => {
    if (!interviewId) return;

    await interviewApi.submitAnswers(
      interviewId,
      answers
    );

    loadInterview();
  };

  const retryInterview = async () => {
    if (!interviewId) return;

    await interviewApi.retryInterview(
      interviewId
    );

    loadInterview();
  };

  const resumeInterview = async () => {
    if (!interviewId) return;

    await interviewApi.resumeInterview(
      interviewId,
      true
    );

    loadInterview();
  };

  if (error)
    return (
      <div className="p-8 text-red-300">
        <h1 className="text-2xl font-bold mb-4">
          Unable to load interview
        </h1>
        <p>{error}</p>
      </div>
    );

  if (!data)
    return (
      <div className="p-8">Loading...</div>
    );

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-3xl font-bold">
        Interview
      </h1>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-slate-900 p-5 rounded-xl">
          <p>Status: {data.status}</p>
          <p>
            Current Step:
            {data.current_step}
          </p>
          <p>
            Retry Count:
            {data.retry_count}
          </p>
        </div>

        <div className="bg-slate-900 p-5 rounded-xl">
          <p>
            Meeting Platform:
            {data.meeting_platform}
          </p>

          <p>
            Calendar Status:
            {data.calendar_status}
          </p>
        </div>
      </div>

      {data.questions?.length > 0 && (
        <div className="bg-slate-900 rounded-xl p-6">
          <h2 className="text-xl mb-4">
            Questions
          </h2>

          {data.questions.map(
            (question, index) => (
              <div
                key={index}
                className="mb-5"
              >
                <p className="mb-2">
                  {question}
                </p>

                <textarea
                  rows={4}
                  className="w-full bg-slate-800 p-3 rounded"
                  onChange={(e) => {
                    const temp = [
                      ...answers,
                    ];

                    temp[index] =
                      e.target.value;

                    setAnswers(temp);
                  }}
                />
              </div>
            )
          )}

          <button
            onClick={submitAnswers}
            className="bg-cyan-500 px-5 py-2 rounded"
          >
            Submit Answers
          </button>
        </div>
      )}

      {data.report && (
        <div className="bg-slate-900 rounded-xl p-6">
          <h2 className="text-xl mb-4">
            Report
          </h2>

          <pre>
            {JSON.stringify(
              data.report,
              null,
              2
            )}
          </pre>
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={resumeInterview}
          className="bg-green-500 px-5 py-2 rounded"
        >
          Resume
        </button>

        <button
          onClick={retryInterview}
          className="bg-red-500 px-5 py-2 rounded"
        >
          Retry
        </button>
      </div>
    </div>
  );
}