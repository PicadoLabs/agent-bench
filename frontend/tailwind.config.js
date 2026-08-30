/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#050505',
        'background-alt': '#000000',
        surface: {
          DEFAULT: '#0D0D0D',
          secondary: '#111111',
          hover: '#141414',
          tertiary: '#1A1A1A',
          card: '#101010',
        },
        border: {
          DEFAULT: '#252525',
          light: '#2D2D2D',
          subtle: '#1C1C1C',
        },
        brand: {
          orange: '#FF5A1F',
          'orange-hover': '#FF7540',
          'orange-glow': 'rgba(255, 90, 31, 0.12)',
        },
        primary: {
          text: '#FFFFFF',
          secondary: '#A0A0A0',
          muted: '#6F6F6F',
        },
        status: {
          success: '#68E090',
          warning: '#F5B942',
          error: '#FF4D4D',
          info: '#38BDF8',
        }
      },
      fontFamily: {
        sans: ['Inter', 'Plus Jakarta Sans', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Geist Mono', 'Fira Code', 'Courier New', 'monospace'],
      },
      borderRadius: {
        'card': '12px',
      }
    },
  },
  plugins: [],
}
