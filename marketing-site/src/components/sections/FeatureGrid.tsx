import React from 'react'
import { motion, Variants } from 'framer-motion'
import { Card } from '../ui/Card'

// ─── Animation ────────────────────────────────────────────────────────────────

const container: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.07, delayChildren: 0.05 } },
}

const item: Variants = {
  hidden:  { opacity: 0, y: 18 },
  visible: {
    opacity: 1, y: 0,
    transition: { type: 'spring', stiffness: 200, damping: 22 },
  },
}

// ─── Icons (inline SVG, no dependency) ───────────────────────────────────────

const icons = {
  bolt: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />
    </svg>
  ),
  shield: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  ),
  globe: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="2" y1="12" x2="22" y2="12" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  ),
  chart: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6"  y1="20" x2="6"  y2="14" />
      <line x1="2"  y1="20" x2="22" y2="20" />
    </svg>
  ),
  api: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="16 18 22 12 16 6" />
      <polyline points="8 6 2 12 8 18" />
    </svg>
  ),
  lock: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  ),
}

// ─── Feature Data ─────────────────────────────────────────────────────────────

interface Feature {
  icon:        React.ReactNode
  title:       string
  description: string
  tag?:        string
  tagColor?:   string
  linkLabel:   string
}

const features: Feature[] = [
  {
    icon:        icons.bolt,
    title:       'Instant Payouts',
    description: 'Move money in milliseconds. Sub-100ms processing latency across 195 countries, with real-time settlement on supported networks.',
    tag:         'New',
    tagColor:    'bg-accent-500/18 text-accent-300',
    linkLabel:   'Explore payouts',
  },
  {
    icon:        icons.shield,
    title:       'Adaptive Fraud Protection',
    description: 'Machine learning trained on billions of transactions. Radar blocks fraud before it happens — without lifting a finger.',
    linkLabel:   'Learn about Radar',
  },
  {
    icon:        icons.globe,
    title:       'Global Reach',
    description: 'Accept 135+ currencies, 50+ payment methods, and local BNPL options. Compliance handled. Localization built in.',
    linkLabel:   'See global coverage',
  },
  {
    icon:        icons.chart,
    title:       'Revenue Analytics',
    description: 'Cohort analysis, MRR tracking, churn forecasting. Every financial metric your team needs, updated in real time.',
    tag:         'Beta',
    tagColor:    'bg-amber-500/15 text-amber-400',
    linkLabel:   'View analytics',
  },
  {
    icon:        icons.api,
    title:       'Developer-First API',
    description: 'A single unified API with client libraries for every major language. Webhooks, idempotency, and exhaustive documentation.',
    linkLabel:   'Read the docs',
  },
  {
    icon:        icons.lock,
    title:       'Enterprise Security',
    description: 'PCI DSS Level 1, SOC 2 Type II, ISO 27001. Your customers\' data is encrypted in transit and at rest. Always.',
    linkLabel:   'Security overview',
  },
]

// ─── Arrow Icon ───────────────────────────────────────────────────────────────

const ArrowRight = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14M12 5l7 7-7 7" />
  </svg>
)

// ─── Feature Card ─────────────────────────────────────────────────────────────

const FeatureCard: React.FC<{ feature: Feature }> = ({ feature }) => (
  <Card padding="none" className="flex flex-col h-full p-6">
    {/* Icon container */}
    <div className="w-10 h-10 rounded-lg border border-accent-500/20 bg-accent-500/10 flex items-center justify-center text-accent-400 mb-5 flex-shrink-0">
      {feature.icon}
    </div>

    {/* Title + optional tag */}
    <div className="flex items-center gap-2 mb-2">
      <h3 className="font-display font-semibold text-base text-text-primary">
        {feature.title}
      </h3>
      {feature.tag && (
        <span className={`px-2 py-0.5 text-[11px] font-body font-semibold rounded-full leading-none ${feature.tagColor}`}>
          {feature.tag}
        </span>
      )}
    </div>

    {/* Description */}
    <p className="font-body text-sm text-text-secondary leading-relaxed flex-1">
      {feature.description}
    </p>

    {/* Learn more link */}
    <div className="mt-5 flex items-center gap-1.5 text-sm text-accent-400 font-body font-medium group/link cursor-pointer">
      <span className="group-hover/link:underline underline-offset-2">{feature.linkLabel}</span>
      <motion.span
        className="flex-shrink-0"
        initial={{ x: 0 }}
        whileHover={{ x: 3 }}
        transition={{ type: 'spring', stiffness: 600, damping: 25 }}
      >
        <ArrowRight />
      </motion.span>
    </div>
  </Card>
)

// ─── Section ──────────────────────────────────────────────────────────────────

export const FeatureGrid: React.FC = () => (
  <section className="bg-surface-base px-4 py-24">
    <div className="max-w-6xl mx-auto">

      {/* ── Section header ──────────────────────────────────────────────── */}
      <div className="text-center mb-16 max-w-2xl mx-auto">
        <p className="font-body text-xs font-semibold text-accent-400 tracking-[0.15em] uppercase mb-4">
          Everything you need
        </p>
        <h2 className="font-display font-bold text-4xl md:text-5xl text-text-primary mb-5 leading-[1.05]">
          Built for scale.{' '}
          <span
            className="bg-clip-text text-transparent"
            style={{ backgroundImage: 'linear-gradient(135deg, #93C5FD, #60A5FA, #818CF8)' }}
          >
            From day one.
          </span>
        </h2>
        <p className="font-body text-base text-text-secondary leading-relaxed">
          Our suite of products works together so you can build exactly the payment experience
          your business needs — without the ops overhead.
        </p>
      </div>

      {/* ── Feature grid ────────────────────────────────────────────────── */}
      <motion.div
        variants={container}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: '-80px' }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {features.map((feature, i) => (
          <motion.div key={i} variants={item} className="flex">
            <FeatureCard feature={feature} />
          </motion.div>
        ))}
      </motion.div>

      {/* ── Bottom CTA strip ────────────────────────────────────────────── */}
      <div className="mt-16 rounded-2xl border border-white/[0.06] bg-surface-raised p-8 flex flex-col sm:flex-row items-center justify-between gap-6">
        <div>
          <p className="font-display font-semibold text-xl text-text-primary mb-1">
            Ready to go to market?
          </p>
          <p className="font-body text-sm text-text-secondary">
            Start processing payments in minutes, not months.
          </p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <motion.a
            href="#"
            whileHover={{ scale: 1.02, y: -1 }}
            whileTap={{ scale: 0.97 }}
            transition={{ type: 'spring', stiffness: 500, damping: 30, mass: 0.8 }}
            className="inline-flex items-center gap-2 h-10 px-5 rounded-lg text-sm font-body font-medium text-white shadow-btn hover:shadow-btn-hover transition-shadow"
            style={{ backgroundImage: 'linear-gradient(145deg, #60A5FA 0%, #4F8EF7 40%, #2563EB 100%)' }}
          >
            Get started free
            <ArrowRight />
          </motion.a>
          <a
            href="#"
            className="inline-flex items-center h-10 px-5 text-sm font-body font-medium text-text-secondary hover:text-text-primary transition-colors"
          >
            View docs
          </a>
        </div>
      </div>
    </div>
  </section>
)
