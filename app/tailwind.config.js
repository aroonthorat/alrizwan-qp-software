/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ["'Times New Roman'", "Georgia", "serif"],
        nastaleeq: ["'Jameel Noori Nastaleeq'", "'Noto Nastaliq Urdu'", "serif"],
        devanagari: ["'Noto Sans Devanagari'", "sans-serif"],
      },
    },
  },
  plugins: [],
}
