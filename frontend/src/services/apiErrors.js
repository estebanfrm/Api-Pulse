export function formatApiError(data, status) {
  if (Array.isArray(data?.detail)) {
    // Pydantic prefixes custom validator messages with "Value error, ".
    return data.detail.map((item) => String(item.msg ?? "").replace(/^Value error, /, "")).join(" ");
  }
  if (typeof data?.detail === "string") {
    return data.detail;
  }
  if (typeof data === "string") {
    return data;
  }
  return `Request failed with status ${status}.`;
}
