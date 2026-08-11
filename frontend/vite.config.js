import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/app/",
  server: {
    port: 5173,
    proxy: {
      "/health": "http://127.0.0.1:8000",
      "/ask": "http://127.0.0.1:8000",
      "/examples": "http://127.0.0.1:8000",
      "/benchmarks": "http://127.0.0.1:8000",
      "/schema": "http://127.0.0.1:8000",
    },
  },
});
