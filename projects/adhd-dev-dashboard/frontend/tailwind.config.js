/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'celebrate': 'celebrate 2s ease-out',
      },
      keyframes: {
        celebrate: {
          '0%': { transform: 'translate(-50%, -50%) scale(0)', opacity: 0 },
          '50%': { transform: 'translate(-50%, -50%) scale(1.5)', opacity: 1 },
          '100%': { transform: 'translate(-50%, -50%) scale(0)', opacity: 0 },
        },
      },
    },
  },
  plugins: [],
}
