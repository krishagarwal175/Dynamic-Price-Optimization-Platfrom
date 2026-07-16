/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Tactical-OS palette. Black dominates; green attracts; red warns.
        ink: {
          0: "#000000",
          1: "#080808",
          2: "#101010",
          3: "#161616",
        },
        line: {
          DEFAULT: "#262626",
          strong: "#2e2e2e",
        },
        accent: {
          DEFAULT: "#c8ff00", // electric neon green — CTAs, active, positive
          fg: "#000000",
          muted: "rgba(200,255,0,0.12)",
          soft: "rgba(200,255,0,0.40)",
        },
        signal: {
          DEFAULT: "#ff3b30", // executive signal red — warnings, negative
          fg: "#ffffff",
          muted: "rgba(255,59,48,0.12)",
        },
      },
      fontFamily: {
        // Condensed display for headlines + big metrics; mono for the technical layer.
        display: ["Anton", "ui-sans-serif", "Impact", "system-ui", "sans-serif"],
        sans: [
          "Inter Variable",
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "monospace",
        ],
      },
      letterSpacing: {
        tightest: "-0.04em",
      },
      boxShadow: {
        // Brutalist: hairline crisp edge, not a soft drop shadow.
        card: "0 0 0 1px rgba(255,255,255,0.02)",
        glow: "0 0 0 1px #c8ff00, 0 0 28px rgba(200,255,0,0.25)",
      },
    },
  },
  plugins: [],
};
