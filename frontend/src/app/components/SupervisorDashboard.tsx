import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import { CohortHeatmap } from "./CohortHeatmap";
import { AtRiskTable } from "./AtRiskTable";
import { StudentDrillDown } from "./StudentDrillDown";
import { Users, AlertTriangle, Activity, LogOut, Sparkles } from "lucide-react";
import { useNavigate } from "react-router";

const API = "";

interface CohortData {
  total: number;
  active_this_week: number;
  inactive_7_plus_days: unknown[];
  weakest_topics: string[];
  at_risk_count: number;
}

interface AtRiskStudent {
  student_id: string;
  last_active: string;
  days_inactive: number;
  weak_topics: string[];
  weak_count: number;
}

export function SupervisorDashboard() {
  const navigate = useNavigate();
  const [cohort, setCohort] = useState<CohortData | null>(null);
  const [atRisk, setAtRisk] = useState<AtRiskStudent[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [insights, setInsights] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/supervisor/cohort`).then((r) => r.json()),
      fetch(`${API}/api/supervisor/at-risk`).then((r) => r.json()),
    ])
      .then(([cohortData, atRiskData]) => {
        setCohort(cohortData);
        setAtRisk(atRiskData.students ?? []);
        setLoading(false);
      })
      .catch(() => {
        setError("Could not load supervisor data. Is the backend running?");
        setLoading(false);
      });

    fetch(`${API}/api/supervisor/insights`)
      .then((r) => r.json())
      .then((data) => setInsights(data.narrative))
      .catch(() => null);
  }, []);

  return (
    <div className="min-h-screen bg-[#0D1B2A] px-6 py-8 relative">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 max-w-5xl mx-auto">
        <div className="flex items-center gap-3">
          <HolographicEyeLogo size={36} animated />
          <div>
            <h1 className="text-white" style={{ fontSize: "1.25rem", fontWeight: 700 }}>
              Supervisor Dashboard
            </h1>
            <p className="text-[#14B8A6]" style={{ fontSize: "0.7rem", letterSpacing: "0.12em" }}>
              EYEQ MEDICAL EDUCATION
            </p>
          </div>
        </div>
        <button
          onClick={() => { sessionStorage.clear(); navigate("/"); }}
          className="flex items-center gap-1.5 text-slate-500 hover:text-slate-300 transition-colors"
          style={{ fontSize: "0.8rem" }}
        >
          <LogOut size={14} />
          Sign out
        </button>
      </div>

      {loading && (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-2 border-[#14B8A6] border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {error && (
        <p className="text-red-400 text-center py-20">{error}</p>
      )}

      {cohort && (
        <div className="max-w-5xl mx-auto space-y-6">
          {/* AI cohort narrative */}
          {insights && (
            <motion.div
              className="flex items-start gap-3 px-5 py-4 rounded-2xl border"
              style={{ background: "rgba(20,184,166,0.06)", borderColor: "rgba(20,184,166,0.2)" }}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Sparkles size={15} style={{ color: "#14B8A6", flexShrink: 0, marginTop: 2 }} />
              <p className="text-slate-300" style={{ fontSize: "0.8125rem", lineHeight: 1.6 }}>
                {insights}
              </p>
            </motion.div>
          )}

          {/* KPI row */}
          <div className="grid grid-cols-3 gap-4">
            {[
              { icon: Users, label: "Total Students", value: cohort.total, color: "#14B8A6" },
              { icon: Activity, label: "Active This Week", value: cohort.active_this_week, color: "#818CF8" },
              { icon: AlertTriangle, label: "At Risk", value: cohort.at_risk_count, color: cohort.at_risk_count > 0 ? "#F87171" : "#4ADE80" },
            ].map(({ icon: Icon, label, value, color }) => (
              <motion.div
                key={label}
                className="px-5 py-5 rounded-2xl bg-white/[0.04] border border-white/10"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <Icon size={16} style={{ color }} />
                  <p className="text-slate-400" style={{ fontSize: "0.75rem", fontWeight: 600 }}>{label}</p>
                </div>
                <p className="text-white" style={{ fontSize: "2rem", fontWeight: 700, color }}>{value}</p>
              </motion.div>
            ))}
          </div>

          {/* Heatmap */}
          <div className="px-5 py-5 rounded-2xl bg-white/[0.04] border border-white/10">
            <h2 className="text-white mb-4" style={{ fontSize: "0.9rem", fontWeight: 600 }}>
              Cohort Topic Weaknesses
            </h2>
            <CohortHeatmap
              topics={cohort.weakest_topics}
              retentionByTopic={{}}
            />
            {cohort.weakest_topics.length === 0 && (
              <p className="text-slate-500 text-sm">No weak topics recorded yet.</p>
            )}
          </div>

          {/* At-risk table */}
          <div className="px-5 py-5 rounded-2xl bg-white/[0.04] border border-white/10">
            <h2 className="text-white mb-4" style={{ fontSize: "0.9rem", fontWeight: 600 }}>
              At-Risk Students
            </h2>
            <AtRiskTable students={atRisk} onSelectStudent={setSelectedStudent} />
          </div>
        </div>
      )}

      {/* Student drill-down modal */}
      <AnimatePresence>
        {selectedStudent && (
          <StudentDrillDown
            studentId={selectedStudent}
            onClose={() => setSelectedStudent(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
