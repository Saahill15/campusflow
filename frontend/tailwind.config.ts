import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#111827',
        secondary: '#F8FAFC',
        surface: '#FFFFFF',
        shadow: '#8B95A1',
        accentWarm: '#D97706',
        accentCool: '#2563EB',
        retroShade: '#9D4EDD',
        success: '#16A34A',
        warning: '#F59E0B',
        error: '#DC2626',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        accent: ['Space Grotesk', 'system-ui', 'sans-serif'],
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '32px',
        '2xl': '48px',
        '3xl': '64px',
        '4xl': '80px',
      },
      borderRadius: {
        lg: '16px',
        md: '12px',
        input: '10px',
        sm: '8px',
      },
      boxShadow: {
        surface: '0 10px 30px rgba(17, 24, 39, 0.08)',
        card: '0 16px 48px rgba(17, 24, 39, 0.10)',
        hover: '0 22px 64px rgba(17, 24, 39, 0.12)',
      },
      transitionTimingFunction: {
        smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      transitionDuration: {
        base: '250ms',
      },
      container: {
        center: true,
        padding: '1rem',
        screens: {
          xl: '1280px',
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
