import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { motion, AnimatePresence } from "motion/react";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import { Flame, CheckCircle, XCircle, ArrowRight } from "lucide-react";

const API = "";

interface QuestionData {
  question: string;
  topic: string;
}

type Phase = "loading" | "question" | "result" | "done";

export function DailyCheckInScreen() {
  const navigate = useNavigate();
  const studentId = sessionStorage.getItem("eyeq_student_id") || "anonymous";

  const [streak, setStreak] = useState(0);
  const [weakTopic, setWeakTopic] = useState<string | null>(null);
  const [question, setQuestion] = useState<QuestionData | null>(null);
  const [answer, setAnswer] = useState("");
  const [phase, setPhase] = useState<Phase>("loading");
  const [correct, setCorrect] = useState<boolean | null>(null);
  const [feedback, setFeedback] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const statusRes = await fetch(`${API}/api/checkin/status?student_id=${studentId}`);
        const status = await statusRes.json();
        setStreak(status.streak ?? 0);
        setWeakTopic(status.weak_topic ?? null);

        const qRes = await fetch(`${API}/api/checkin/question?student_id=${studentId}`);
        const q = await qRes.json();
        setQuestion(q);
        setPhase("question");
      } catch {
        // If we can't load the check-in, skip straight to dashboard
        navigate("/dashboard");
      }
    })();
  }, [studentId, navigate]);

  const handleSubmit = async () => {
    if (!answer.trim() || !question) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${API}/api/checkin/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: studentId,
          question: question.question,
          answer: answer.trim(),
          topic: question.topic,
        }),
      });
      const data = await res.json();
      setCorrect(data.correct);
      setFeedback(data.feedback);
      setPhase("result");
    } catch {
      setFeedback("Could not evaluate — please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0D1B2A] flex items-center justify-center px-4 py-12">
      <motion.div
        className="w-full max-w-lg"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <HolographicEyeLogo size={36} animated />
          <div>
            <h1 className="text-white" style={{ fontSize: "1.25rem", fontWeight: 700 }}>
              Daily Check-In
            </h1>
            {streak > 0 && (
              <div className="flex items-center gap-1.5 mt-0.5">
                <Flame size={13} className="text-orange-400" />
                <span className="text-orange-400" style={{ fontSize: "0.75rem", fontWeight: 600 }}>
                  {streak}-day streak
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Focus topic */}
        {weakTopic && phase !== "loading" && (
          <div className="mb-5 px-4 py-3 rounded-xl bg-[#14B8A6]/10 border border-[#14B8A6]/20">
            <p className="text-[#14B8A6]" style={{ fontSize: "0.8rem" }}>
              Today's focus: <strong>{weakTopic}</strong>
            </p>
          </div>
        )}

        {/* Loading */}
        {phase === "loading" && (
          <div className="flex items-center justify-center h-40">
            <div className="w-8 h-8 border-2 border-[#14B8A6] border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Question */}
        <AnimatePresence>
          {phase === "question" && question && (
            <motion.div
              key="question"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
            >
              <div className="mb-6 px-5 py-5 rounded-2xl bg-white/[0.05] border border-white/10">
                <p className="text-slate-400 mb-3" style={{ fontSize: "0.7rem", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                  Warm-up question
                </p>
                <p className="text-white" style={{ fontSize: "1rem", lineHeight: 1.6 }}>
                  {question.question}
                </p>
              </div>

              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer…"
                rows={3}
                className="w-full px-4 py-3 mb-4 rounded-xl bg-white/[0.05] border border-white/15 text-white placeholder-slate-600 outline-none focus:border-[#14B8A6]/50 resize-none"
                style={{ fontSize: "0.9rem", lineHeight: 1.5 }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleSubmit();
                }}
              />

              <button
                onClick={handleSubmit}
                disabled={!answer.trim() || submitting}
                className="w-full py-3 rounded-xl bg-[#14B8A6] text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#0D9488] transition-colors"
                style={{ fontSize: "0.9375rem" }}
              >
                {submitting ? "Checking…" : "Submit Answer"}
              </button>

              <button
                onClick={() => navigate("/dashboard")}
                className="w-full mt-3 py-2 text-slate-600 hover:text-slate-400 transition-colors"
                style={{ fontSize: "0.8rem" }}
              >
                Skip for today
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Result */}
        <AnimatePresence>
          {phase === "result" && (
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center"
            >
              <div className="flex justify-center mb-4">
                {correct ? (
                  <CheckCircle size={48} className="text-green-400" />
                ) : (
                  <XCircle size={48} className="text-red-400" />
                )}
              </div>
              <p className="text-white mb-2" style={{ fontSize: "1.1rem", fontWeight: 600 }}>
                {correct ? "Correct!" : "Not quite"}
              </p>
              <p className="text-slate-300 mb-8" style={{ fontSize: "0.9rem", lineHeight: 1.6 }}>
                {feedback}
              </p>
              <button
                onClick={() => navigate("/dashboard")}
                className="flex items-center gap-2 mx-auto px-6 py-3 rounded-xl bg-[#14B8A6] text-white font-semibold hover:bg-[#0D9488] transition-colors"
                style={{ fontSize: "0.9375rem" }}
              >
                Continue to Dashboard
                <ArrowRight size={16} />
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
