import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { motion } from "motion/react";
import confetti from "canvas-confetti";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import { XPBar } from "./XPBar";
import { StreakDisplay } from "./StreakDisplay";
import { ParticleBackground } from "./ParticleBackground";
import { getUserProgress, addXP, checkAndUnlockAchievements, XP_REWARDS, ACHIEVEMENTS } from "../utils/gamification";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import {
  BookOpen,
  Layers,
  CheckCircle2,
  ChevronRight,
  Home,
  Trophy,
  RotateCcw,
  ArrowRight,
  HelpCircle,
  Lightbulb,
  Zap,
  Award,
  Target,
} from "lucide-react";

function loadSession() {
  try {
    const s = JSON.parse(sessionStorage.getItem("eyeq_session") || "{}");
    const cards: { front: string; back: string; topic_tag: string }[] = Array.isArray(s.cards) ? s.cards : [];
    return {
      topic: s.topic || "Ophthalmology",
      flashcardsGenerated: cards.length,
      questionsAnswered: Math.max(0, Math.floor((s.messageCount || 2) / 2)),
      cards,
    };
  } catch {
    return { topic: "Ophthalmology", flashcardsGenerated: 0, questionsAnswered: 0, cards: [] };
  }
}

const TAG_COLORS: Record<string, string> = {
  glaucoma: "bg-purple-100 text-purple-700",
  retina: "bg-blue-100 text-blue-700",
  cornea: "bg-amber-100 text-amber-700",
  cataract: "bg-orange-100 text-orange-700",
  medications: "bg-[#14B8A6]/15 text-[#0D6B60]",
  default: "bg-slate-100 text-slate-700",
};

const PREVIEW_CARDS = [
  {
    id: 1,
    tag: "Pathology",
    tagColor: "bg-purple-100 text-purple-700",
    question: "Earliest histological finding in diabetic retinopathy?",
    preview: "Pericyte loss from retinal capillaries — occurs before any clinically visible changes...",
  },
  {
    id: 2,
    tag: "Mechanisms",
    tagColor: "bg-blue-100 text-blue-700",
    question: "Four pathological pathways in diabetic retinopathy?",
    preview: "Polyol pathway, PKC activation, AGE formation, Oxidative stress...",
  },
  {
    id: 3,
    tag: "Clinical",
    tagColor: "bg-amber-100 text-amber-700",
    question: "ETDRS CSME criteria definition?",
    preview: "Retinal thickening within 500μm of the foveal center; Hard exudates within...",
  },
  {
    id: 4,
    tag: "Pharmacology",
    tagColor: "bg-[#14B8A6]/15 text-[#0D6B60]",
    question: "How does VEGF-A cause iBRB breakdown?",
    preview: "Phosphorylation of tight junction proteins occludin and ZO-1...",
  },
  {
    id: 5,
    tag: "Classification",
    tagColor: "bg-slate-100 text-slate-700",
    question: "Key difference between NPDR and PDR?",
    preview: "PDR defined by neovascularization (NVD/NVE); 4-2-1 rule for severe NPDR...",
  },
];


export function SummaryScreen() {
  const navigate = useNavigate();
  const [userProgress, setUserProgress] = useState(getUserProgress());
  const sessionData = loadSession();

  const userData = (() => {
    try {
      return JSON.parse(sessionStorage.getItem("eyeq_user") || "{}");
    } catch {
      return { fullName: "Student" };
    }
  })();
  const firstName = (userData.fullName || "Student").split(" ")[0];

  useEffect(() => {
    addXP(XP_REWARDS.sessionComplete);
    setUserProgress(getUserProgress());
    checkAndUnlockAchievements();

    confetti({ particleCount: 150, spread: 120, origin: { y: 0.5 }, colors: ["#14B8A6", "#F59E0B", "#8B5CF6", "#EC4899"] });
    setTimeout(() => {
      confetti({ particleCount: 100, spread: 100, origin: { y: 0.6 }, colors: ["#10B981", "#14B8A6", "#06B6D4"] });
    }, 500);
  }, []);

  const realStats = [
    { icon: BookOpen, label: "Topic Covered", value: sessionData.topic, iconColor: "text-indigo-500", bgColor: "bg-indigo-50" },
    { icon: Layers, label: "Flashcards Generated", value: `${sessionData.flashcardsGenerated}`, subvalue: "ready for review", iconColor: "text-amber-500", bgColor: "bg-amber-50" },
    { icon: HelpCircle, label: "Questions Explored", value: `${sessionData.questionsAnswered}`, subvalue: "in-depth exchanges", iconColor: "text-emerald-500", bgColor: "bg-emerald-50" },
  ];

  const previewCards = sessionData.cards.slice(0, 6).map((c, i) => ({
    id: i + 1,
    tag: c.topic_tag,
    tagColor: TAG_COLORS[c.topic_tag.toLowerCase()] ?? TAG_COLORS.default,
    question: c.front,
    preview: c.back.slice(0, 80) + (c.back.length > 80 ? "…" : ""),
  }));

  const performanceData = [
    { name: "Easy", value: 2, color: "#10B981" },
    { name: "Good", value: 2, color: "#14B8A6" },
    { name: "Hard", value: 1, color: "#F59E0B" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0D1B2A] via-[#0D2535] to-[#0D1B2A] flex flex-col relative overflow-hidden">
      <ParticleBackground density={50} color="#14B8A6" />

      {/* Header */}
      <motion.div
        className="bg-gradient-to-r from-[#0D1B2A]/80 via-[#0D2B3A]/80 to-[#0D1B2A]/80 backdrop-blur-xl px-6 py-5 border-b border-white/10 shadow-2xl"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <HolographicEyeLogo size={36} animated={true} />
            <span className="text-white" style={{ fontWeight: 700, fontSize: "1.2rem" }}>
              EyeQ
            </span>
          </div>
          <div className="flex items-center gap-4">
            <StreakDisplay streak={userProgress.streak} size="md" />
            <motion.button
              onClick={() => navigate("/")}
              className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors px-3 py-2 rounded-lg hover:bg-white/10"
              style={{ fontSize: "0.85rem" }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Home size={16} />
              Home
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Animated success bar */}
      <motion.div
        className="h-2 bg-gradient-to-r from-[#14B8A6] via-emerald-400 to-[#14B8A6] relative overflow-hidden"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 1, ease: "easeOut" }}
        style={{ transformOrigin: "left" }}
      >
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent"
          animate={{ x: ["-100%", "200%"] }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        />
      </motion.div>

      <div className="flex-1 max-w-5xl mx-auto w-full px-6 py-10 relative z-10">
        {/* Success Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-[#14B8A6] to-[#0D9488] shadow-2xl shadow-[#14B8A6]/50 mb-6 relative"
            animate={{
              scale: [1, 1.1, 1],
              rotate: [0, 360],
            }}
            transition={{
              scale: { duration: 2, repeat: Infinity },
              rotate: { duration: 20, repeat: Infinity, ease: "linear" },
            }}
          >
            <Trophy size={36} className="text-white" />
            <motion.div
              className="absolute inset-0 rounded-full bg-[#14B8A6]"
              animate={{ scale: [1, 1.4], opacity: [0.5, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </motion.div>
          <motion.h1
            className="text-white mb-3"
            style={{ fontSize: "2.5rem", fontWeight: 800, textShadow: "0 2px 10px rgba(0,0,0,0.3)" }}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
          >
            Outstanding Work!
          </motion.h1>
          <motion.p
            className="text-slate-300 max-w-md mx-auto"
            style={{ fontSize: "1.05rem", lineHeight: 1.6 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            Excellent progress, <span className="text-[#14B8A6] font-semibold">{firstName}</span>! You've completed your study session on{" "}
            <span className="text-white font-semibold">{sessionData.topic}</span>.
          </motion.p>
        </motion.div>

        {/* XP Progress */}
        <motion.div
          className="mb-10 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6 shadow-2xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <XPBar currentXP={userProgress.xp} level={userProgress.level} size="lg" />
        </motion.div>

        {/* Stats Grid with enhanced design */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-5 mb-10">
          {realStats.map((stat, idx) => (
            <motion.div
              key={idx}
              className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-6 shadow-xl hover:bg-white/15 transition-all"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 + idx * 0.1, duration: 0.5 }}
              whileHover={{ scale: 1.05, y: -5 }}
            >
              <motion.div
                className={`w-11 h-11 rounded-xl ${stat.bgColor} flex items-center justify-center mb-4 shadow-lg`}
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
              >
                <stat.icon size={20} className={stat.iconColor} />
              </motion.div>
              <div className="text-white mb-1" style={{ fontSize: "1.5rem", fontWeight: 800, lineHeight: 1 }}>
                {stat.value}
              </div>
              {stat.subvalue && (
                <div className="text-[#14B8A6]" style={{ fontSize: "0.75rem", fontWeight: 600, marginBottom: "4px" }}>
                  {stat.subvalue}
                </div>
              )}
              <div className="text-slate-300" style={{ fontSize: "0.8rem", fontWeight: 500 }}>
                {stat.label}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Performance Chart & Subtopics in 2 columns */}
        <div className="grid md:grid-cols-2 gap-6 mb-10">
          {/* Performance Chart */}
          <motion.div
            className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-6 shadow-xl"
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.1, duration: 0.5 }}
          >
            <div className="flex items-center gap-2 mb-4">
              <Target size={18} className="text-[#14B8A6]" />
              <h3 className="text-white font-bold" style={{ fontSize: "1rem" }}>
                Performance Breakdown
              </h3>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={performanceData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {performanceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(13, 27, 42, 0.95)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "8px",
                    color: "#fff",
                  }}
                />
                <Legend
                  wrapperStyle={{ color: "#fff" }}
                  iconType="circle"
                />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Subtopics */}
          <motion.div
            className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-6 shadow-xl"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2, duration: 0.5 }}
          >
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb size={18} className="text-amber-500" />
              <h3 className="text-white font-bold" style={{ fontSize: "1rem" }}>
                Topics Mastered
              </h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {["Pathophysiology", "Clinical Staging", "Management", "Investigations"].map((topic, idx) => (
                <motion.div
                  key={idx}
                  className="flex items-center gap-1.5 bg-[#14B8A6]/20 text-[#14B8A6] border border-[#14B8A6]/40 rounded-full px-3 py-1.5 backdrop-blur-sm"
                  style={{ fontSize: "0.85rem", fontWeight: 600 }}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.3 + idx * 0.1 }}
                  whileHover={{ scale: 1.1 }}
                >
                  <CheckCircle2 size={14} />
                  {topic}
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Achievements Section */}
        <motion.div
          className="mb-10 bg-gradient-to-br from-amber-500/20 to-orange-500/20 backdrop-blur-xl rounded-2xl border border-amber-400/30 p-6 shadow-xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3, duration: 0.5 }}
        >
          <div className="flex items-center gap-2 mb-4">
            <Award size={20} className="text-amber-400" />
            <h3 className="text-white font-bold" style={{ fontSize: "1.1rem" }}>
              Your Achievements
            </h3>
          </div>
          <div className="flex flex-wrap gap-3">
            {userProgress.achievements.slice(0, 6).map((achievementId, idx) => {
              const achievement = ACHIEVEMENTS.find((a) => a.id === achievementId);
              if (!achievement) return null;
              return (
                <motion.div
                  key={achievementId}
                  className="flex items-center gap-2 bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 backdrop-blur-sm"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.4 + idx * 0.1 }}
                  whileHover={{ scale: 1.1, y: -2 }}
                >
                  <span className="text-2xl">{achievement.icon}</span>
                  <div>
                    <div className="text-white font-semibold" style={{ fontSize: "0.85rem" }}>
                      {achievement.name}
                    </div>
                    <div className="text-slate-300" style={{ fontSize: "0.7rem" }}>
                      {achievement.description}
                    </div>
                  </div>
                </motion.div>
              );
            })}
            {userProgress.achievements.length === 0 && (
              <p className="text-slate-300" style={{ fontSize: "0.9rem" }}>
                Keep learning to unlock achievements!
              </p>
            )}
          </div>
        </motion.div>

        {/* Flashcard Preview Grid */}
        <motion.div
          className="mb-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.5 }}
        >
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <Layers size={20} className="text-[#14B8A6]" />
              <h2 className="text-white font-bold" style={{ fontSize: "1.2rem" }}>
                Generated Flashcards
              </h2>
              <motion.span
                className="bg-[#14B8A6] text-white rounded-full w-7 h-7 flex items-center justify-center shadow-lg"
                style={{ fontSize: "0.8rem", fontWeight: 700 }}
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {previewCards.length}
              </motion.span>
            </div>
            <span className="text-slate-300" style={{ fontSize: "0.85rem", fontWeight: 500 }}>
              Ready for spaced repetition
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {previewCards.map((card, idx) => (
              <motion.div
                key={card.id}
                className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-5 shadow-xl hover:bg-white/15 hover:border-[#14B8A6]/50 transition-all cursor-pointer group"
                onClick={() => navigate("/flashcards")}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.6 + idx * 0.1 }}
                whileHover={{ scale: 1.03, y: -5 }}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className={`text-xs rounded-full px-3 py-1 font-semibold ${card.tagColor} backdrop-blur-sm`}>
                    {card.tag}
                  </span>
                  <span className="text-slate-400 font-mono" style={{ fontSize: "0.75rem" }}>
                    #{idx + 1}
                  </span>
                </div>
                <p className="text-white mb-2.5" style={{ fontSize: "0.9rem", fontWeight: 600, lineHeight: 1.5 }}>
                  {card.question}
                </p>
                <p className="text-slate-300" style={{ fontSize: "0.8rem", lineHeight: 1.6 }}>
                  {card.preview}
                </p>
                <div className="flex items-center gap-1 text-[#14B8A6] mt-4 opacity-0 group-hover:opacity-100 transition-opacity font-semibold" style={{ fontSize: "0.8rem" }}>
                  <span>Review now</span>
                  <ChevronRight size={14} />
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          className="flex flex-col sm:flex-row gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2, duration: 0.5 }}
        >
          <motion.button
            onClick={() => navigate("/flashcards")}
            className="flex-1 flex items-center justify-center gap-3 py-5 rounded-2xl bg-gradient-to-r from-[#14B8A6] to-[#0D9488] text-white shadow-2xl shadow-[#14B8A6]/40 relative overflow-hidden group"
            style={{ fontWeight: 700, fontSize: "1.1rem" }}
            whileHover={{ scale: 1.03, y: -3 }}
            whileTap={{ scale: 0.98 }}
          >
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
              initial={{ x: "-100%" }}
              whileHover={{ x: "200%" }}
              transition={{ duration: 0.8 }}
            />
            <Layers size={22} />
            <span className="relative z-10">Review Cards Now</span>
            <ArrowRight size={20} />
          </motion.button>
          <motion.button
            onClick={() => navigate("/")}
            className="flex-1 flex items-center justify-center gap-3 py-5 rounded-2xl bg-white/10 border-2 border-white/20 text-white backdrop-blur-xl shadow-xl hover:bg-white/15 transition-all"
            style={{ fontWeight: 600, fontSize: "1.05rem" }}
            whileHover={{ scale: 1.03, y: -3 }}
            whileTap={{ scale: 0.98 }}
          >
            <Home size={20} />
            New Session
          </motion.button>
        </motion.div>

        {/* Footnote */}
        <motion.p
          className="text-center text-slate-300 mt-8"
          style={{ fontSize: "0.85rem" }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.2 }}
        >
          Your flashcards are scheduled using spaced repetition. Next review recommended in{" "}
          <span className="text-[#14B8A6] font-semibold">1 day</span>.
        </motion.p>
      </div>
    </div>
  );
}
