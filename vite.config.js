import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "app/static/react",
    emptyOutDir: true,
    rollupOptions: {
      input: "frontend/src/modern-ui.jsx",
      output: {
        entryFileNames: "modern-ui.js",
        chunkFileNames: "modern-ui-[hash].js",
        assetFileNames: "modern-ui.[ext]",
      },
    },
  },
});
