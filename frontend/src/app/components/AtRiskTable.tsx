import React from "react";
import { AlertTriangle } from "lucide-react";

interface AtRiskStudent {
  student_id: string;
  last_active: string;
  days_inactive: number;
  weak_topics: string[];
  weak_count: number;
}

interface Props {
  students: AtRiskStudent[];
  onSelectStudent: (id: string) => void;
}

export function AtRiskTable({ students, onSelectStudent }: Props) {
  if (students.length === 0) {
    return (
      <p className="text-slate-500 text-sm">No at-risk students. All good.</p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-slate-500 text-left border-b border-white/10">
            <th className="pb-2 pr-4 font-semibold" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>Student</th>
            <th className="pb-2 pr-4 font-semibold" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>Days Inactive</th>
            <th className="pb-2 pr-4 font-semibold" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>Last Active</th>
            <th className="pb-2 font-semibold" style={{ fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>Weak Topics</th>
          </tr>
        </thead>
        <tbody>
          {students.map((s) => (
            <tr
              key={s.student_id}
              onClick={() => onSelectStudent(s.student_id)}
              className="border-b border-white/5 hover:bg-white/[0.03] cursor-pointer transition-colors"
            >
              <td className="py-3 pr-4">
                <div className="flex items-center gap-2">
                  <AlertTriangle size={13} className="text-red-400 flex-shrink-0" />
                  <span className="text-white font-mono text-xs truncate max-w-[120px]">{s.student_id.slice(0, 8)}…</span>
                </div>
              </td>
              <td className="py-3 pr-4">
                <span className="text-red-400 font-semibold">{s.days_inactive}d</span>
              </td>
              <td className="py-3 pr-4 text-slate-400">{s.last_active}</td>
              <td className="py-3">
                <div className="flex flex-wrap gap-1">
                  {s.weak_topics.slice(0, 3).map((t) => (
                    <span key={t} className="px-2 py-0.5 rounded-full bg-red-500/15 text-red-400 text-xs">{t}</span>
                  ))}
                  {s.weak_topics.length > 3 && (
                    <span className="text-slate-600 text-xs">+{s.weak_topics.length - 3}</span>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
