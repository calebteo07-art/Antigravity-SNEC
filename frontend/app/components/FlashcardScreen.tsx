import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { motion, AnimatePresence } from "motion/react";
import confetti from "canvas-confetti";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import { XPBar } from "./XPBar";
import { StreakDisplay } from "./StreakDisplay";
import { AchievementManager } from "./AchievementToast";
import { getUserProgress, addXP, checkAndUnlockAchievements, XP_REWARDS } from "../utils/gamification";
import { RotateCcw, ChevronLeft, ChevronRight, Layers, Zap, Sparkles, Trophy } from "lucide-react";

interface Flashcard {
  id: number;
  question: string;
  answer: string;
  tag: string;
}

const FLASHCARDS: Flashcard[] = [
  {
    id: 1,
    question:
      "What is the earliest histological finding in diabetic retinopathy, and what is the first clinically visible sign on fundoscopy?",
    answer:
      "Earliest histological finding: Pericyte loss from retinal capillaries — this occurs before any clinically visible changes and is detected on trypsin digest preparations.\n\nFirst visible fundoscopic sign: Microaneurysms (dot-shaped red lesions) — these form due to weakening of capillary walls after pericyte loss.",
    tag: "Pathology",
  },
  {
    id: 2,
    question:
      "Describe the four major pathological pathways activated by chronic hyperglycemia in diabetic retinopathy.",
    answer:
      "1. Polyol Pathway — Aldose reductase converts excess glucose → sorbitol, causing osmotic stress and cellular damage.\n\n2. PKC Activation — Protein kinase C increases VEGF production and enhances vascular permeability.\n\n3. AGE Formation — Advanced glycation end-products cross-link basement membrane proteins, thickening vessel walls and impairing function.\n\n4. Oxidative Stress — ROS generation damages pericytes and endothelial cells, initiating microvascular changes.",
    tag: "Mechanisms",
  },
  {
    id: 3,
    question:
      "What defines Clinically Significant Macular Edema (CSME) according to ETDRS criteria?",
    answer:
      "ETDRS CSME criteria (any one sufficient):\n• Retinal thickening within 500μm of the foveal center\n• Hard exudates within 500μm of the fovea with adjacent thickening\n• Retinal thickening ≥1 disc area, any portion within 1 disc diameter of the fovea\n\nClinical significance: CSME indicates high risk of visual loss requiring treatment — now primarily with anti-VEGF agents for center-involving DME.",
    tag: "Clinical Criteria",
  },
  {
    id: 4,
    question:
      "How does VEGF-A cause breakdown of the inner blood-retinal barrier in diabetic macular edema?",
    answer:
      "VEGF-A mediates iBRB breakdown through:\n• Phosphorylation of tight junction proteins occludin and ZO-1\n• This disrupts the integrity of inter-endothelial junctions\n• Plasma proteins and fluid leak into extracellular retinal space\n• Results in retinal thickening visible on OCT\n\nTherapeutic implication: Anti-VEGF agents (ranibizumab, aflibercept, bevacizumab) target this pathway and are now first-line for center-involving DME.",
    tag: "Pharmacology",
  },
  {
    id: 5,
    question:
      "Classify diabetic retinopathy and describe the key distinguishing feature between NPDR and PDR.",
    answer:
      "Classification:\n• Non-Proliferative DR (NPDR): Mild, Moderate, Severe\n• Proliferative DR (PDR): The hallmark is neovascularization\n\nKey distinction: PDR is defined by the presence of new blood vessel formation (neovascularization) on the disc (NVD) or elsewhere (NVE) — driven by chronic ischemia and VEGF overexpression.\n\n4-2-1 Rule (Severe NPDR): >20 microaneurysms in all 4 quadrants, venous beading in ≥2 quadrants, or IRMA in ≥1 quadrant.",
    tag: "Classification",
  },
];

const RATINGS = [
  { label: "Again", color: "bg-red-500 hover:bg-red-600", textColor: "text-white", borderColor: "border-red-500", value: 1 },
  { label: "Hard", color: "bg-orange-400 hover:bg-orange-500", textColor: "text-white", borderColor: "border-orange-400", value: 2 },
  { label: "Good", color: "bg-[#14B8A6] hover:bg-[#0D9488]", textColor: "text-white", borderColor: "border-[#14B8A6]", value: 3 },
  { label: "Easy", color: "bg-emerald-500 hover:bg-emerald-600", textColor: "text-white", borderColor: "border-emerald-500", value: 4 },
];

export function FlashcardScreen() {
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [ratedCards, setRatedCards] = useState<Record<number, number>>({});
  const [animating, setAnimating] = useState(false);

  const [userProgress, setUserProgress] = useState(getUserProgress());
  const [newAchievements, setNewAchievements] = useState<string[]>([]);
  const [showXPGain, setShowXPGain] = useState(false);
  const [xpGained, setXpGained] = useState(0);

  const card = FLASHCARDS[currentIndex];
  const progress = ((currentIndex) / FLASHCARDS.length) * 100;
  const remaining = FLASHCARDS.length - Object.keys(ratedCards).length;

  const flipCard = () => {
    if (!animating) setIsFlipped((f) => !f);
  };

  const handleRating = (value: number) => {
    setRatedCards((prev) => ({ ...prev, [card.id]: value }));

    let xpReward = 0;
    if (value === 1) xpReward = XP_REWARDS.flashcardAgain;
    else if (value === 2) xpReward = XP_REWARDS.flashcardHard;
    else if (value === 3) xpReward = XP_REWARDS.flashcardGood;
    else if (value === 4) xpReward = XP_REWARDS.flashcardEasy;

    const result = addXP(xpReward);
    const updatedProgress = getUserProgress();
    updatedProgress.totalCards += 1;
    setUserProgress(updatedProgress);
    setXpGained(xpReward);
    setShowXPGain(true);
    setTimeout(() => setShowXPGain(false), 2000);

    if (value >= 3) {
      confetti({
        particleCount: value === 4 ? 100 : 50,
        spread: value === 4 ? 100 : 70,
        origin: { y: 0.6 },
        colors: value === 4 ? ["#14B8A6", "#F59E0B", "#10B981"] : ["#14B8A6", "#60A5FA"],
      });
    }

    if (result.leveledUp) {
      confetti({
        particleCount: 150,
        spread: 120,
        origin: { y: 0.5 },
        colors: ["#F59E0B", "#FCD34D", "#FBBF24"],
        shapes: ["star"],
      });
    }

    const unlockedAchievements = checkAndUnlockAchievements();
    if (unlockedAchievements.length > 0) {
      setNewAchievements((prev) => [...prev, ...unlockedAchievements]);
    }

    setAnimating(true);
    setIsFlipped(false);

    setTimeout(() => {
      if (currentIndex < FLASHCARDS.length - 1) {
        setCurrentIndex((i) => i + 1);
      } else {
        navigate("/summary");
      }
      setAnimating(false);
    }, 350);
  };

  const goToPrev = () => {
    if (currentIndex > 0 && !animating) {
      setAnimating(true);
      setIsFlipped(false);
      setTimeout(() => {
        setCurrentIndex((i) => i - 1);
        setAnimating(false);
      }, 300);
    }
  };

  const goToNext = () => {
    if (currentIndex < FLASHCARDS.length - 1 && !animating) {
      setAnimating(true);
      setIsFlipped(false);
      setTimeout(() => {
        setCurrentIndex((i) => i + 1);
        setAnimating(false);
      }, 300);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F1F5F9] to-[#E2E8F0] flex flex-col relative overflow-hidden">
      <AchievementManager
        achievements={newAchievements}
        onDismiss={(id) => setNewAchievements((prev) => prev.filter((a) => a !== id))}
      />

      {/* XP Gain Notification */}
      <AnimatePresence>
        {showXPGain && (
          <motion.div
            className="fixed top-6 left-1/2 -translate-x-1/2 z-50 bg-gradient-to-r from-amber-500 to-orange-500 text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-2"
            initial={{ opacity: 0, y: -50, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -30, scale: 0.9 }}
          >
            <Zap size={16} className="fill-white" />
            <span className="font-bold">+{xpGained} XP</span>
            <Sparkles size={14} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <motion.div
        className="bg-gradient-to-r from-[#0D1B2A] via-[#0D2535] to-[#0D1B2A] px-6 py-4 flex items-center justify-between border-b border-white/10 shadow-xl"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <div className="flex items-center gap-3">
          <motion.button
            onClick={() => navigate("/chat")}
            className="text-slate-400 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-white/10"
            whileHover={{ scale: 1.1, x: -3 }}
            whileTap={{ scale: 0.9 }}
          >
            <ChevronLeft size={20} />
          </motion.button>
          <div className="flex items-center gap-2.5">
            <HolographicEyeLogo size={32} animated={true} />
            <span className="text-white" style={{ fontWeight: 700, fontSize: "1.05rem" }}>
              EyeQ
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <StreakDisplay streak={userProgress.streak} size="sm" />
          <div className="flex items-center gap-1.5 text-slate-400">
            <Layers size={14} />
            <span style={{ fontSize: "0.8rem" }}>
              {currentIndex + 1} / {FLASHCARDS.length}
            </span>
          </div>
          <motion.div
            className="bg-[#14B8A6]/20 border border-[#14B8A6]/40 text-[#14B8A6] rounded-full px-3 py-1.5 backdrop-blur-sm"
            style={{ fontSize: "0.75rem", fontWeight: 600 }}
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {remaining} remaining
          </motion.div>
        </div>
      </motion.div>

      {/* XP Progress Bar */}
      <div className="bg-[#0D1B2A] px-6 py-3 border-b border-white/5">
        <XPBar currentXP={userProgress.xp} level={userProgress.level} size="sm" />
      </div>

      {/* Progress Bar */}
      <div className="h-2 bg-slate-200 w-full relative overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-[#14B8A6] via-emerald-400 to-[#0D9488] relative"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
            animate={{ x: ["-100%", "200%"] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          />
        </motion.div>
      </div>

      {/* Topic Label */}
      <div className="flex items-center justify-center mt-6">
        <div className="bg-white border border-slate-200 rounded-full px-4 py-1.5 flex items-center gap-2 shadow-sm">
          <div className="w-2 h-2 rounded-full bg-[#14B8A6]" />
          <span className="text-[#0D1B2A]" style={{ fontSize: "0.8rem", fontWeight: 500 }}>
            Diabetic Retinopathy
          </span>
          <span className="text-slate-400" style={{ fontSize: "0.75rem" }}>
            •
          </span>
          <span className="text-[#14B8A6]" style={{ fontSize: "0.75rem", fontWeight: 500 }}>
            {card.tag}
          </span>
        </div>
      </div>

      {/* Flashcard Area */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-6">
        {/* Card navigation + card */}
        <div className="w-full max-w-2xl flex items-center gap-4">
          <button
            onClick={goToPrev}
            disabled={currentIndex === 0 || animating}
            className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border transition-all ${
              currentIndex === 0 || animating
                ? "border-slate-200 text-slate-300 cursor-not-allowed"
                : "border-slate-300 text-slate-500 hover:border-[#14B8A6] hover:text-[#14B8A6] hover:bg-white"
            }`}
          >
            <ChevronLeft size={18} />
          </button>

          {/* The Flashcard */}
          <div
            className="flex-1"
            style={{ perspective: "1500px" }}
          >
            <motion.div
              onClick={flipCard}
              className="relative cursor-pointer"
              style={{
                transformStyle: "preserve-3d",
                minHeight: "380px",
              }}
              animate={{
                rotateY: isFlipped ? 180 : 0,
              }}
              transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
              whileHover={{ scale: 1.02, y: -5 }}
            >
              {/* Front */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-white to-slate-50 rounded-2xl border-2 border-slate-200 shadow-2xl p-8 flex flex-col"
                style={{ backfaceVisibility: "hidden", WebkitBackfaceVisibility: "hidden" }}
                whileHover={{ boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.15)" }}
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="bg-[#0D1B2A] text-white rounded-full px-3 py-1" style={{ fontSize: "0.7rem", fontWeight: 600, letterSpacing: "0.05em" }}>
                    QUESTION
                  </span>
                  <div className="flex items-center gap-1.5 text-slate-400" style={{ fontSize: "0.75rem" }}>
                    <RotateCcw size={12} />
                    Click to reveal
                  </div>
                </div>
                <div className="flex-1 flex items-center justify-center">
                  <p className="text-[#0D1B2A] text-center" style={{ fontSize: "1.05rem", lineHeight: 1.7, fontWeight: 500 }}>
                    {card.question}
                  </p>
                </div>
                <div className="flex justify-center gap-1 mt-4">
                  {FLASHCARDS.map((_, idx) => (
                    <div
                      key={idx}
                      className={`h-1.5 rounded-full transition-all ${
                        idx === currentIndex
                          ? "w-6 bg-[#14B8A6]"
                          : ratedCards[FLASHCARDS[idx].id]
                          ? "w-2 bg-emerald-400"
                          : "w-2 bg-slate-200"
                      }`}
                    />
                  ))}
                </div>
              </motion.div>

              {/* Back */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-teal-50 to-cyan-50 rounded-2xl border-2 border-[#14B8A6]/40 shadow-2xl p-8 flex flex-col overflow-y-auto"
                style={{
                  backfaceVisibility: "hidden",
                  WebkitBackfaceVisibility: "hidden",
                  transform: "rotateY(180deg)",
                }}
                whileHover={{ boxShadow: "0 25px 50px -12px rgba(20, 184, 166, 0.2)" }}
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="bg-[#14B8A6] text-white rounded-full px-3 py-1" style={{ fontSize: "0.7rem", fontWeight: 600, letterSpacing: "0.05em" }}>
                    ANSWER
                  </span>
                  <div className="flex items-center gap-1.5 text-slate-400" style={{ fontSize: "0.75rem" }}>
                    <RotateCcw size={12} />
                    Click to flip back
                  </div>
                </div>
                <div className="flex-1">
                  <div className="text-slate-700 whitespace-pre-line" style={{ fontSize: "0.9rem", lineHeight: 1.75 }}>
                    {card.answer}
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </div>

          <button
            onClick={goToNext}
            disabled={currentIndex === FLASHCARDS.length - 1 || animating}
            className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border transition-all ${
              currentIndex === FLASHCARDS.length - 1 || animating
                ? "border-slate-200 text-slate-300 cursor-not-allowed"
                : "border-slate-300 text-slate-500 hover:border-[#14B8A6] hover:text-[#14B8A6] hover:bg-white"
            }`}
          >
            <ChevronRight size={18} />
          </button>
        </div>

        {/* Rating Buttons (shown when flipped) */}
        <div
          className={`w-full max-w-2xl mt-6 transition-all duration-300 ${
            isFlipped ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4 pointer-events-none"
          }`}
        >
          <p className="text-center text-slate-500 mb-3" style={{ fontSize: "0.8rem", fontWeight: 500 }}>
            How well did you know this?
          </p>
          <div className="grid grid-cols-4 gap-3">
            {RATINGS.map((rating, idx) => (
              <motion.button
                key={rating.label}
                onClick={(e) => {
                  e.stopPropagation();
                  handleRating(rating.value);
                }}
                className={`${rating.color} ${rating.textColor} py-3.5 rounded-xl shadow-lg relative overflow-hidden`}
                style={{ fontWeight: 700, fontSize: "0.95rem" }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                whileHover={{ scale: 1.08, y: -3 }}
                whileTap={{ scale: 0.95 }}
              >
                <motion.div
                  className="absolute inset-0 bg-white"
                  initial={{ opacity: 0 }}
                  whileHover={{ opacity: 0.2 }}
                  transition={{ duration: 0.2 }}
                />
                <span className="relative z-10">{rating.label}</span>
              </motion.button>
            ))}
          </div>
          <div className="flex justify-between mt-2 px-1">
            <span className="text-red-400" style={{ fontSize: "0.7rem" }}>Needs more practice</span>
            <span className="text-emerald-500" style={{ fontSize: "0.7rem" }}>Mastered</span>
          </div>
        </div>

        {/* Hint when not flipped */}
        {!isFlipped && (
          <div className="mt-6 text-center">
            <p className="text-slate-400" style={{ fontSize: "0.8rem" }}>
              Tap the card to reveal the answer
            </p>
          </div>
        )}
      </div>

      {/* Bottom action */}
      <div className="flex justify-center pb-6">
        <button
          onClick={() => navigate("/summary")}
          className="text-slate-400 hover:text-[#14B8A6] transition-colors flex items-center gap-1.5"
          style={{ fontSize: "0.8rem" }}
        >
          Skip to Summary
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  );
}
