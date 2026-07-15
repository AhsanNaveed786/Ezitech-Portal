/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        base: {
          950: '#050912',
          900: '#0A1120',
          800: '#0E1729',
          700: '#121C33',
          600: '#182541',
          500: '#1E2E50',
        },
        line: {
          DEFAULT: 'rgba(120,160,255,0.12)',
          soft: 'rgba(120,160,255,0.07)',
          strong: 'rgba(120,160,255,0.22)',
        },
        ink: {
          DEFAULT: '#EAF1FF',
          muted: '#8CA0C7',
          faint: '#5C6E92',
        },
        brand: {
          50: '#EAF1FF',
          100: '#CFE0FF',
          200: '#9FC0FF',
          300: '#6FA1FF',
          400: '#4F8EFF',
          500: '#2F6FED',
          600: '#2158C7',
          700: '#1A459C',
          800: '#153672',
          900: '#0F274F',
        },
        cyan: {
          DEFAULT: '#22D3EE',
          soft: '#67E8F9',
        },
        signal: {
          up: '#34D399',
          warn: '#FBBF24',
          down: '#F87171',
          idle: '#7C8BAE',
        },
      },
      fontFamily: {
        display: ['"Sora"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(79,142,255,0.15), 0 8px 32px -8px rgba(47,111,237,0.35)',
        'glow-lg': '0 0 0 1px rgba(79,142,255,0.18), 0 24px 64px -12px rgba(47,111,237,0.45)',
        card: '0 1px 0 rgba(255,255,255,0.03) inset, 0 20px 40px -24px rgba(0,0,0,0.6)',
      },
      backgroundImage: {
        mesh: 'radial-gradient(60% 50% at 15% 0%, rgba(47,111,237,0.20) 0%, rgba(5,9,18,0) 60%), radial-gradient(50% 40% at 85% 10%, rgba(34,211,238,0.14) 0%, rgba(5,9,18,0) 60%)',
        'grid-fade': 'linear-gradient(180deg, rgba(5,9,18,0) 0%, rgba(5,9,18,1) 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3.5s cubic-bezier(0.4,0,0.6,1) infinite',
        rise: 'rise 0.6s cubic-bezier(0.16,1,0.3,1) both',
      },
      keyframes: {
        rise: {
          '0%': { opacity: 0, transform: 'translateY(10px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
