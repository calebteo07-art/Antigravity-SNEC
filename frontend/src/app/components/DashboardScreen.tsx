import React from "react";
import { useNavigate } from "react-router";
import { motion } from "motion/react";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import { MessageSquare, Stethoscope, Layers, ChevronRight, LogOut, Sparkles } from "lucide-react";

const MODES = [
  {
    icon: MessageSquare,
    label: "Chat Tutor",
    description: "Ask questions and explore ophthalmology topics with your AI tutor",
    path: "/chat",
    accent: "#14B8A6",
    bg: "from-[#14B8A6]/20 to-[#14B8A6]/5",
    border: "border-[#14B8A6]/30",
  },
  {
    icon: Stethoscope,
    label: "Case Simulation",
    description: "Interview a virtual patient, reach a diagnosis, and receive scored feedback",
    path: "/cases",
    accent: "#818CF8",
    bg: "from-indigo-500/20 to-indigo-500/5",
    border: "border-indigo-500/30",
  },
  {
    icon: Layers,
    label: "Flashcards",
    description: "Review spaced-repetition cards generated from your sessions",
    path: "/flashcards",
    accent: "#F59E0B",
    bg: "from-amber-500/20 to-amber-500/5",
    border: "border-amber-500/30",
  },
];

export function DashboardScreen() {
  const navigate = useNavigate();

  const userData = (() => {
    try {
      return JSON.parse(sessionStorage.getItem("eyeq_user") || "{}");
    } catch {
      return {};
    }
  })();

  const firstName = (userData.fullName || "Student").split(" ")[0];

  const [checkinChecked, setCheckinChecked] = React.useState(false);
  const [suggestion, setSuggestion] = React.useState<string | null>(null);

  React.useEffect(() => {
    const studentId = sessionStorage.getItem("eyeq_student_id");
    if (!studentId) { setCheckinChecked(true); return; }

    fetch(`http://localhost:8000/api/checkin/status?student_id=${studentId}`)
      .then((r) => r.json())
      .then((data) => {
        if (!data.checkin_done_today) {
          navigate("/checkin");
        } else {
          setCheckinChecked(true);
        }
      })
      .catch(() => setCheckinChecked(true));

    fetch(`http://localhost:8000/api/study-suggestion?student_id=${studentId}`)
      .then((r) => r.json())
      .then((data) => setSuggestion(data.suggestion))
      .catch(() => null);
  }, [navigate]);

  if (!checkinChecked) return null;

  return (
    <div className="min-h-screen bg-[#0D1B2A] flex flex-col items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/4 left-1/3 w-96 h-96 rounded-full bg-[#14B8A6] opacity-[0.04] blur-3xl"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/3 w-80 h-80 rounded-full bg-indigo-500 opacity-[0.04] blur-3xl"
          animate={{ scale: [1, 1.3, 1] }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut", delay: 2 }}
        />
      </div>

      <motion.div
        className="w-full max-w-2xl relative z-10"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div className="flex items-center gap-3">
            <HolographicEyeLogo size={40} animated={true} />
            <div>
              <h1 className="text-white" style={{ fontSize: "1.5rem", fontWeight: 700, lineHeight: 1 }}>
                Welcome back, {firstName}
              </h1>
              <p className="text-[#14B8A6]" style={{ fontSize: "0.75rem", letterSpacing: "0.12em", fontWeight: 500 }}>
                EYEQ MEDICAL EDUCATION
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              sessionStorage.clear();
              navigate("/");
            }}
            className="flex items-center gap-1.5 text-slate-500 hover:text-slate-300 transition-colors"
            style={{ fontSize: "0.8rem" }}
          >
            <LogOut size={14} />
            Sign out
          </button>
        </div>

        {/* AI study suggestion */}
        {suggestion && (
          <motion.div
            className="mb-6 flex items-start gap-3 px-5 py-4 rounded-2xl border"
            style={{ background: "rgba(20,184,166,0.07)", borderColor: "rgba(20,184,166,0.25)" }}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Sparkles size={16} style={{ color: "#14B8A6", flexShrink: 0, marginTop: 2 }} />
            <p className="text-slate-300" style={{ fontSize: "0.8125rem", lineHeight: 1.5 }}>
              {suggestion}
            </p>
          </motion.div>
        )}

        {/* Mode cards */}
        <div className="space-y-4">
          {MODES.map(({ icon: Icon, label, description, path, accent, bg, border }, i) => (
            <motion.button
              key={path}
              onClick={() => navigate(path)}
              className={`w-full flex items-center gap-5 px-6 py-5 rounded-2xl bg-gradient-to-r ${bg} border ${border} text-left group transition-all`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 + i * 0.1, duration: 0.5 }}
              whileHover={{ scale: 1.02, x: 4 }}
              whileTap={{ scale: 0.98 }}
            >
              <div
                className="flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center"
                style={{ background: `${accent}20`, border: `1px solid ${accent}40` }}
              >
                <Icon size={22} style={{ color: accent }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white" style={{ fontSize: "1rem", fontWeight: 600 }}>
                  {label}
                </p>
                <p className="text-slate-400 mt-0.5" style={{ fontSize: "0.8125rem", lineHeight: 1.4 }}>
                  {description}
                </p>
              </div>
              <ChevronRight
                size={18}
                className="flex-shrink-0 text-slate-600 group-hover:text-slate-300 transition-colors"
              />
            </motion.button>
          ))}
        </div>

        <p className="text-center text-slate-600 mt-8" style={{ fontSize: "0.75rem" }}>
          © 2026 EyeQ Medical Education. All rights reserved.
        </p>
      </motion.div>
    </div>
  );
}
