import { formatApiError } from "./apiErrors.js";

const API_BASE_URL = resolveApiBaseUrl();

export async function healthCheck() {
  return request("/health");
}

export async function fetchChecks() {
  return request("/api/checks?limit=50");
}

export async function createCheck(payload) {
  return request("/api/checks", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const data = await parseBody(response);
  if (!response.ok) {
    throw new Error(formatApiError(data, response.status));
  }
  return data;
}

async function parseBody(response) {
  const text = await response.text();
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function resolveApiBaseUrl() {
  const configuredUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
  try {
    const parsed = new URL(configuredUrl);
    const browserHost = window.location.hostname;
    const configuredHost = parsed.hostname;
    const shouldUseCurrentHost =
      ["localhost", "127.0.0.1"].includes(configuredHost) &&
      browserHost &&
      !["localhost", "127.0.0.1"].includes(browserHost);

    if (shouldUseCurrentHost) {
      parsed.hostname = browserHost;
    }

    return parsed.toString().replace(/\/$/, "");
  } catch {
    return configuredUrl.replace(/\/$/, "");
  }
}
