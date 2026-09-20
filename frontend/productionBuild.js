import { isIP } from "node:net";

export function validateProductionApiUrl(value) {
  let parsed;
  try {
    parsed = new URL(value);
  } catch {
    throw new Error("Public build requires VITE_API_BASE_URL as an HTTPS origin.");
  }
  if (
    parsed.protocol !== "https:" ||
    !parsed.hostname ||
    parsed.hostname === "localhost" ||
    parsed.hostname.endsWith(".localhost") ||
    parsed.hostname.endsWith(".local") ||
    parsed.hostname.startsWith("[") ||
    isIP(parsed.hostname) !== 0 ||
    parsed.username ||
    parsed.password ||
    parsed.port ||
    parsed.pathname !== "/" ||
    parsed.search ||
    parsed.hash
  ) {
    throw new Error("Public build requires VITE_API_BASE_URL as an HTTPS origin.");
  }
  return parsed.origin;
}
