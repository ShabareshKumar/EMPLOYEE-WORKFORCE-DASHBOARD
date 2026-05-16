/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0B132B',
        accent: {
          pink: '#FF006E',
          orange: '#FB5607'
        }
      }
    },
  },
  plugins: [],
}
