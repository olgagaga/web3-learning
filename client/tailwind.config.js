/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Claude orange palette
        'claude': {
          50: '#FFF5F0',
          100: '#FFE8DB',
          200: '#FFD4B8',
          300: '#FFB894',
          400: '#FF9B70',
          500: '#FF7F4D',  // Primary orange
          600: '#E6652A',
          700: '#CC4D14',
          800: '#993A0F',
          900: '#66270A',
        },
        'primary': '#FF7F4D',
        'primary-dark': '#E6652A',
        'primary-light': '#FFD4B8',
      },
    },
  },
  plugins: [],
}
