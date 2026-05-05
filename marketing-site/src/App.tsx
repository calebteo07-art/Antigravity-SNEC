import React from 'react'
import { Hero } from './components/sections/Hero'
import { FeatureGrid } from './components/sections/FeatureGrid'

// ─── Navbar ───────────────────────────────────────────────────────────────────

const Navbar: React.FC = () => (
  <header className="fixed top-0 inset-x-0 z-50">
    {/* Backdrop — frosted glass over whatever's scrolling beneath */}
    <div
      className="absolute inset-0 border-b border-white/[0.05]"
      style={{
        background: 'rgba(6,9,20,0.75)',
        backdropFilter: 'blur(16px) saturate(180%)',
        WebkitBackdropFilter: 'blur(16px) saturate(180%)',
      }}
    />

    <nav className="relative max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
      {/* Logo */}
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-accent-500 flex items-center justify-center">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="white" aria-hidden>
            <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />
          </svg>
        </div>
        <span className="font-display font-bold text-base text-text-primary tracking-tight">
          Voltpay
        </span>
      </div>

      {/* Nav links */}
      <div className="hidden md:flex items-center gap-8">
        {['Products', 'Pricing', 'Docs', 'Blog', 'Company'].map((link) => (
          <a
            key={link}
            href="#"
            className="font-body text-sm text-text-secondary hover:text-text-primary transition-colors duration-150"
          >
            {link}
          </a>
        ))}
      </div>

      {/* Auth actions */}
      <div className="flex items-center gap-3">
        <a
          href="#"
          className="font-body text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
        >
          Sign in
        </a>
        <a
          href="#"
          className="inline-flex items-center h-8 px-4 rounded-lg text-sm font-body font-medium text-white shadow-sm transition-all duration-150 hover:opacity-90"
          style={{ backgroundImage: 'linear-gradient(145deg, #60A5FA, #4F8EF7, #2563EB)' }}
        >
          Get started
        </a>
      </div>
    </nav>
  </header>
)

// ─── Footer ───────────────────────────────────────────────────────────────────

const Footer: React.FC = () => (
  <footer className="bg-surface-base border-t border-white/[0.05] px-6 py-12">
    <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-2">
        <div className="w-5 h-5 rounded bg-accent-500/80 flex items-center justify-center">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="white">
            <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />
          </svg>
        </div>
        <span className="font-body text-sm text-text-tertiary">
          © 2025 Voltpay, Inc.
        </span>
      </div>
      <div className="flex items-center gap-6">
        {['Privacy', 'Terms', 'Security', 'Cookies'].map((l) => (
          <a key={l} href="#" className="font-body text-xs text-text-tertiary hover:text-text-secondary transition-colors">
            {l}
          </a>
        ))}
      </div>
    </div>
  </footer>
)

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  return (
    <div className="min-h-screen bg-surface-base">
      <Navbar />
      <main className="pt-16">
        <Hero />
        <FeatureGrid />
      </main>
      <Footer />
    </div>
  )
}
