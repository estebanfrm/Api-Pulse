import assert from "node:assert/strict";
import test from "node:test";

import { validateProductionApiUrl } from "../productionBuild.js";

test("public build accepts a single HTTPS API origin", () => {
  assert.equal(validateProductionApiUrl("https://api-pulse-api.onrender.com"), "https://api-pulse-api.onrender.com");
});

test("public build rejects missing, local, credential-bearing or non-origin URLs", () => {
  for (const value of [
    undefined,
    "http://localhost:8000",
    "https://localhost",
    "https://127.0.0.1",
    "https://[::1]",
    "https://user:secret@example.com",
    "https://example.com/path"
  ]) {
    assert.throws(() => validateProductionApiUrl(value), /Public build requires/);
  }
});
