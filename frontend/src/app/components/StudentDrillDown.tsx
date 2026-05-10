import React, { useEffect, useState } from "react";
import { motion } from "motion/react";
import { X, TrendingUp, TrendingDown, Minus } from "lucide-react";

const API = "http://localhost:8000";

interface StudentProfile {
  student_id: string;
  weak_topics: string[];
  missed_findings: string[];
  retention_scores: Record<string, number>;
  session_count: number;
  streak: number;
  last_active: string;
  learning_velocity: string;
  checkin_done_today: boolean;
}

interface Props {
  studentId: string;
  onClose: () => void;
}

function VelocityIcon({ velocity }: { velocity: string }) {
  if (velocity === "improving") return <TrendingUp size={14} className="text-green-400" />;
  if (velocity === "declining") return <TrendingDown size={14} className="text-red-400" />;
  return <Minus size={14} className="text-slate-400" />;
}

export function StudentDrillDown({ studentId, onClose }: Props) {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API}/api/supervisor/student/${studentId}`)
      .then((r) => { if (!r.ok) throw new Error("Not found"); return r.json(); })
      .then((data) => { setProfile(data); setLoading(false); })
      .catch(() => { setError("Could not load student profile."); setLoading(false); });
  }, [studentId]);

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="w-full max-w-lg bg-[#0D1B2A] border border-white/15 rounded-2xl overflow-hidden shadow-2xl"
        initial={{ scale: 0.95, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <p className="text-white font-semibold">Student Profile</p>
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
            <X size={18} />
          </button>
        </div>

        <div className="px-6 py-5 overflow-y-auto max-h-[70vh]">
          {loading && (
            <div className="flex justify-center py-8">
              <div className="w-6 h-6 border-2 border-[#14B8A6] border-t-transparent rounded-full animate-spin" />
            </div>
          )}
          {error && <p className="text-red-400 text-sm">{error}</p>}
          {profile && (
            <div className="space-y-5">
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: "Sessions", value: profile.session_count },
                  { label: "Streak", value: `${profile.streak}d` },
                  { label: "Last Active", value: profile.last_active || "Never" },
                ].map(({ label, value }) => (
                  <div key={label} className="px-3 py-3 rounded-xl bg-white/[0.04] border border-white/10 text-center">
                    <p className="text-slate-500 mb-1" style={{ fontSize: "0.65rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</p>
                    <p className="text-white font-semibold" style={{ fontSize: "0.9rem" }}>{value}</p>
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-2">
                <VelocityIcon velocity={profile.learning_velocity} />
                <span className="text-slate-400 text-sm capitalize">{profile.learning_velocity}</span>
              </div>

              <div>
                <p className="text-slate-500 mb-2" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase", fontWeight: 600 }}>
                  Weak Topics
                </p>
                {profile.weak_topics.length === 0 ? (
                  <p className="text-slate-600 text-sm">None — all topics above threshold.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {profile.weak_topics.map((t) => {
                      const score = profile.retention_scores[t];
                      return (
                        <span key={t} className="px-2.5 py-1 rounded-full bg-red-500/15 border border-red-500/30 text-red-400 text-xs">
                          {t}{score !== undefined ? ` — ${Math.round(score * 100)}%` : ""}
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>

              <div>
                <p className="text-slate-500 mb-2" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase", fontWeight: 600 }}>
                  Missed Findings
                </p>
                {profile.missed_findings.length === 0 ? (
                  <p className="text-slate-600 text-sm">None recorded.</p>
                ) : (
                  <ul className="space-y-1">
                    {profile.missed_findings.map((f, i) => (
                      <li key={i} className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-slate-600 mt-0.5">•</span>
                        {f}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
