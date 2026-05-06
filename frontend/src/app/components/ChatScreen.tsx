import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router";
import { motion, AnimatePresence } from "motion/react";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import { XPBar } from "./XPBar";
import { StreakDisplay } from "./StreakDisplay";
import { AchievementManager } from "./AchievementToast";
import { getUserProgress, addXP, updateStreak, checkAndUnlockAchievements, XP_REWARDS } from "../utils/gamification";

async function apiChat(
  studentId: string,
  messages: { role: string; content: string }[]
): Promise<{ explanation: string; mechanism: string; clinicalPearl: string; checkUnderstanding: string }> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id: studentId, messages }),
  });
  if (!res.ok) throw new Error("Chat request failed");
  return res.json();
}

async function apiEndSession(
  studentId: string,
  messages: { role: string; content: string }[],
  topic: string
): Promise<{ session_id: string; cards: unknown[] }> {
  const res = await fetch("/api/end-session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id: studentId, messages, topic }),
  });
  if (!res.ok) throw new Error("End session failed");
  return res.json();
}
import {
  Send,
  BookOpen,
  Layers,
  ChevronRight,
  Lightbulb,
  Stethoscope,
  Brain,
  HelpCircle,
  User,
  Bot,
  RotateCcw,
  ArrowRight,
  Zap,
} from "lucide-react";

interface AIMessage {
  type: "ai";
  id: string;
  sections: {
    explanation: string;
    mechanism: string;
    clinicalPearl: string;
    checkUnderstanding: string;
  };
}

interface UserMessage {
  type: "user";
  id: string;
  text: string;
}

type Message = AIMessage | UserMessage;

const SAMPLE_TOPIC = "Diabetic Retinopathy";
const INITIAL_MESSAGES: Message[] = [
  {
    type: "ai",
    id: "1",
    sections: {
      explanation:
        "Diabetic retinopathy (DR) is a microvascular complication of diabetes mellitus affecting the retinal vasculature. It is the leading cause of preventable blindness in working-age adults globally. DR is classified into non-proliferative (NPDR) and proliferative (PDR) stages, with macular edema potentially occurring at any stage.",
      mechanism:
        "Chronic hyperglycemia triggers multiple pathological pathways: (1) Polyol pathway activation — excess glucose is converted to sorbitol via aldose reductase, causing osmotic stress. (2) Protein kinase C (PKC) activation — increases VEGF production and vascular permeability. (3) Advanced glycation end-products (AGEs) — cross-link basement membrane proteins, thickening vessel walls. (4) Oxidative stress — reactive oxygen species damage pericytes, the primary protective cells of retinal capillaries.",
      clinicalPearl:
        "⚡ Pericyte loss is the earliest histological finding in diabetic retinopathy — occurring before any clinically visible changes. This is why trypsin digest preparations of retinal vasculature remain a gold standard for early research detection. Clinically, microaneurysms (dot-shaped red lesions) are the first visible sign on fundoscopy.",
      checkUnderstanding:
        "Why does pericyte loss lead to microaneurysm formation in diabetic retinopathy? What role does VEGF play in the transition from NPDR to PDR, and what therapeutic implications does this have?",
    },
  },
];

const AI_RESPONSES: Record<string, AIMessage["sections"]> = {
  default: {
    explanation:
      "Macular edema (DME) in diabetes occurs when fluid accumulates in the macula — the central, high-acuity region of the retina. It is the most common cause of vision loss in diabetic retinopathy and can occur at any stage of the disease.",
    mechanism:
      "Breakdown of the inner blood-retinal barrier (iBRB) is central to DME pathogenesis. VEGF-A upregulation causes phosphorylation of occludin and ZO-1 tight junction proteins, increasing endothelial permeability. This allows plasma proteins and fluid to leak into the extracellular space, causing retinal thickening detectable on optical coherence tomography (OCT).",
    clinicalPearl:
      "⚡ Clinically Significant Macular Edema (CSME) — defined by the ETDRS criteria — includes any retinal thickening within 500μm of the foveal center. Anti-VEGF agents (ranibizumab, aflibercept, bevacizumab) have become first-line treatment, superseding laser photocoagulation for center-involving DME.",
    checkUnderstanding:
      "A 54-year-old with Type 2 DM presents with blurred central vision. OCT shows foveal thickening of 380μm. What is the diagnosis? Outline your management approach, including the rationale for your first-line treatment choice.",
  },
};

function AIMessageBubble({ message }: { message: AIMessage }) {
  return (
    <motion.div
      className="flex gap-3 items-start"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      <motion.div
        className="flex-shrink-0 w-8 h-8 rounded-full bg-[#14B8A6]/20 border border-[#14B8A6]/40 flex items-center justify-center mt-1"
        whileHover={{ scale: 1.1, rotate: 360 }}
        transition={{ duration: 0.3 }}
      >
        <Bot size={15} className="text-[#14B8A6]" />
      </motion.div>
      <div className="flex-1 max-w-[calc(100%-3rem)]">
        <motion.div
          className="bg-white rounded-2xl rounded-tl-sm border border-slate-200 shadow-sm overflow-hidden"
          whileHover={{ boxShadow: "0 10px 30px rgba(0, 0, 0, 0.1)" }}
          transition={{ duration: 0.2 }}
        >
          {/* Section: Explanation */}
          <div className="border-b border-slate-100">
            <div className="flex items-center gap-2 px-4 py-2.5 bg-slate-50 border-b border-slate-100">
              <BookOpen size={13} className="text-[#14B8A6]" />
              <span className="text-[#0D1B2A]" style={{ fontSize: "0.7rem", fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase" }}>
                Explanation
              </span>
            </div>
            <p className="px-4 py-3 text-slate-700" style={{ fontSize: "0.875rem", lineHeight: 1.7 }}>
              {message.sections.explanation}
            </p>
          </div>

          {/* Section: Mechanism */}
          <div className="border-b border-slate-100">
            <div className="flex items-center gap-2 px-4 py-2.5 bg-slate-50 border-b border-slate-100">
              <Brain size={13} className="text-indigo-500" />
              <span className="text-[#0D1B2A]" style={{ fontSize: "0.7rem", fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase" }}>
                Mechanism
              </span>
            </div>
            <p className="px-4 py-3 text-slate-700" style={{ fontSize: "0.875rem", lineHeight: 1.7 }}>
              {message.sections.mechanism}
            </p>
          </div>

          {/* Section: Clinical Pearl */}
          <div className="border-b border-slate-100">
            <div className="flex items-center gap-2 px-4 py-2.5 bg-amber-50 border-b border-amber-100">
              <Lightbulb size={13} className="text-amber-500" />
              <span className="text-amber-800" style={{ fontSize: "0.7rem", fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase" }}>
                Clinical Pearl
              </span>
            </div>
            <p className="px-4 py-3 text-slate-700" style={{ fontSize: "0.875rem", lineHeight: 1.7 }}>
              {message.sections.clinicalPearl}
            </p>
          </div>

          {/* Section: Check Your Understanding */}
          <div>
            <div className="flex items-center gap-2 px-4 py-2.5 bg-[#14B8A6]/8 border-b border-[#14B8A6]/15">
              <HelpCircle size={13} className="text-[#0D9488]" />
              <span className="text-[#0D6B60]" style={{ fontSize: "0.7rem", fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase" }}>
                Check Your Understanding
              </span>
            </div>
            <p className="px-4 py-3 text-slate-700" style={{ fontSize: "0.875rem", lineHeight: 1.7, fontStyle: "italic" }}>
              {message.sections.checkUnderstanding}
            </p>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}

function UserMessageBubble({ message }: { message: UserMessage }) {
  return (
    <motion.div
      className="flex gap-3 items-start justify-end"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      <motion.div
        className="max-w-[75%] bg-gradient-to-br from-[#0D1B2A] to-[#0D2B3A] text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-sm"
        style={{ fontSize: "0.9rem", lineHeight: 1.6 }}
        whileHover={{ scale: 1.02 }}
      >
        {message.text}
      </motion.div>
      <motion.div
        className="flex-shrink-0 w-8 h-8 rounded-full bg-[#0D1B2A] flex items-center justify-center mt-1"
        whileHover={{ scale: 1.1 }}
      >
        <User size={15} className="text-white" />
      </motion.div>
    </motion.div>
  );
}

export function ChatScreen() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isEndingSession, setIsEndingSession] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const [userProgress, setUserProgress] = useState(getUserProgress());
  const [newAchievements, setNewAchievements] = useState<string[]>([]);
  const [showXPGain, setShowXPGain] = useState(false);
  const [xpGained, setXpGained] = useState(0);

  const userData = (() => {
    try {
      return JSON.parse(sessionStorage.getItem("eyeq_user") || "{}");
    } catch {
      return { fullName: "Student" };
    }
  })();

  const studentId: string = userData.student_id || "anonymous";
  const studentName: string = userData.fullName || "Student";
  const firstName = studentName.split(" ")[0];

  useEffect(() => {
    updateStreak();
    setUserProgress(getUserProgress());
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const buildApiHistory = (uiMessages: Message[]) =>
    uiMessages.flatMap((msg): { role: string; content: string }[] => {
      if (msg.type === "user") return [{ role: "user", content: msg.text }];
      const s = msg.sections;
      return [{
        role: "assistant",
        content: `**Explanation:** ${s.explanation}\n\n**Mechanism:** ${s.mechanism}\n\n**Clinical Pearl:** ${s.clinicalPearl}\n\n**Check Your Understanding:** ${s.checkUnderstanding}`,
      }];
    });

  const sendMessage = async () => {
    if (!input.trim() || isTyping) return;

    const userMsg: UserMessage = { type: "user", id: Date.now().toString(), text: input.trim() };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput("");
    setIsTyping(true);

    addXP(XP_REWARDS.chatMessage);
    setUserProgress(getUserProgress());
    setXpGained(XP_REWARDS.chatMessage);
    setShowXPGain(true);
    setTimeout(() => setShowXPGain(false), 2000);

    const unlocked = checkAndUnlockAchievements();
    if (unlocked.length > 0) setNewAchievements((prev) => [...prev, ...unlocked]);

    try {
      const sections = await apiChat(studentId, buildApiHistory(nextMessages));
      const aiMsg: AIMessage = { type: "ai", id: (Date.now() + 1).toString(), sections };
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      const aiMsg: AIMessage = {
        type: "ai",
        id: (Date.now() + 1).toString(),
        sections: {
          explanation: "Could not reach the backend. Make sure the API server is running.",
          mechanism: "",
          clinicalPearl: "",
          checkUnderstanding: "",
        },
      };
      setMessages((prev) => [...prev, aiMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const endSession = async (destination: "/summary" | "/flashcards") => {
    if (isEndingSession) return;
    setIsEndingSession(true);
    const topic = SAMPLE_TOPIC;
    const apiMsgs = buildApiHistory(messages);
    try {
      const result = await apiEndSession(studentId, apiMsgs, topic);
      sessionStorage.setItem("eyeq_session", JSON.stringify({ ...result, topic, messageCount: messages.length }));
    } catch {
      sessionStorage.setItem("eyeq_session", JSON.stringify({ session_id: "unknown", cards: [], topic, messageCount: messages.length }));
    }
    navigate(destination);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-resize
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
  };

  return (
    <div className="h-screen flex bg-[#F8FAFC] overflow-hidden relative">
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
          </motion.div>
        )}
      </AnimatePresence>

      {/* Left Sidebar */}
      <motion.div
        className="w-64 flex-shrink-0 bg-[#0D1B2A] flex flex-col"
        initial={{ x: -264 }}
        animate={{ x: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        {/* Logo */}
        <div className="px-5 py-5 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <HolographicEyeLogo size={32} animated={true} />
            <div>
              <span className="text-white" style={{ fontSize: "1.1rem", fontWeight: 700, letterSpacing: "-0.01em" }}>
                EyeQ
              </span>
              <div className="text-[#14B8A6]" style={{ fontSize: "0.6rem", letterSpacing: "0.12em", fontWeight: 500 }}>
                MEDICAL EDUCATION
              </div>
            </div>
          </div>
        </div>

        {/* Progress Stats */}
        <div className="px-5 py-4 border-b border-white/10 space-y-3">
          <XPBar currentXP={userProgress.xp} level={userProgress.level} size="sm" />
          <div className="flex justify-center">
            <StreakDisplay streak={userProgress.streak} size="sm" />
          </div>
        </div>

        {/* Student Info */}
        <div className="px-5 py-4 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-[#14B8A6]/20 border border-[#14B8A6]/40 flex items-center justify-center">
              <User size={15} className="text-[#14B8A6]" />
            </div>
            <div>
              <p className="text-white" style={{ fontSize: "0.8125rem", fontWeight: 600 }}>
                {firstName}
              </p>
              <p className="text-slate-400" style={{ fontSize: "0.7rem" }}>
                Medical Student
              </p>
            </div>
          </div>
        </div>

        {/* Session Topic */}
        <div className="px-5 py-4 border-b border-white/10">
          <p className="text-slate-400 mb-2" style={{ fontSize: "0.65rem", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase" }}>
            Current Topic
          </p>
          <div className="flex items-start gap-2">
            <Stethoscope size={14} className="text-[#14B8A6] mt-0.5 flex-shrink-0" />
            <span className="text-white" style={{ fontSize: "0.875rem", fontWeight: 500, lineHeight: 1.4 }}>
              {SAMPLE_TOPIC}
            </span>
          </div>
        </div>

        {/* Session Topics */}
        <div className="px-5 py-4 flex-1 overflow-y-auto">
          <p className="text-slate-400 mb-3" style={{ fontSize: "0.65rem", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase" }}>
            Topics Covered
          </p>
          <div className="space-y-1">
            {[
              { label: "Introduction to DR", active: false },
              { label: "Pathophysiology", active: true },
              { label: "VEGF & Angiogenesis", active: false },
              { label: "Clinical Staging", active: false },
              { label: "Macular Edema", active: false },
            ].map((topic, idx) => (
              <div
                key={idx}
                className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg cursor-pointer transition-all ${
                  topic.active
                    ? "bg-[#14B8A6]/20 text-[#14B8A6]"
                    : "text-slate-500 hover:text-slate-300 hover:bg-white/5"
                }`}
              >
                <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${topic.active ? "bg-[#14B8A6]" : "bg-slate-600"}`} />
                <span style={{ fontSize: "0.8rem" }}>{topic.label}</span>
                {topic.active && <ChevronRight size={12} className="ml-auto" />}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="px-5 py-4 border-t border-white/10 space-y-2">
          <button
            onClick={() => endSession("/flashcards")}
            disabled={isEndingSession}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-[#14B8A6]/15 text-[#14B8A6] hover:bg-[#14B8A6]/25 transition-all disabled:opacity-50"
          >
            <Layers size={14} />
            <span style={{ fontSize: "0.8125rem", fontWeight: 500 }}>Flashcard Review</span>
            <ArrowRight size={12} className="ml-auto" />
          </button>
          <button
            onClick={() => endSession("/summary")}
            disabled={isEndingSession}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-all disabled:opacity-50"
          >
            <RotateCcw size={14} />
            <span style={{ fontSize: "0.8125rem" }}>{isEndingSession ? "Ending…" : "End Session"}</span>
          </button>
        </div>
      </motion.div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat Header */}
        <div className="flex-shrink-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-[#0D1B2A]" style={{ fontSize: "1rem", fontWeight: 600 }}>
              {SAMPLE_TOPIC}
            </h2>
            <p className="text-slate-500" style={{ fontSize: "0.8rem" }}>
              AI Tutor Session • {messages.length} exchanges
            </p>
          </div>
          <div className="flex items-center gap-2 bg-[#14B8A6]/10 border border-[#14B8A6]/20 rounded-full px-3 py-1">
            <div className="w-2 h-2 rounded-full bg-[#14B8A6] animate-pulse" />
            <span className="text-[#0D9488]" style={{ fontSize: "0.75rem", fontWeight: 500 }}>
              AI Active
            </span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          {/* Session start indicator */}
          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-slate-200" />
            <span className="text-slate-400 bg-[#F8FAFC] px-2" style={{ fontSize: "0.7rem" }}>
              Session started
            </span>
            <div className="flex-1 h-px bg-slate-200" />
          </div>

          {messages.map((msg) =>
            msg.type === "ai" ? (
              <AIMessageBubble key={msg.id} message={msg} />
            ) : (
              <UserMessageBubble key={msg.id} message={msg} />
            )
          )}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex gap-3 items-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#14B8A6]/20 border border-[#14B8A6]/40 flex items-center justify-center">
                <Bot size={15} className="text-[#14B8A6]" />
              </div>
              <div className="bg-white rounded-2xl rounded-tl-sm border border-slate-200 px-4 py-3 flex items-center gap-1.5">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-2 h-2 rounded-full bg-[#14B8A6]"
                    style={{
                      animation: "bounce 1.2s infinite",
                      animationDelay: `${i * 0.2}s`,
                    }}
                  />
                ))}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="flex-shrink-0 bg-white border-t border-slate-200 px-6 py-4">
          <div className="flex gap-3 items-end">
            <div className="flex-1 bg-[#F8FAFC] border border-slate-200 rounded-xl overflow-hidden focus-within:border-[#14B8A6] focus-within:ring-2 focus-within:ring-[#14B8A6]/20 transition-all">
              <textarea
                ref={inputRef}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="Ask about diabetic retinopathy, mechanisms, clinical presentations..."
                rows={1}
                className="w-full px-4 py-3 bg-transparent text-[#0D1B2A] placeholder-slate-400 outline-none resize-none"
                style={{ fontSize: "0.9rem", lineHeight: 1.5, minHeight: "48px", maxHeight: "120px" }}
              />
            </div>
            <motion.button
              onClick={sendMessage}
              disabled={!input.trim() || isTyping}
              className={`flex-shrink-0 w-11 h-11 rounded-xl flex items-center justify-center transition-all ${
                input.trim() && !isTyping
                  ? "bg-gradient-to-br from-[#14B8A6] to-[#0D9488] text-white shadow-lg shadow-[#14B8A6]/30"
                  : "bg-slate-100 text-slate-400 cursor-not-allowed"
              }`}
              whileHover={input.trim() && !isTyping ? { scale: 1.05, rotate: -5 } : undefined}
              whileTap={input.trim() && !isTyping ? { scale: 0.95 } : undefined}
            >
              <Send size={17} />
            </motion.button>
          </div>
          <p className="text-slate-400 mt-2" style={{ fontSize: "0.7rem" }}>
            Press Enter to send • Shift+Enter for new line
          </p>
        </div>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  );
}
