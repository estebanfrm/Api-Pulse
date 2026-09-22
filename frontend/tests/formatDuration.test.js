import assert from "node:assert/strict";
import test from "node:test";

import { formatDuration } from "../src/components/formatDuration.js";

test("sub-millisecond measurements read as <1 ms instead of 0 ms", () => {
  assert.equal(formatDuration(0), "<1 ms");
  assert.equal(formatDuration(0.4), "<1 ms");
});

test("whole and fractional milliseconds are rounded", () => {
  assert.equal(formatDuration(1), "1 ms");
  assert.equal(formatDuration(272), "272 ms");
  assert.equal(formatDuration(58.6), "59 ms");
});

test("missing or invalid durations degrade to N/A", () => {
  assert.equal(formatDuration(null), "N/A");
  assert.equal(formatDuration(undefined), "N/A");
  assert.equal(formatDuration(Number.NaN), "N/A");
  assert.equal(formatDuration(-5), "N/A");
});
