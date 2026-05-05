import React from 'react'
import { motion, Variants } from 'framer-motion'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'

// ─── Animation Variants ───────────────────────────────────────────────────────

const fadeUp: Variants = {
  hidden:   { opacity: 0, y: 22 },
  visible:  {
    opacity: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 180, damping: 22 },
  },
}

const staggerContainer: Variants = {
  hidden:  {},
  visible: { transition: { staggerChildren: 0.1, delayChildren: 0.05 } },
}

const mockupReveal: Variants = {
  hidden:  { opacity: 0, y: 52, scale: 0.97 },
  visible: {
    opacity: 1, y: 0, scale: 1,
    transition: { type: 'spring', stiffness: 120, damping: 24, delay: 0.55 },
  },
}

// ─── Decorative Icons ─────────────────────────────────────────────────────────

const ArrowRight = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14M12 5l7 7-7 7" />
  </svg>
)

// ─── Dashboard Mockup ─────────────────────────────────────────────────────────

const DashboardMockup: React.FC = () => (
  <motion.div
    variants={mockupReveal}
    initial="hidden"
    animate="visible"
    className="relative w-full max-w-4xl mx-auto mt-16 px-4"
  >
    {/* Glow behind the card */}
    <div
      className="absolute inset-x-16 top-8 bottom-0 blur-3xl opacity-25"
      style={{ background: 'radial-gradient(ellipse, rgba(79,142,247,0.5) 0%, transparent 70%)' }}
    />

    <div className="relative rounded-2xl overflow-hidden shadow-2xl border border-white/[0.07]">
      {/* Browser chrome */}
      <div className="flex items-center gap-2 px-4 h-11 bg-surface-overlay border-b border-white/[0.05]">
        <span className="w-3 h-3 rounded-full bg-red-500/50" />
        <span className="w-3 h-3 rounded-full bg-amber-400/50" />
        <span className="w-3 h-3 rounded-full bg-emerald-500/50" />
        <div className="flex-1 mx-4 h-6 rounded-md bg-surface-muted/40 flex items-center px-3">
          <span className="text-xs text-text-tertiary font-mono tracking-tight">
            dashboard.yourapp.com
          </span>
        </div>
      </div>

      {/* Dashboard body */}
      <div className="bg-surface-raised p-6">
        {/* Stat row */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { label: 'Revenue',       value: '$84,240', trend: '+18.2%' },
            { label: 'Transactions',  value: '12,084',  trend: '+6.4%'  },
            { label: 'Success Rate',  value: '99.1%',   trend: '+0.3%'  },
          ].map((stat, i) => (
            <div
              key={i}
              className="rounded-lg bg-surface-base border border-white/[0.05] p-4"
            >
              <p className="text-xs text-text-tertiary mb-1 font-body">{stat.label}</p>
              <p className="text-xl font-display font-bold text-text-primary">{stat.value}</p>
              <p className="text-xs text-emerald-400 mt-1 font-body">{stat.trend} this month</p>
            </div>
          ))}
        </div>

        {/* Sparkline chart bars — purely decorative */}
        <div className="h-24 flex items-end gap-1.5">
          {[35, 55, 40, 70, 50, 85, 60, 90, 75, 95, 65, 88, 72, 100, 80, 92].map((h, i) => (
            <motion.div
              key={i}
              initial={{ scaleY: 0, originY: 1 }}
              animate={{ scaleY: 1 }}
              transition={{ delay: 0.7 + i * 0.04, duration: 0.4, ease: 'easeOut' }}
              className="flex-1 rounded-sm origin-bottom"
              style={{
                height: `${h}%`,
                background: i === 14
                  ? 'rgba(79,142,247,0.9)'
                  : i > 10
                  ? 'rgba(79,142,247,0.35)'
                  : 'rgba(255,255,255,0.08)',
              }}
            />
          ))}
        </div>
      </div>
    </div>

    {/* Bottom fade */}
    <div
      className="absolute -bottom-px inset-x-0 h-20 pointer-events-none"
      style={{ background: 'linear-gradient(to top, #060914, transparent)' }}
    />
  </motion.div>
)

// ─── Hero ─────────────────────────────────────────────────────────────────────

export const Hero: React.FC = () => (
  <section className="relative flex flex-col items-center justify-center overflow-hidden bg-surface-base px-4 pt-24 pb-0">

    {/* Dot grid texture */}
    <div
      className="absolute inset-0 pointer-events-none"
      style={{
        backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.065) 1px, transparent 1px)',
        backgroundSize: '28px 28px',
      }}
    />

    {/* Gradient mesh atmosphere */}
    <div
      className="absolute inset-0 pointer-events-none"
      style={{
        background: [
          'radial-gradient(at 18% 22%, rgba(79,142,247,0.14) 0%, transparent 52%)',
          'radial-gradient(at 80% 75%, rgba(99,102,241,0.09) 0%, transparent 50%)',
          'radial-gradient(at 50% 50%, rgba(16,185,129,0.04) 0%, transparent 50%)',
        ].join(', '),
      }}
    />

    {/* Concentric geometric rings — gives depth behind hero text */}
    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-[60%] pointer-events-none">
      {[520, 680, 840].map((size, i) => (
        <div
          key={i}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border"
          style={{
            width: size,
            height: size,
            borderColor: `rgba(79,142,247,${0.04 + i * 0.025})`,
          }}
        />
      ))}
    </div>

    {/* ── Main content ─────────────────────────────────────────────────── */}
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="relative z-10 flex flex-col items-center text-center gap-6 max-w-4xl"
    >
      {/* Eyebrow badge */}
      <motion.div variants={fadeUp}>
        <Badge variant="accent" dot pulse>
          Now in public beta — Get early access
        </Badge>
      </motion.div>

      {/* Headline */}
      <motion.h1
        variants={fadeUp}
        className="font-display font-bold text-5xl sm:text-6xl md:text-7xl text-text-primary leading-[0.95]"
      >
        Payments{' '}
        <br className="hidden sm:block" />
        <span className="relative inline-block">
          <span
            className="bg-clip-text text-transparent"
            style={{
              backgroundImage: 'linear-gradient(135deg, #93C5FD 0%, #60A5FA 40%, #818CF8 100%)',
            }}
          >
            engineered
          </span>
          {/* Subtle line beneath gradient word */}
          <span
            className="absolute -bottom-1 left-0 right-0 h-px"
            style={{
              background: 'linear-gradient(90deg, transparent, rgba(79,142,247,0.55), transparent)',
            }}
          />
        </span>{' '}
        for scale
      </motion.h1>

      {/* Subheadline */}
      <motion.p
        variants={fadeUp}
        className="font-body text-lg md:text-xl text-text-secondary max-w-2xl leading-relaxed"
      >
        Financial infrastructure for the internet. Accept payments, grow revenue, and
        operate globally — with one unified platform trusted by over{' '}
        <span className="text-text-primary font-medium">100,000 businesses</span>.
      </motion.p>

      {/* CTA row */}
      <motion.div
        variants={fadeUp}
        className="flex flex-col sm:flex-row items-center gap-3 mt-2"
      >
        <Button
          variant="primary"
          size="lg"
          icon={<ArrowRight />}
          iconPosition="right"
        >
          Start building
        </Button>
        <Button variant="secondary" size="lg">
          Contact sales
        </Button>
      </motion.div>

      {/* Trust signal */}
      <motion.p
        variants={fadeUp}
        className="font-body text-sm text-text-tertiary"
      >
        No credit card required &nbsp;·&nbsp; Free up to $10k/month &nbsp;·&nbsp; SOC 2 certified
      </motion.p>
    </motion.div>

    {/* Dashboard mockup */}
    <DashboardMockup />
  </section>
)
