import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 5000,
    hmr: { overlay: false },
    proxy: {
      "/api/auth": { target: "http://localhost:5001", changeOrigin: true },
      "/api/tickets": { target: "http://localhost:5002", changeOrigin: true },
      "/api/geo": { target: "http://localhost:5003", changeOrigin: true },
      "/api/media": { target: "http://localhost:5004", changeOrigin: true },
      "/api/notifications": { target: "http://localhost:5005", changeOrigin: true },
      "/api/admin": { target: "http://localhost:5006", changeOrigin: true }
    }
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));

