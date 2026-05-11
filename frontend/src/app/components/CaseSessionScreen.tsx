import React, { useState, useRef, useEffect } from "react";
import { useNavigate, useParams } from "react-router";
import { motion, AnimatePresence } from "motion/react";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import {
  Send, User, Bot, ArrowLeft, CheckSquare, AlertCircle,
  Layers, ChevronDown, ChevronUp,
} from "lucide-react";

interface CaseInfo {
  case_id: string;
  title: string;
  difficulty: string;
  topic: string;
  estimated_minutes: number;
  patient: { name: string; age: number; presenting_complaint: string };
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface DomainResult {
  history_score: number;
  investigations_score: number;
  diagnosis_score: number;
  management_score: number;
  history_feedback: string;
  investigations_feedback: string;
  diagnosis_feedback: string;
  management_feedback: string;
  total_score: number;
  overall_feedback: string;
}

const DOMAINS: { label: string; scoreKey: keyof DomainResult; feedbackKey: keyof DomainResult }[] = [
  { label: "History Taking",   scoreKey: "history_score",        feedbackKey: "history_feedback" },
  { label: "Investigations",   scoreKey: "investigations_score",  feedbackKey: "investigations_feedback" },
  { label: "Diagnosis",        scoreKey: "diagnosis_score",       feedbackKey: "diagnosis_feedback" },
  { label: "Management",       scoreKey: "management_score",      feedbackKey: "management_feedback" },
];

export function CaseSessionScreen() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();

  const [caseInfo, setCaseInfo] = useState<CaseInfo | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const [showSubmitForm, setShowSubmitForm] = useState(false);
  const [diagnosis, setDiagnosis] = useState("");
  const [managementPlan, setManagementPlan] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<DomainResult | null>(null);
  const [cards, setCards] = useState<unknown[]>([]);
  const [debrief, setDebrief] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Load case info from the cases list endpoint
  useEffect(() => {
    if (!caseId) return;
    fetch("/api/cases")
      .then((r) => r.json())
      .then((data) => {
        const found = data.cases.find((c: CaseInfo) => c.case_id === caseId);
        if (found) setCaseInfo(found);
        else setLoadError(`Case "${caseId}" not found.`);
      })
      .catch(() => setLoadError("Could not load case. Is the backend running?"));
  }, [caseId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const sendMessage = async () => {
    if (!input.trim() || sending || !caseId) return;
    const content = input.trim();
    const newMsg: ChatMessage = { role: "user", content };
    const updated = [...messages, newMsg];

    setMessages(updated);
    setInput("");
    setSending(true);

    const studentId = sessionStorage.getItem("eyeq_student_id") || "anonymous";
    try {
      const res = await fetch(`/api/cases/${caseId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_id: studentId, messages: updated }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "(Error: could not reach the server.)" },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSubmit = async () => {
    if (!diagnosis.trim() || !managementPlan.trim() || !caseId) return;
    setSubmitting(true);
    setSubmitError(null);

    const studentId = sessionStorage.getItem("eyeq_student_id") || "anonymous";
    try {
      const res = await fetch(`/api/cases/${caseId}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: studentId,
          messages,
          diagnosis: diagnosis.trim(),
          management_plan: managementPlan.trim(),
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResult(data.result);
      setCards(data.cards);
      setDebrief(data.debrief ?? null);
      setShowSubmitForm(false);
    } catch {
      setSubmitError("Evaluation failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const scoreColor = (s: number) =>
    s >= 8 ? "#4ADE80" : s >= 5 ? "#F59E0B" : "#F87171";

  if (loadError) {
    return (
      <div className="min-h-screen bg-[#0D1B2A] flex items-center justify-center p-8">
        <div className="text-center">
          <AlertCircle size={40} className="text-red-400 mx-auto mb-4" />
          <p className="text-red-400 mb-4">{loadError}</p>
          <button
            onClick={() => navigate("/cases")}
            className="text-[#14B8A6] hover:underline text-sm"
          >
            ← Back to cases
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-[#0D1B2A] flex flex-col overflow-hidden">
      {/* Top bar */}
      <div className="flex-shrink-0 flex items-center gap-4 px-5 py-3 border-b border-white/10">
        <button
          onClick={() => navigate("/cases")}
          className="flex items-center gap-1.5 text-slate-500 hover:text-slate-300 transition-colors"
          style={{ fontSize: "0.8rem" }}
        >
          <ArrowLeft size={14} />
          Cases
        </button>
        <div className="flex items-center gap-2.5 ml-auto">
          <HolographicEyeLogo size={24} animated={false} />
          <span className="text-white" style={{ fontSize: "0.9rem", fontWeight: 600 }}>
            {caseInfo ? caseInfo.title : "Loading…"}
          </span>
        </div>
        {!result && (
          <button
            onClick={() => setShowSubmitForm((v) => !v)}
            className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#14B8A6]/15 text-[#14B8A6] hover:bg-[#14B8A6]/25 transition-all border border-[#14B8A6]/30"
            style={{ fontSize: "0.8rem", fontWeight: 500 }}
          >
            <CheckSquare size={13} />
            Submit My Answer
            {showSubmitForm ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>
        )}
      </div>

      <div className="flex flex-1 min-h-0">
        {/* Left panel — patient info */}
        <div className="w-64 flex-shrink-0 border-r border-white/10 flex flex-col overflow-y-auto">
          <div className="p-5">
            <p
              className="text-slate-500 mb-3"
              style={{ fontSize: "0.65rem", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase" }}
            >
              Patient
            </p>
            {caseInfo ? (
              <div className="space-y-3">
                <div>
                  <p className="text-white" style={{ fontSize: "0.9375rem", fontWeight: 600 }}>
                    {caseInfo.patient.name}
                  </p>
                  <p className="text-slate-400" style={{ fontSize: "0.8rem" }}>
                    {caseInfo.patient.age} years old
                  </p>
                </div>
                <div>
                  <p
                    className="text-slate-500 mb-1"
                    style={{ fontSize: "0.65rem", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase" }}
                  >
                    Chief Complaint
                  </p>
                  <p className="text-slate-300" style={{ fontSize: "0.8125rem", lineHeight: 1.5 }}>
                    {caseInfo.patient.presenting_complaint}
                  </p>
                </div>
                <div>
                  <p
                    className="text-slate-500 mb-1"
                    style={{ fontSize: "0.65rem", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase" }}
                  >
                    Topic
                  </p>
                  <p className="text-[#14B8A6]" style={{ fontSize: "0.8rem" }}>
                    {caseInfo.topic}
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                {[80, 60, 90].map((w, i) => (
                  <div key={i} className="h-3 rounded bg-white/10 animate-pulse" style={{ width: `${w}%` }} />
                ))}
              </div>
            )}
          </div>

          <div className="mt-auto p-5 border-t border-white/10">
            <p className="text-slate-600" style={{ fontSize: "0.72rem", lineHeight: 1.5 }}>
              Ask questions to take a history. Request examinations and investigations by name. Submit your answer when ready.
            </p>
          </div>
        </div>

        {/* Right — chat + submit/results */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Submit form panel */}
          <AnimatePresence>
            {showSubmitForm && !result && (
              <motion.div
                className="flex-shrink-0 border-b border-white/10 bg-[#0D2B3A] px-6 py-5"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25 }}
              >
                <h3 className="text-white mb-4" style={{ fontSize: "0.9375rem", fontWeight: 600 }}>
                  Submit Your Answer
                </h3>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-slate-400 mb-1.5" style={{ fontSize: "0.75rem", fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                      Diagnosis
                    </label>
                    <textarea
                      value={diagnosis}
                      onChange={(e) => setDiagnosis(e.target.value)}
                      placeholder="State your diagnosis…"
                      rows={3}
                      className="w-full px-3 py-2.5 rounded-lg bg-white/[0.06] border border-white/15 text-white placeholder-slate-600 outline-none focus:border-[#14B8A6]/50 resize-none"
                      style={{ fontSize: "0.875rem" }}
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1.5" style={{ fontSize: "0.75rem", fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                      Management Plan
                    </label>
                    <textarea
                      value={managementPlan}
                      onChange={(e) => setManagementPlan(e.target.value)}
                      placeholder="Outline your management plan…"
                      rows={3}
                      className="w-full px-3 py-2.5 rounded-lg bg-white/[0.06] border border-white/15 text-white placeholder-slate-600 outline-none focus:border-[#14B8A6]/50 resize-none"
                      style={{ fontSize: "0.875rem" }}
                    />
                  </div>
                </div>
                {submitError && (
                  <p className="text-red-400 mb-3" style={{ fontSize: "0.8rem" }}>{submitError}</p>
                )}
                <button
                  onClick={handleSubmit}
                  disabled={submitting || !diagnosis.trim() || !managementPlan.trim()}
                  className="px-5 py-2.5 rounded-lg bg-[#14B8A6] text-white font-semibold hover:bg-[#0D9488] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ fontSize: "0.875rem" }}
                >
                  {submitting ? "Evaluating…" : "Submit for Evaluation"}
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Results panel */}
          {result && (
            <motion.div
              className="flex-shrink-0 border-b border-white/10 bg-[#0D2B3A] px-6 py-5 overflow-y-auto"
              style={{ maxHeight: "50%" }}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white" style={{ fontSize: "0.9375rem", fontWeight: 600 }}>
                  Evaluation Results
                </h3>
                <span className="text-white font-bold" style={{ fontSize: "1.1rem" }}>
                  <span style={{ color: scoreColor(result.total_score / 4) }}>
                    {result.total_score}
                  </span>
                  <span className="text-slate-500">/40</span>
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4">
                {DOMAINS.map(({ label, scoreKey, feedbackKey }) => {
                  const score = result[scoreKey] as number;
                  return (
                    <div
                      key={label}
                      className="px-4 py-3 rounded-xl bg-white/[0.04] border border-white/10"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-slate-300" style={{ fontSize: "0.8rem", fontWeight: 600 }}>
                          {label}
                        </p>
                        <span style={{ fontSize: "0.875rem", fontWeight: 700, color: scoreColor(score) }}>
                          {score}/10
                        </span>
                      </div>
                      <p className="text-slate-500" style={{ fontSize: "0.75rem", lineHeight: 1.5 }}>
                        {result[feedbackKey] as string}
                      </p>
                    </div>
                  );
                })}
              </div>

              <div className="px-4 py-3 rounded-xl bg-[#14B8A6]/10 border border-[#14B8A6]/20 mb-4">
                <p className="text-slate-300" style={{ fontSize: "0.8125rem", lineHeight: 1.6 }}>
                  {result.overall_feedback}
                </p>
              </div>

              {debrief && (
                <div className="px-4 py-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 mb-4">
                  <p className="text-slate-400 mb-2" style={{ fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                    Debrief
                  </p>
                  <div className="text-slate-300 whitespace-pre-wrap" style={{ fontSize: "0.8125rem", lineHeight: 1.7 }}>
                    {debrief.split(/\*\*(.*?)\*\*/g).map((part, i) =>
                      i % 2 === 1 ? (
                        <strong key={i} className="text-white">{part}</strong>
                      ) : (
                        <span key={i}>{part}</span>
                      )
                    )}
                  </div>
                </div>
              )}

              <button
                onClick={() => {
                  if (cards.length > 0) {
                    sessionStorage.setItem("eyeq_session_cards", JSON.stringify(cards));
                  }
                  navigate("/flashcards");
                }}
                className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-400 hover:bg-amber-500/25 transition-all"
                style={{ fontSize: "0.875rem", fontWeight: 500 }}
              >
                <Layers size={15} />
                Generate Flashcards ({cards.length})
              </button>
            </motion.div>
          )}

          {/* Chat messages */}
          <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
            {messages.length === 0 && !sending && (
              <div className="flex items-center justify-center h-full">
                <p className="text-slate-600 text-center" style={{ fontSize: "0.875rem" }}>
                  Introduce yourself and start taking a history.
                  <br />
                  <span style={{ fontSize: "0.8rem" }}>Press Enter to send.</span>
                </p>
              </div>
            )}

            {messages.map((m, i) => (
              <motion.div
                key={i}
                className={`flex gap-3 items-start ${m.role === "user" ? "flex-row-reverse" : ""}`}
                initial={{ opacity: 0, x: m.role === "user" ? 16 : -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div
                  className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center ${
                    m.role === "user"
                      ? "bg-[#0D1B2A] border border-white/20"
                      : "bg-[#14B8A6]/20 border border-[#14B8A6]/40"
                  }`}
                >
                  {m.role === "user" ? (
                    <User size={13} className="text-white" />
                  ) : (
                    <Bot size={13} className="text-[#14B8A6]" />
                  )}
                </div>
                <div
                  className={`max-w-[78%] px-4 py-3 rounded-2xl ${
                    m.role === "user"
                      ? "rounded-tr-sm bg-[#14B8A6]/15 border border-[#14B8A6]/25 text-white"
                      : "rounded-tl-sm bg-white/[0.06] border border-white/10 text-slate-200"
                  }`}
                  style={{ fontSize: "0.875rem", lineHeight: 1.6 }}
                >
                  {m.content}
                </div>
              </motion.div>
            ))}

            {sending && (
              <div className="flex gap-3 items-start">
                <div className="flex-shrink-0 w-7 h-7 rounded-full bg-[#14B8A6]/20 border border-[#14B8A6]/40 flex items-center justify-center">
                  <Bot size={13} className="text-[#14B8A6]" />
                </div>
                <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-white/[0.06] border border-white/10 flex items-center gap-1.5">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="w-1.5 h-1.5 rounded-full bg-[#14B8A6]"
                      style={{ animation: "bounce 1.2s infinite", animationDelay: `${i * 0.2}s` }}
                    />
                  ))}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          {!result && (
            <div className="flex-shrink-0 border-t border-white/10 px-5 py-4">
              <div className="flex gap-3 items-end">
                <div className="flex-1 bg-white/[0.05] border border-white/15 rounded-xl overflow-hidden focus-within:border-[#14B8A6]/50 transition-all">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => {
                      setInput(e.target.value);
                      e.target.style.height = "auto";
                      e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask the patient a question…"
                    rows={1}
                    className="w-full px-4 py-3 bg-transparent text-white placeholder-slate-600 outline-none resize-none"
                    style={{ fontSize: "0.875rem", lineHeight: 1.5, minHeight: "44px", maxHeight: "120px" }}
                  />
                </div>
                <motion.button
                  onClick={sendMessage}
                  disabled={!input.trim() || sending}
                  className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all ${
                    input.trim() && !sending
                      ? "bg-[#14B8A6] text-white shadow-lg shadow-[#14B8A6]/30"
                      : "bg-white/10 text-slate-600 cursor-not-allowed"
                  }`}
                  whileHover={input.trim() && !sending ? { scale: 1.05 } : undefined}
                  whileTap={input.trim() && !sending ? { scale: 0.95 } : undefined}
                >
                  <Send size={15} />
                </motion.button>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-5px); }
        }
      `}</style>
    </div>
  );
}
