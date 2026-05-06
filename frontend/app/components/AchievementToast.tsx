import React, { useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Trophy, X } from "lucide-react";
import confetti from "canvas-confetti";
import { ACHIEVEMENTS } from "../utils/gamification";

interface AchievementToastProps {
  achievementId: string;
  onClose: () => void;
}

export function AchievementToast({ achievementId, onClose }: AchievementToastProps) {
  const achievement = ACHIEVEMENTS.find((a) => a.id === achievementId);

  useEffect(() => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ["#14B8A6", "#F59E0B", "#8B5CF6", "#EC4899"],
    });

    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);

  if (!achievement) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -100, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.9 }}
      transition={{ type: "spring", damping: 15, stiffness: 300 }}
      className="fixed top-6 right-6 z-50 max-w-sm"
    >
      <div className="bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-400 rounded-2xl shadow-2xl overflow-hidden">
        <div className="h-1 bg-gradient-to-r from-amber-400 via-orange-400 to-amber-400" />
        <div className="p-5 relative">
          <button
            onClick={onClose}
            className="absolute top-3 right-3 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={16} />
          </button>

          <div className="flex items-start gap-4">
            <motion.div
              className="flex-shrink-0 w-14 h-14 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg"
              animate={{
                rotate: [0, -10, 10, -10, 0],
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 0.6,
                ease: "easeInOut",
              }}
            >
              <span className="text-3xl">{achievement.icon}</span>
            </motion.div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <Trophy size={14} className="text-amber-600" />
                <span className="text-amber-800 font-semibold uppercase tracking-wide" style={{ fontSize: "0.65rem" }}>
                  Achievement Unlocked!
                </span>
              </div>
              <h4 className="text-[#0D1B2A] font-bold mb-1" style={{ fontSize: "1rem" }}>
                {achievement.name}
              </h4>
              <p className="text-slate-600" style={{ fontSize: "0.85rem", lineHeight: 1.4 }}>
                {achievement.description}
              </p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

interface AchievementManagerProps {
  achievements: string[];
  onDismiss: (id: string) => void;
}

export function AchievementManager({ achievements, onDismiss }: AchievementManagerProps) {
  return (
    <AnimatePresence mode="popLayout">
      {achievements.map((id, index) => (
        <motion.div
          key={id}
          style={{ top: `${24 + index * 140}px` }}
          className="fixed right-6 z-50"
        >
          <AchievementToast achievementId={id} onClose={() => onDismiss(id)} />
        </motion.div>
      ))}
    </AnimatePresence>
  );
}
