/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        // Midnight Executive Semantic Tokens
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
        // Midnight Executive Direct Theme Tokens
        midnight: {
          bg: "#080A0F",
          secondary: "#101216",
          sidebar: "#0C0F14",
          card: "#15191F",
          elevated: "#1B2028",
          hover: "#232A34",
          border: "#292E37",
          borderHover: "#3B424F",
          text: "#F2F3F5",
          secondaryText: "#A0A7B2",
          mutedText: "#727B89",
        },
        // Executive Accent Tokens
        executive: {
          blue: "#547DB8",
          blueLight: "#7898C4",
          blueDark: "#3E5D8A",
          champagne: "#C5A46D",
          champagneLight: "#D7BD8F",
          champagneDark: "#9E7F4C",
          emerald: "#36B58F",
          amber: "#D9A94F",
          crimson: "#D66C73",
        },
        brand: {
          blue: "#547DB8",
          indigo: "#547DB8",
          purple: "#7898C4",
          gold: "#C5A46D",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      boxShadow: {
        executive: "0 4px 20px -2px rgba(0, 0, 0, 0.6)",
        "executive-sm": "0 2px 10px -1px rgba(0, 0, 0, 0.4)",
        "executive-lg": "0 10px 30px -4px rgba(0, 0, 0, 0.7)",
        "glass": "0 8px 32px 0 rgba(0, 0, 0, 0.5)",
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0", transform: "translateY(6px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.2s ease-out",
      },
    },
  },
  plugins: [],
}
