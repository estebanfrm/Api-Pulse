import assert from "node:assert/strict";
import test from "node:test";

import { formatApiError } from "../src/services/apiErrors.js";

test("validation messages drop the Pydantic 'Value error, ' prefix", () => {
  const data = { detail: [{ msg: "Value error, Header values must be strings, numbers, booleans, or null." }] };
  assert.equal(formatApiError(data, 422), "Header values must be strings, numbers, booleans, or null.");
});

test("plain validation, string and unknown errors keep their existing wording", () => {
  assert.equal(formatApiError({ detail: [{ msg: "Field required" }] }, 422), "Field required");
  assert.equal(formatApiError({ detail: "Demo request limit reached. Try again later." }, 429), "Demo request limit reached. Try again later.");
  assert.equal(formatApiError(null, 503), "Request failed with status 503.");
});
