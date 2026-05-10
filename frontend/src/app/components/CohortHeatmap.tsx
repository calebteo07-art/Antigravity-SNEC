import React from "react";

interface Props {
  topics: string[];
  retentionByTopic: Record<string, number>;
}

function scoreToColor(score: number | undefined): string {
  if (score === undefined) return "#1e293b";
  if (score >= 0.75) return "#14B8A6";
  if (score >= 0.5) return "#F59E0B";
  return "#F87171";
}

export function CohortHeatmap({ topics, retentionByTopic }: Props) {
  if (topics.length === 0) {
    return (
      <p className="text-slate-500 text-sm">No topic data yet.</p>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {topics.map((topic) => {
        const score = retentionByTopic[topic];
        return (
          <div
            key={topic}
            className="px-3 py-2 rounded-lg text-xs font-medium"
            style={{
              background: `${scoreToColor(score)}22`,
              border: `1px solid ${scoreToColor(score)}66`,
              color: scoreToColor(score),
            }}
            title={score !== undefined ? `${Math.round(score * 100)}%` : "No data"}
          >
            {topic}
            {score !== undefined && (
              <span className="ml-1.5 opacity-70">{Math.round(score * 100)}%</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
