import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { motion } from "motion/react";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import { Stethoscope, Clock, ChevronRight, ArrowLeft, AlertCircle } from "lucide-react";

interface CaseInfo {
  case_id: string;
  title: string;
  difficulty: string;
  topic: string;
  estimated_minutes: number;
  patient: {
    name: string;
    age: number;
    presenting_complaint: string;
  };
}

const DIFFICULTY_COLORS: Record<string, { text: string; bg: string; border: string }> = {
  beginner:     { text: "#4ADE80", bg: "#4ADE8015", border: "#4ADE8030" },
  intermediate: { text: "#F59E0B", bg: "#F59E0B15", border: "#F59E0B30" },
  advanced:     { text: "#F87171", bg: "#F8717115", border: "#F8717130" },
};

function difficultyStyle(d: string) {
  return DIFFICULTY_COLORS[d.toLowerCase()] ?? DIFFICULTY_COLORS.intermediate;
}

export function CaseListScreen() {
  const navigate = useNavigate();
  const [cases, setCases] = useState<CaseInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/cases")
      .then((r) => {
        if (!r.ok) throw new Error("Server error");
        return r.json();
      })
      .then((data) => setCases(data.cases))
      .catch(() => setError("Could not load cases. Is the backend running?"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-[#0D1B2A] flex flex-col items-center px-4 py-10 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/3 left-1/4 w-96 h-96 rounded-full bg-indigo-500 opacity-[0.04] blur-3xl"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      <motion.div
        className="w-full max-w-2xl relative z-10"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-1.5 text-slate-500 hover:text-slate-300 transition-colors"
            style={{ fontSize: "0.85rem" }}
          >
            <ArrowLeft size={16} />
            Dashboard
          </button>
          <div className="flex items-center gap-3 ml-auto">
            <HolographicEyeLogo size={28} animated={false} />
            <span className="text-white" style={{ fontSize: "1rem", fontWeight: 700 }}>
              Case Simulation
            </span>
          </div>
        </div>

        <h2 className="text-white mb-1" style={{ fontSize: "1.5rem", fontWeight: 700 }}>
          Choose a Case
        </h2>
        <p className="text-slate-400 mb-8" style={{ fontSize: "0.875rem" }}>
          Interview a virtual patient, request investigations, and submit your diagnosis.
        </p>

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 rounded-full border-2 border-[#14B8A6] border-t-transparent animate-spin" />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-3 px-5 py-4 rounded-xl bg-red-500/10 border border-red-500/25 text-red-400">
            <AlertCircle size={18} />
            <span style={{ fontSize: "0.875rem" }}>{error}</span>
          </div>
        )}

        {/* Case cards */}
        {!loading && !error && cases.length === 0 && (
          <p className="text-slate-500 text-center py-16" style={{ fontSize: "0.9rem" }}>
            No cases available. Add JSON files to the <code className="text-slate-400">cases/</code> directory.
          </p>
        )}

        <div className="space-y-4">
          {cases.map((c, i) => {
            const ds = difficultyStyle(c.difficulty);
            return (
              <motion.button
                key={c.case_id}
                onClick={() => navigate(`/cases/${c.case_id}`)}
                className="w-full text-left px-6 py-5 rounded-2xl bg-white/[0.04] border border-white/10 group transition-all hover:bg-white/[0.07] hover:border-white/20"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2.5 mb-2 flex-wrap">
                      <span className="text-white" style={{ fontSize: "1rem", fontWeight: 600 }}>
                        {c.title}
                      </span>
                      <span
                        className="px-2 py-0.5 rounded-full text-xs font-semibold"
                        style={{
                          color: ds.text,
                          background: ds.bg,
                          border: `1px solid ${ds.border}`,
                          fontSize: "0.7rem",
                          letterSpacing: "0.05em",
                          textTransform: "capitalize",
                        }}
                      >
                        {c.difficulty}
                      </span>
                    </div>

                    <p className="text-slate-400 mb-3" style={{ fontSize: "0.8125rem" }}>
                      {c.topic}
                    </p>

                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1.5 text-slate-500" style={{ fontSize: "0.75rem" }}>
                        <Stethoscope size={12} />
                        <span>{c.patient.name}, {c.patient.age}y</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-slate-500" style={{ fontSize: "0.75rem" }}>
                        <Clock size={12} />
                        <span>~{c.estimated_minutes} min</span>
                      </div>
                    </div>

                    <p className="text-slate-500 mt-2" style={{ fontSize: "0.8rem", fontStyle: "italic" }}>
                      "{c.patient.presenting_complaint}"
                    </p>
                  </div>

                  <ChevronRight
                    size={18}
                    className="flex-shrink-0 text-slate-600 group-hover:text-slate-300 transition-colors mt-1"
                  />
                </div>
              </motion.button>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
