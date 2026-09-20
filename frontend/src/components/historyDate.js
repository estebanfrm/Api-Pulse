const historyDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit"
});

export function formatHistoryDate(value) {
  return historyDateFormatter.format(new Date(value));
}
