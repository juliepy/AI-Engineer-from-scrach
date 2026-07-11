import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#2f6bff",
          50: "#eff4ff",
          100: "#dce7ff",
          500: "#2f6bff",
          600: "#1a55ef",
          700: "#1244d8",
        },
      },
    },
  },
  plugins: [],
};

export default config;
