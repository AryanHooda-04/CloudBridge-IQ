/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./frontend/src/**/*.{js,jsx}", "./app/static/index.html"],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        muted: "#64748b",
        line: "#e2e8f0",
      },
      boxShadow: {
        enterprise: "0 18px 46px rgba(15, 23, 42, 0.08)",
        soft: "0 10px 28px rgba(15, 23, 42, 0.06)",
      },
    },
  },
  plugins: [],
};
