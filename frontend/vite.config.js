import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react()],
    // Vercel + local dev: "/" (default). Render bundled UI at /app/: set VITE_BASE=/app/
    base: env.VITE_BASE || "/",
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
  };
});
