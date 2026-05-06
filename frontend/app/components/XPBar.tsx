import React from "react";
import { motion } from "motion/react";
import { Zap } from "lucide-react";
import { getXPProgress, getXPForNextLevel } from "../utils/gamification";

interface XPBarProps {
  currentXP: number;
  level: number;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
}

export function XPBar({ currentXP, level, showLabel = true, size = "md" }: XPBarProps) {
  const progress = getXPProgress(currentXP);
  const nextLevelXP = getXPForNextLevel(currentXP);
  const currentLevelXP = (level - 1) * 500;
  const xpIntoLevel = currentXP - currentLevelXP;

  const heights = { sm: "h-1.5", md: "h-2", lg: "h-3" };
  const textSizes = { sm: "text-[0.65rem]", md: "text-[0.75rem]", lg: "text-[0.85rem]" };

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-1.5">
            <Zap size={12} className="text-amber-500 fill-amber-500" />
            <span className={`text-[#0D1B2A] font-semibold ${textSizes[size]}`}>
              Level {level}
            </span>
          </div>
          <span className={`text-slate-500 ${textSizes[size]}`}>
            {xpIntoLevel} / {nextLevelXP - currentLevelXP} XP
          </span>
        </div>
      )}
      <div className={`w-full bg-slate-200 rounded-full overflow-hidden ${heights[size]} relative`}>
        <motion.div
          className="absolute inset-y-0 left-0 bg-gradient-to-r from-amber-400 via-amber-500 to-amber-600 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
            animate={{ x: ["-100%", "200%"] }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          />
        </motion.div>
      </div>
    </div>
  );
}
