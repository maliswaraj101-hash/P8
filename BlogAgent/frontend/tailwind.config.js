/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ["Newsreader", "Georgia", "serif"],
        body: ["var(--font-sans)", "sans-serif"],
        label: ["var(--font-sans)", "sans-serif"],
      },
      colors: {
        primary: "#012d1d",
        "primary-container": "#1b4332",
        secondary: "#4c616c",
        "secondary-container": "#cfe6f2",
        background: "#f8f9fa",
        "on-surface": "#191c1d",
        "surface-container-low": "#f3f4f5",
      },
    },
  },
  plugins: [],
};
