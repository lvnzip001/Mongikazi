module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        mk: {
          primary: "#0F766E",
          primaryDark: "#0B4F4A",
          secondary: "#F4EFE7",
          accent: "#D9A441",
          bg: "#FAFAF7",
          surface: "#FFFFFF",
          text: "#1F2933",
          muted: "#6B7280",
          border: "#E5E7EB",
          success: "#15803D",
          warning: "#B45309",
          danger: "#B91C1C",
        },
      },
      borderRadius: {
        "mk-card": "1.25rem",
        "mk-button": "0.875rem",
      },
      boxShadow: {
        "mk-card": "0 12px 30px rgba(15, 23, 42, 0.08)",
        "mk-soft": "0 8px 20px rgba(15, 23, 42, 0.06)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
