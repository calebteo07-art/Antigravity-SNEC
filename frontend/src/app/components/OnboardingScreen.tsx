import React, { useState } from "react";
import { useNavigate } from "react-router";
import { motion } from "motion/react";
import { HolographicEyeLogo } from "./HolographicEyeLogo";
import { ParticleBackground } from "./ParticleBackground";
import { Eye, Sparkles } from "lucide-react";

async function apiOnboard(fullName: string, email: string): Promise<string> {
  const res = await fetch("/api/onboard", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ full_name: fullName, email }),
  });
  if (!res.ok) throw new Error("Onboarding failed");
  const data = await res.json();
  return data.student_id;
}

const PDPA_TEXT = `PERSONAL DATA PROTECTION ACT (PDPA) CONSENT

1. COLLECTION OF PERSONAL DATA
EyeQ ("the Application") collects personal information including your full name and email address for the purpose of providing personalized medical education services. By registering, you consent to the collection, use, and processing of your personal data as described herein.

2. PURPOSE OF DATA COLLECTION
Your personal data is collected for the following purposes:
(a) Creating and managing your learner account
(b) Personalizing your AI tutoring experience
(c) Tracking learning progress and session history
(d) Generating spaced repetition flashcard schedules
(e) Communicating important service updates

3. DATA RETENTION
Your personal data will be retained for the duration of your active account and for a period of 3 years after account closure, in accordance with applicable medical education record-keeping requirements.

4. DATA SHARING
EyeQ does not sell, trade, or transfer your personal information to third parties without your explicit consent, except where required by law or necessary for the operation of services directly related to the Application.

5. YOUR RIGHTS
You have the right to: access your personal data; request correction of inaccurate data; withdraw consent at any time; request deletion of your data subject to applicable legal requirements.

6. SECURITY MEASURES
We implement industry-standard security measures including encryption, secure server infrastructure, and access controls to protect your personal data from unauthorized access or disclosure.

7. CONTACT
For data-related inquiries, please contact our Data Protection Officer at dpo@eyeq-medical.com.

By checking the box below, you acknowledge that you have read, understood, and agree to this PDPA consent notice and our Terms of Service.`;

export function OnboardingScreen() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [pdpaConsent, setPdpaConsent] = useState(false);
  const [errors, setErrors] = useState<{ fullName?: string; email?: string; pdpa?: string; api?: string }>({});
  const [submitting, setSubmitting] = useState(false);

  const validate = () => {
    const newErrors: typeof errors = {};
    if (!fullName.trim()) newErrors.fullName = "Full name is required";
    if (!email.trim()) newErrors.email = "Email address is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) newErrors.email = "Please enter a valid email";
    if (!pdpaConsent) newErrors.pdpa = "You must agree to the PDPA consent to continue";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate() || submitting) return;
    setSubmitting(true);
    try {
      const student_id = await apiOnboard(fullName.trim(), email.trim());
      sessionStorage.setItem("eyeq_user", JSON.stringify({ fullName, email, student_id }));
      navigate("/chat");
    } catch {
      setErrors((prev) => ({ ...prev, api: "Could not reach server. Is the backend running?" }));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0D1B2A] flex flex-col items-center justify-center px-4 py-12 relative overflow-hidden">
      <ParticleBackground density={40} color="#14B8A6" />

      {/* Enhanced background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-[#14B8A6] opacity-[0.05] blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.05, 0.08, 0.05],
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-[#14B8A6] opacity-[0.06] blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.06, 0.09, 0.06],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        />
      </div>

      <motion.div
        className="w-full max-w-md relative z-10"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        {/* Logo & Branding */}
        <motion.div
          className="flex flex-col items-center mb-10"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.6, type: "spring" }}
        >
          <div className="flex items-center gap-4 mb-3">
            <HolographicEyeLogo size={64} animated={true} />
            <div>
              <motion.h1
                className="text-white tracking-tight"
                style={{ fontSize: "2.25rem", fontWeight: 700, lineHeight: 1 }}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.5 }}
              >
                EyeQ
              </motion.h1>
              <motion.p
                className="text-[#14B8A6]"
                style={{ fontSize: "0.75rem", letterSpacing: "0.15em", fontWeight: 500 }}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.5, duration: 0.5 }}
              >
                MEDICAL EDUCATION
              </motion.p>
            </div>
          </div>
          <motion.p
            className="text-slate-400 text-center mt-2"
            style={{ fontSize: "0.9rem" }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
          >
            AI-powered tutoring for the modern clinician
          </motion.p>
        </motion.div>

        {/* Form Card */}
        <motion.div
          className="bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl overflow-hidden border border-white/20"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          {/* Card header bar with animation */}
          <motion.div
            className="h-1 w-full bg-gradient-to-r from-[#0D9488] via-[#14B8A6] to-[#0D9488]"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            style={{ transformOrigin: "left" }}
          />

          <form onSubmit={handleSubmit} className="p-8">
            <h2 className="text-[#0D1B2A] mb-1" style={{ fontSize: "1.25rem", fontWeight: 600 }}>
              Create your account
            </h2>
            <p className="text-slate-500 mb-6" style={{ fontSize: "0.875rem" }}>
              Begin your personalized learning journey
            </p>

            {/* Full Name */}
            <div className="mb-5">
              <label className="block text-[#0D1B2A] mb-1.5" style={{ fontSize: "0.875rem", fontWeight: 600 }}>
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. Jane Smith"
                className={`w-full px-4 py-3 rounded-lg border bg-slate-50 text-[#0D1B2A] placeholder-slate-400 transition-all outline-none focus:bg-white focus:border-[#14B8A6] focus:ring-2 focus:ring-[#14B8A6]/20 ${
                  errors.fullName ? "border-red-400" : "border-slate-200"
                }`}
                style={{ fontSize: "0.9375rem" }}
              />
              {errors.fullName && (
                <p className="text-red-500 mt-1" style={{ fontSize: "0.8rem" }}>
                  {errors.fullName}
                </p>
              )}
            </div>

            {/* Email */}
            <div className="mb-6">
              <label className="block text-[#0D1B2A] mb-1.5" style={{ fontSize: "0.875rem", fontWeight: 600 }}>
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jane.smith@hospital.org"
                className={`w-full px-4 py-3 rounded-lg border bg-slate-50 text-[#0D1B2A] placeholder-slate-400 transition-all outline-none focus:bg-white focus:border-[#14B8A6] focus:ring-2 focus:ring-[#14B8A6]/20 ${
                  errors.email ? "border-red-400" : "border-slate-200"
                }`}
                style={{ fontSize: "0.9375rem" }}
              />
              {errors.email && (
                <p className="text-red-500 mt-1" style={{ fontSize: "0.8rem" }}>
                  {errors.email}
                </p>
              )}
            </div>

            {/* PDPA Section */}
            <div className="mb-6">
              <label className="block text-[#0D1B2A] mb-2" style={{ fontSize: "0.875rem", fontWeight: 600 }}>
                PDPA Consent
              </label>
              {/* Scrollable legal text */}
              <div
                className="w-full h-36 overflow-y-auto border border-slate-200 rounded-lg bg-slate-50 p-3 mb-3"
                style={{ fontSize: "0.75rem", lineHeight: 1.6, color: "#475569" }}
              >
                <pre className="whitespace-pre-wrap font-sans">{PDPA_TEXT}</pre>
              </div>

              {/* Checkbox */}
              <label className="flex items-start gap-3 cursor-pointer group">
                <div className="relative mt-0.5 flex-shrink-0">
                  <input
                    type="checkbox"
                    checked={pdpaConsent}
                    onChange={(e) => setPdpaConsent(e.target.checked)}
                    className="sr-only"
                  />
                  <div
                    onClick={() => setPdpaConsent(!pdpaConsent)}
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all cursor-pointer ${
                      pdpaConsent
                        ? "bg-[#14B8A6] border-[#14B8A6]"
                        : "bg-white border-slate-300 group-hover:border-[#14B8A6]"
                    }`}
                  >
                    {pdpaConsent && (
                      <svg width="12" height="9" viewBox="0 0 12 9" fill="none">
                        <path d="M1 4L4.5 7.5L11 1" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </div>
                </div>
                <span
                  className="text-slate-600 leading-snug"
                  style={{ fontSize: "0.8125rem" }}
                  onClick={() => setPdpaConsent(!pdpaConsent)}
                >
                  I have read and agree to the Personal Data Protection Act (PDPA) consent notice and{" "}
                  <span className="text-[#14B8A6] hover:underline cursor-pointer">Terms of Service</span>
                </span>
              </label>
              {errors.pdpa && (
                <p className="text-red-500 mt-1" style={{ fontSize: "0.8rem" }}>
                  {errors.pdpa}
                </p>
              )}
            </div>

            {/* API error */}
            {errors.api && (
              <p className="text-red-500 text-center mb-3" style={{ fontSize: "0.8rem" }}>
                {errors.api}
              </p>
            )}

            {/* CTA Button */}
            <motion.button
              type="submit"
              disabled={submitting}
              className="w-full py-4 rounded-xl bg-gradient-to-r from-[#0D1B2A] via-[#0D2B3A] to-[#0D1B2A] text-white transition-all hover:shadow-2xl flex items-center justify-center gap-2 shadow-lg shadow-[#0D1B2A]/40 relative overflow-hidden group disabled:opacity-60 disabled:cursor-not-allowed"
              style={{ fontWeight: 600, fontSize: "1rem", letterSpacing: "0.01em" }}
              whileHover={!submitting ? { scale: 1.02, y: -2 } : undefined}
              whileTap={!submitting ? { scale: 0.98 } : undefined}
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                initial={{ x: "-100%" }}
                whileHover={{ x: "200%" }}
                transition={{ duration: 0.6, ease: "easeInOut" }}
              />
              <Sparkles size={18} className="text-[#14B8A6]" />
              <span className="relative z-10">{submitting ? "Starting…" : "Start Learning"}</span>
              <Eye size={18} className="text-[#14B8A6]" />
            </motion.button>

            <p className="text-center text-slate-400 mt-4" style={{ fontSize: "0.75rem" }}>
              Your data is protected under PDPA guidelines
            </p>
          </form>
        </motion.div>

        <motion.p
          className="text-center text-slate-500 mt-6"
          style={{ fontSize: "0.8rem" }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          © 2026 EyeQ Medical Education. All rights reserved.
        </motion.p>
      </motion.div>
    </div>
  );
}
