import assert from "node:assert/strict";
import test from "node:test";

import { formatHistoryDate } from "../src/components/historyDate.js";

test("history dates keep English month names regardless of browser locale", () => {
  assert.match(formatHistoryDate("2026-09-20T12:00:00Z"), /Sep/);
});

test("unparseable history dates degrade to N/A instead of Invalid Date", () => {
  assert.equal(formatHistoryDate(null), "N/A");
  assert.equal(formatHistoryDate("not-a-date"), "N/A");
});
