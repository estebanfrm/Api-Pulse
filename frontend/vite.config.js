import process from "node:process";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { validateProductionApiUrl } from "./productionBuild.js";

if (process.env.RENDER === "true" && process.env.VITE_PUBLIC_DEMO !== "true") {
  throw new Error("Render build requires VITE_PUBLIC_DEMO=true.");
}

if (process.env.RENDER === "true" || process.env.VITE_PUBLIC_DEMO === "true") {
  validateProductionApiUrl(process.env.VITE_API_BASE_URL);
}

export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0",
    port: 5173
  }
});
