import assert from "node:assert/strict";
import test from "node:test";

import { DEMO_SCENARIOS } from "../src/services/demoScenarios.js";

test("public scenario picker exposes only fixed first-party example paths", () => {
  assert.equal(DEMO_SCENARIOS.length, 4);
  assert.deepEqual(
    DEMO_SCENARIOS.map((scenario) => new URL(scenario.url).pathname),
    ["/echo", "/status/404", "/status/500", "/redirect"]
  );
  assert.ok(DEMO_SCENARIOS.every((scenario) => new URL(scenario.url).origin === "https://demo.api-pulse.invalid"));
});
