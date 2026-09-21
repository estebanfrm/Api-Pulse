const historyDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit"
});

export function formatHistoryDate(value) {
  // new Date(null) silently becomes the epoch, so anything that is not a timestamp
  // string or number is rejected before parsing.
  if (typeof value !== "string" && typeof value !== "number") {
    return "N/A";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return "N/A";
  }
  return historyDateFormatter.format(parsed);
}
