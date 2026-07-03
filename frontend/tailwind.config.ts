import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // New design system — deep navy + electric indigo + cyan accent
        surface: {
          base:   '#07090f',   // page background
          raised: '#0e1117',   // cards
          overlay:'#141824',   // elevated panels
          border: '#1e2535',   // borders
        },
        brand: {
          DEFAULT: '#6366f1',  // indigo-500
          light:   '#818cf8',  // indigo-400
          dim:     '#3730a3',  // indigo-800
          glow:    'rgba(99,102,241,0.25)',
        },
        accent: {
          DEFAULT: '#22d3ee',  // cyan-400
          dim:     'rgba(34,211,238,0.12)',
        },
        verdict: {
          win:  '#10b981',  // emerald
          lose: '#f43f5e',  // rose
          mid:  '#f59e0b',  // amber
        },
        // Keep "legal" aliases so existing pages don't break
        legal: {
          dark:   '#0e1117',
          darker: '#07090f',
          gold:   '#6366f1',   // remap gold → indigo for consistency
          silver: '#94a3b8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'grid-subtle': "url(\"data:image/svg+xml,%3Csvg width='40' height='40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h40v40H0z' fill='none'/%3E%3Cpath d='M0 40V0M40 0v40' stroke='%231e2535' stroke-width='1'/%3E%3C/svg%3E\")",
      },
      boxShadow: {
        'brand': '0 0 0 1px rgba(99,102,241,0.4), 0 4px 24px rgba(99,102,241,0.15)',
        'card':  '0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.35s ease-out',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(12px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
export default config
