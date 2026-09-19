export const DEMO_SCENARIOS = Object.freeze([
  { label: "Echo (200 / 201)", url: "https://demo.api-pulse.invalid/echo" },
  { label: "Not found (404)", url: "https://demo.api-pulse.invalid/status/404" },
  { label: "Server error (500)", url: "https://demo.api-pulse.invalid/status/500" },
  { label: "Redirect (302, not followed)", url: "https://demo.api-pulse.invalid/redirect" }
]);
