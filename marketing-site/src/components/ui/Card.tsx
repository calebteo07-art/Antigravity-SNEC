import React from 'react'
import { motion, HTMLMotionProps } from 'framer-motion'

// ─── Types ────────────────────────────────────────────────────────────────────

interface CardProps extends HTMLMotionProps<'div'> {
  hoverable?: boolean
  gradient?:  boolean
  padding?:   'none' | 'sm' | 'md' | 'lg'
}

const paddingMap = {
  none: '',
  sm:   'p-4',
  md:   'p-6',
  lg:   'p-8',
}

// ─── Component ────────────────────────────────────────────────────────────────

export const Card = React.forwardRef<HTMLDivElement, CardProps>(({
  hoverable = true,
  gradient  = true,
  padding   = 'md',
  className = '',
  children,
  ...props
}, ref) => (
  <motion.div
    ref={ref}
    whileHover={hoverable ? { y: -3 } : undefined}
    transition={{ type: 'spring', stiffness: 400, damping: 26, mass: 0.9 }}
    className={[
      'relative rounded-xl overflow-hidden',
      'bg-surface-raised',
      gradient ? 'bg-card-gradient' : '',
      'shadow-card',
      hoverable ? 'hover:shadow-card-hover cursor-pointer group' : '',
      'border border-white/[0.05]',
      hoverable ? 'transition-[border-color,box-shadow] duration-250 hover:border-accent-500/22' : '',
      paddingMap[padding],
      className,
    ].join(' ')}
    {...props}
  >
    {children}
  </motion.div>
))

Card.displayName = 'Card'

// ─── Sub-components ───────────────────────────────────────────────────────────

export const CardHeader: React.FC<{ className?: string; children: React.ReactNode }> = ({
  className = '', children,
}) => (
  <div className={`mb-4 ${className}`}>{children}</div>
)

export const CardBody: React.FC<{ className?: string; children: React.ReactNode }> = ({
  className = '', children,
}) => (
  <div className={`text-text-secondary font-body text-sm leading-relaxed ${className}`}>
    {children}
  </div>
)

export const CardFooter: React.FC<{ className?: string; children: React.ReactNode }> = ({
  className = '', children,
}) => (
  <div className={`mt-6 pt-4 border-t border-white/[0.06] ${className}`}>{children}</div>
)
