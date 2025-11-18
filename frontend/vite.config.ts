import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  // --- CORRIGIDO ---
  server: {
    host: '0.0.0.0', // Standard para Docker
    port: 5173,      // TEM de ser 5173 para corresponder ao Nginx
    watch: {
      usePolling: true // Ajuda no hot-reload dentro do Docker
    }
  },
  // -----------------
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));