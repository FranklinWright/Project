import path from "node:path";
import { fileURLToPath } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const apiProxyTarget =
  process.env.VITE_API_PROXY_TARGET ?? "http://localhost:3001";

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: ["babel-plugin-react-compiler"],
      },
    }),
    tailwindcss(),
  ],
  root: "frontend",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "frontend"),
    },
  },
  build: {
    outDir: path.resolve(__dirname, "dist"),
  },
  ssr: {
    noExternal: true,
    target: "node",
  },
  server: {
    port: 5173,
    proxy: {
      "/api": apiProxyTarget,
    },
  },
});
