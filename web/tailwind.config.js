/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: '#0a0c10',
        card: '#161922',
        glass: 'rgba(22, 25, 34, 0.72)',
        'glass-border': 'rgba(255, 255, 255, 0.08)',
        'comma-green': '#00E676',
        'comma-mint': '#80D8A6',
        'tesla-red': '#E82127',
        'sky-blue': '#00B0FF',
        'amber-warm': '#FFB300',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.45)',
        'glass-hi': '0 12px 40px 0 rgba(0, 0, 0, 0.6)',
        'glow-green': '0 0 20px rgba(0, 230, 118, 0.35)',
        'glow-blue': '0 0 20px rgba(0, 176, 255, 0.35)',
      }
    },
  },
  plugins: [],
}
