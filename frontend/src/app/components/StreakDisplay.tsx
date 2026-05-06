import React from "react";
import { motion } from "motion/react";
import { Flame } from "lucide-react";

interface StreakDisplayProps {
  streak: number;
  size?: "sm" | "md" | "lg";
  animated?: boolean;
}

export function StreakDisplay({ streak, size = "md", animated = true }: StreakDisplayProps) {
  const iconSizes = { sm: 14, md: 18, lg: 24 };
  const textSizes = { sm: "text-sm", md: "text-base", lg: "text-lg" };
  const paddingSizes = { sm: "px-2 py-1", md: "px-3 py-1.5", lg: "px-4 py-2" };

  return (
    <motion.div
      className={`inline-flex items-center gap-1.5 rounded-full ${paddingSizes[size]}`}
      style={{
        background: "linear-gradient(135deg, rgba(251, 146, 60, 0.15) 0%, rgba(239, 68, 68, 0.15) 100%)",
        border: "1px solid rgba(251, 146, 60, 0.3)",
      }}
      whileHover={animated ? { scale: 1.05 } : undefined}
      animate={
        animated && streak > 0
          ? {
              boxShadow: [
                "0 0 0 0 rgba(251, 146, 60, 0)",
                "0 0 0 4px rgba(251, 146, 60, 0.1)",
                "0 0 0 0 rgba(251, 146, 60, 0)",
              ],
            }
          : undefined
      }
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      <motion.div
        animate={
          animated && streak > 0
            ? {
                scale: [1, 1.2, 1],
                rotate: [0, -10, 10, -10, 0],
              }
            : undefined
        }
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        <Flame
          size={iconSizes[size]}
          className="text-orange-500 fill-orange-500"
        />
      </motion.div>
      <span className={`font-bold ${textSizes[size]}`} style={{ color: "#EA580C" }}>
        {streak}
      </span>
      <span className={`${textSizes[size]} text-orange-600 font-medium`}>
        {streak === 1 ? "day" : "days"}
      </span>
    </motion.div>
  );
}
