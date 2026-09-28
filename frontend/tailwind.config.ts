import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: {
        "2xl": "1440px",
      },
    },
    extend: {
      colors: {
        // Strict Cotarco Corporate Palette
        brand: {
          DEFAULT: "#FF3C1D",
          hover: "#E02E11",
          subtle: "#FFF1EF",
          foreground: "#FFFFFF",
        },
        ink: {
          DEFAULT: "#000000",
          muted: "#4A4646",
        },
        slateSecondary: {
          DEFAULT: "#6B6363",
          light: "#9CA3AF",
        },
        canvas: "#F8F9FA",
        surface: "#FFFFFF",

        // Shadcn UI Semantic Mapping
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Functional / Semantic
        success: {
          DEFAULT: "#16A34A",
          subtle: "#F0FDF4",
          border: "rgba(22, 163, 74, 0.2)",
        },
        warning: {
          DEFAULT: "#F59E0B",
          subtle: "#FFFBEB",
          border: "rgba(245, 158, 11, 0.2)",
        },
        error: {
          DEFAULT: "#DC2626",
          subtle: "#FEF2F2",
          border: "rgba(220, 38, 38, 0.2)",
        },
        info: {
          DEFAULT: "#2563EB",
          subtle: "#EFF6FF",
          border: "rgba(37, 99, 235, 0.2)",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
