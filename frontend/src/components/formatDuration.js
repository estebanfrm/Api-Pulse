// The backend stores whole milliseconds, so anything faster than half a millisecond
// is recorded as 0. A completed exchange never takes zero time, so 0 is shown as
// "<1 ms" rather than a value that reads like a broken timer.
export function formatDuration(value) {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0) {
    return "N/A";
  }
  if (value < 1) {
    return "<1 ms";
  }
  return `${Math.round(value)} ms`;
}
