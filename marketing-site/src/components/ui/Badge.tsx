import React from 'react'

// ─── Types ────────────────────────────────────────────────────────────────────

type BadgeVariant = 'default' | 'accent' | 'success' | 'warning' | 'error' | 'outline'

interface BadgeProps {
  variant?:  BadgeVariant
  dot?:      boolean
  pulse?:    boolean
  children:  React.ReactNode
  className?: string
}

// ─── Style Map ────────────────────────────────────────────────────────────────

const variants: Record<BadgeVariant, string> = {
  default: 'bg-surface-overlay text-text-secondary  border border-white/[0.07]',
  accent:  'bg-accent-500/12  text-accent-300        border border-accent-500/22',
  success: 'bg-emerald-500/10 text-emerald-400       border border-emerald-500/20',
  warning: 'bg-amber-500/10  text-amber-400          border border-amber-500/20',
  error:   'bg-red-500/10    text-red-400            border border-red-500/20',
  outline: 'bg-transparent   text-text-secondary     border border-white/10',
}

// ─── Component ────────────────────────────────────────────────────────────────

export const Badge: React.FC<BadgeProps> = ({
  variant   = 'default',
  dot       = false,
  pulse     = false,
  children,
  className = '',
}) => (
  <span
    className={[
      'inline-flex items-center gap-1.5',
      'px-3 py-1',
      'text-xs font-body font-medium',
      'rounded-full',
      'leading-none tracking-[0.02em]',
      variants[variant],
      className,
    ].join(' ')}
  >
    {dot && (
      <span className="relative flex h-1.5 w-1.5 flex-shrink-0">
        {pulse && (
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-current opacity-50" />
        )}
        <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-current" />
      </span>
    )}
    {children}
  </span>
)
