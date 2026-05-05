import React from 'react'
import { motion, HTMLMotionProps } from 'framer-motion'

// ─── Types ────────────────────────────────────────────────────────────────────

type Variant = 'primary' | 'secondary' | 'ghost' | 'outline'
type Size    = 'sm' | 'md' | 'lg'

interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'size'> {
  variant?:      Variant
  size?:         Size
  icon?:         React.ReactNode
  iconPosition?: 'left' | 'right'
  loading?:      boolean
  fullWidth?:    boolean
}

// ─── Style Maps ───────────────────────────────────────────────────────────────

const variants: Record<Variant, string> = {
  primary: [
    'bg-btn-primary text-white',
    'shadow-btn',
    'border border-blue-400/20',
    'hover:bg-btn-primary-hover hover:shadow-btn-hover',
  ].join(' '),

  secondary: [
    'bg-surface-raised text-text-primary',
    'shadow-card',
    'border border-white/[0.07]',
    'hover:border-white/[0.12] hover:bg-surface-overlay',
  ].join(' '),

  ghost: [
    'bg-transparent text-text-secondary',
    'hover:bg-surface-raised hover:text-text-primary',
  ].join(' '),

  outline: [
    'bg-transparent text-accent-400',
    'border border-accent-500/35',
    'hover:bg-accent-500/10 hover:border-accent-500/55',
  ].join(' '),
}

const sizes: Record<Size, string> = {
  sm: 'h-8  px-3 text-sm  rounded-md  gap-1.5',
  md: 'h-10 px-4 text-sm  rounded-lg  gap-2',
  lg: 'h-12 px-6 text-base rounded-xl gap-2.5',
}

// ─── Component ────────────────────────────────────────────────────────────────

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
  variant      = 'primary',
  size         = 'md',
  icon,
  iconPosition = 'left',
  loading      = false,
  fullWidth    = false,
  children,
  className    = '',
  ...props
}, ref) => {
  const base = [
    'inline-flex items-center justify-center',
    'font-body font-medium tracking-[-0.01em]',
    'transition-all duration-150 ease-out',
    'cursor-pointer select-none',
    'focus-visible:outline-none',
    'focus-visible:ring-2 focus-visible:ring-accent-500 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-base',
    'disabled:opacity-40 disabled:pointer-events-none',
    fullWidth ? 'w-full' : '',
    variants[variant],
    sizes[size],
    className,
  ].join(' ')

  return (
    <motion.button
      ref={ref}
      whileHover={{ scale: 1.02, y: -1 }}
      whileTap={{ scale: 0.97 }}
      // Spring physics — snappy but never elastic
      transition={{ type: 'spring', stiffness: 500, damping: 30, mass: 0.8 }}
      className={base}
      {...props}
    >
      {loading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : (
        <>
          {icon && iconPosition === 'left'  && <span className="flex-shrink-0 opacity-80">{icon}</span>}
          <span>{children}</span>
          {icon && iconPosition === 'right' && <span className="flex-shrink-0 opacity-80">{icon}</span>}
        </>
      )}
    </motion.button>
  )
})

Button.displayName = 'Button'
