/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,html}'],

  theme: {
    // ── Strict 4px spacing scale ──────────────────────────────────────────
    spacing: {
      px:  '1px',
      0:   '0px',
      1:   '4px',
      2:   '8px',
      3:   '12px',
      4:   '16px',
      6:   '24px',
      8:   '32px',
      12:  '48px',
      16:  '64px',
      20:  '80px',
      24:  '96px',
      32:  '128px',
      40:  '160px',
      48:  '192px',
      64:  '256px',
    },

    extend: {
      // ── Color System ──────────────────────────────────────────────────────
      colors: {
        // Dark surface stack — navy-midnight
        surface: {
          base:    '#060914',   // deepest background, page body
          raised:  '#0C1020',   // cards, panels
          overlay: '#111827',   // modals, dropdowns
          border:  '#1A2235',   // dividers
          muted:   '#253047',   // inactive / disabled surfaces
        },

        // Text hierarchy on dark
        text: {
          primary:   '#EEF2FF',  // headlines, key content
          secondary: '#94A3C4',  // body copy, labels
          tertiary:  '#4E5E7A',  // captions, hints, timestamps
          inverse:   '#060914',  // text on light/accent backgrounds
        },

        // Primary accent — phosphor blue (not purple, not teal, not gradient cliché)
        accent: {
          50:   '#EFF6FF',
          100:  '#DBEAFE',
          200:  '#BFDBFE',
          300:  '#93C5FD',
          400:  '#60A5FA',
          500:  '#4F8EF7',   // brand core
          600:  '#3B82F6',
          700:  '#2563EB',
          800:  '#1D4ED8',
          900:  '#1E3A8A',
        },

        // High-contrast white
        white: '#FFFFFF',

        // Neutral slate — for light-mode text and secondary UI
        slate: {
          50:  '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
          950: '#020617',
        },

        // Semantic states
        success: '#10B981',
        warning: '#F59E0B',
        error:   '#EF4444',
      },

      // ── Typography ────────────────────────────────────────────────────────
      fontFamily: {
        // Syne: geometric, editorial, authoritative — a grotesque with character
        display: ['"Syne"', 'system-ui', 'sans-serif'],
        // Instrument Sans: refined, readable, warm grotesque
        body:    ['"Instrument Sans"', 'system-ui', 'sans-serif'],
        // JetBrains Mono: for code snippets and monospace UI
        mono:    ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },

      // Typography scale with tight tracking for large display sizes
      fontSize: {
        'xs':    ['0.75rem',   { lineHeight: '1rem',      letterSpacing: '0.01em' }],
        'sm':    ['0.875rem',  { lineHeight: '1.25rem',   letterSpacing: '0.005em' }],
        'base':  ['1rem',      { lineHeight: '1.625rem',  letterSpacing: '0em' }],
        'lg':    ['1.125rem',  { lineHeight: '1.75rem',   letterSpacing: '-0.005em' }],
        'xl':    ['1.25rem',   { lineHeight: '1.875rem',  letterSpacing: '-0.01em' }],
        '2xl':   ['1.5rem',    { lineHeight: '2rem',      letterSpacing: '-0.015em' }],
        '3xl':   ['1.875rem',  { lineHeight: '2.25rem',   letterSpacing: '-0.02em' }],
        '4xl':   ['2.25rem',   { lineHeight: '2.5rem',    letterSpacing: '-0.025em' }],
        '5xl':   ['3rem',      { lineHeight: '1.1',       letterSpacing: '-0.03em' }],
        '6xl':   ['3.75rem',   { lineHeight: '1.05',      letterSpacing: '-0.035em' }],
        '7xl':   ['4.5rem',    { lineHeight: '1',         letterSpacing: '-0.04em' }],
        '8xl':   ['6rem',      { lineHeight: '0.95',      letterSpacing: '-0.045em' }],
      },

      // ── Shadows ───────────────────────────────────────────────────────────
      boxShadow: {
        // Soft utility shadows (light, Stripe-philosophy: never harsh black)
        'xs':     '0 1px 2px 0 rgba(0,0,0,0.05)',
        'sm':     '0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px 0 rgba(0,0,0,0.06)',
        'md':     '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)',
        'lg':     '0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05)',
        'xl':     '0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)',
        '2xl':    '0 25px 50px -12px rgba(0,0,0,0.25)',

        // Dark surface cards — 1px border glow system
        'card':       '0 0 0 1px rgba(255,255,255,0.05), 0 2px 8px rgba(0,0,0,0.4)',
        'card-hover': '0 0 0 1px rgba(79,142,247,0.28), 0 8px 24px rgba(79,142,247,0.14), 0 2px 8px rgba(0,0,0,0.4)',

        // CTA button shadows
        'btn':        '0 1px 3px 0 rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.1)',
        'btn-hover':  '0 4px 14px rgba(79,142,247,0.35), 0 1px 4px rgba(0,0,0,0.2)',

        // Ambient accent glow (used sparingly)
        'glow-sm':    '0 0 12px rgba(79,142,247,0.22)',
        'glow-md':    '0 0 28px rgba(79,142,247,0.32)',

        // Inset for input focus
        'inner':      'inset 0 1px 0 rgba(255,255,255,0.06)',
        'none':       'none',
      },

      // ── Border Radius ─────────────────────────────────────────────────────
      borderRadius: {
        'sm':  '6px',
        'md':  '10px',
        'lg':  '14px',
        'xl':  '20px',
        '2xl': '28px',
        'full': '9999px',
      },

      // ── Background Images ─────────────────────────────────────────────────
      backgroundImage: {
        // Gradient mesh — ambient atmosphere for hero
        'gradient-mesh': [
          'radial-gradient(at 18% 22%, rgba(79,142,247,0.13) 0%, transparent 52%)',
          'radial-gradient(at 82% 78%, rgba(99,102,241,0.09) 0%, transparent 52%)',
          'radial-gradient(at 50% 50%, rgba(16,185,129,0.04) 0%, transparent 50%)',
        ].join(', '),

        // Dot grid — subtle structural texture
        'dot-grid': 'radial-gradient(circle, rgba(255,255,255,0.07) 1px, transparent 1px)',

        // Card surface shimmer
        'card-gradient': 'linear-gradient(135deg, rgba(255,255,255,0.025) 0%, rgba(255,255,255,0) 100%)',

        // Primary button
        'btn-primary':       'linear-gradient(145deg, #60A5FA 0%, #4F8EF7 40%, #2563EB 100%)',
        'btn-primary-hover': 'linear-gradient(145deg, #93C5FD 0%, #60A5FA 40%, #3B82F6 100%)',
      },

      // ── Animation ─────────────────────────────────────────────────────────
      animation: {
        'fade-up':   'fadeUp 0.55s cubic-bezier(0.16,1,0.3,1) forwards',
        'fade-in':   'fadeIn 0.4s ease-out forwards',
        'shimmer':   'shimmer 2.5s linear infinite',
        'float':     'float 7s ease-in-out infinite',
        'pulse-dot': 'pulseDot 2s ease-in-out infinite',
      },

      keyframes: {
        fadeUp: {
          '0%':   { opacity: 0, transform: 'translateY(20px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%':   { opacity: 0 },
          '100%': { opacity: 1 },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition:  '200% center' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-10px)' },
        },
        pulseDot: {
          '0%, 100%': { opacity: 1, transform: 'scale(1)' },
          '50%':      { opacity: 0.4, transform: 'scale(0.8)' },
        },
      },
    },
  },

  plugins: [],
}
