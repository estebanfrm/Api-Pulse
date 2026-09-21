import assert from "node:assert/strict";
import test from "node:test";

import { SERVICE_STATUS, useApiDashboard } from "../src/composables/useApiDashboard.js";

function createServices(overrides = {}) {
  return {
    createCheck: async () => ({ check: { success: true, status_code: 200 } }),
    fetchChecks: async () => [],
    healthCheck: async () => ({ status: "ok" }),
    ...overrides
  };
}

test("initialization exposes health and history failures without rejecting", async () => {
  const dashboard = useApiDashboard(
    createServices({
      fetchChecks: async () => {
        throw new Error("History is unavailable.");
      },
      healthCheck: async () => {
        throw new Error("Backend is unavailable.");
      }
    })
  );

  await assert.doesNotReject(dashboard.initialize());

  assert.equal(dashboard.serviceStatus.value, SERVICE_STATUS.OFFLINE);
  assert.equal(dashboard.serviceStatusLabel.value, "Offline");
  assert.equal(dashboard.historyError.value, "History is unavailable.");
  assert.equal(dashboard.historyLoading.value, false);
});

test("a saved result remains visible when refreshing history fails", async () => {
  const savedResult = {
    check: { id: 7, success: true, status_code: 500 },
    response: { error: "controlled failure" }
  };
  const dashboard = useApiDashboard(
    createServices({
      createCheck: async () => savedResult,
      fetchChecks: async () => {
        throw new Error("History refresh failed.");
      }
    })
  );

  const returnedResult = await dashboard.runCheck({ method: "GET" });

  assert.equal(returnedResult, savedResult);
  assert.deepEqual(dashboard.currentResult.value, savedResult);
  assert.equal(dashboard.requestError.value, "");
  assert.equal(dashboard.historyError.value, "History refresh failed.");
  assert.equal(dashboard.serviceStatus.value, SERVICE_STATUS.ONLINE);
});

test("retry recovers health and history while preserving stale entries during a failure", async () => {
  const previousHistory = [{ id: 1, success: true, status_code: 200 }];
  const recoveredHistory = [{ id: 2, success: true, status_code: 204 }];
  let backendAvailable = false;
  const dashboard = useApiDashboard(
    createServices({
      fetchChecks: async () => {
        if (!backendAvailable) {
          throw new Error("History is temporarily unavailable.");
        }
        return recoveredHistory;
      },
      healthCheck: async () => {
        if (!backendAvailable) {
          throw new Error("Backend is temporarily unavailable.");
        }
        return { status: "ok" };
      }
    })
  );

  dashboard.history.value = previousHistory;
  await dashboard.initialize();

  assert.equal(dashboard.serviceStatus.value, SERVICE_STATUS.OFFLINE);
  assert.deepEqual(dashboard.history.value, previousHistory);
  assert.equal(dashboard.historyError.value, "History is temporarily unavailable.");

  backendAvailable = true;
  await dashboard.retryConnection();

  assert.equal(dashboard.serviceStatus.value, SERVICE_STATUS.ONLINE);
  assert.deepEqual(dashboard.history.value, recoveredHistory);
  assert.equal(dashboard.historyError.value, "");
});

test("request failures stay separate and refresh backend health", async () => {
  let healthChecks = 0;
  const dashboard = useApiDashboard(
    createServices({
      createCheck: async () => {
        throw new Error("The check could not be saved.");
      },
      healthCheck: async () => {
        healthChecks += 1;
        return { status: "ok" };
      }
    })
  );

  const result = await dashboard.runCheck({ method: "GET" });

  assert.equal(result, null);
  assert.equal(dashboard.requestError.value, "The check could not be saved.");
  assert.equal(dashboard.historyError.value, "");
  assert.equal(dashboard.serviceStatus.value, SERVICE_STATUS.ONLINE);
  assert.equal(healthChecks, 1);
  assert.equal(dashboard.requestLoading.value, false);
});

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

test("a slow failing health probe cannot flip a recovered badge back to Offline", async () => {
  let call = 0;
  const dashboard = useApiDashboard(
    createServices({
      healthCheck: async () => {
        call += 1;
        if (call === 1) {
          await wait(60);
          throw new Error("Backend is unavailable.");
        }
        await wait(5);
        return { status: "ok" };
      }
    })
  );

  const stale = dashboard.retryConnection();
  await wait(5);
  const current = dashboard.retryConnection();
  await Promise.all([stale, current]);

  assert.equal(dashboard.serviceStatus.value, SERVICE_STATUS.ONLINE);
});

test("a slow history refresh cannot overwrite a newer list or its cleared error", async () => {
  const older = [{ id: 1, success: true }];
  const newer = [{ id: 2, success: true }, ...older];
  let call = 0;
  const dashboard = useApiDashboard(
    createServices({
      fetchChecks: async () => {
        call += 1;
        if (call === 1) {
          await wait(60);
          throw new Error("stale failure");
        }
        await wait(5);
        return newer;
      }
    })
  );

  const stale = dashboard.refreshHistory();
  await wait(5);
  const current = dashboard.refreshHistory();
  await Promise.all([stale, current]);

  assert.deepEqual(dashboard.history.value, newer);
  assert.equal(dashboard.historyError.value, "");
});

test("history stays in the loading state while a later refresh is still running", async () => {
  let call = 0;
  const dashboard = useApiDashboard(
    createServices({
      fetchChecks: async () => {
        call += 1;
        await wait(call === 1 ? 5 : 80);
        return [];
      }
    })
  );

  const fast = dashboard.refreshHistory();
  await wait(2);
  const slow = dashboard.refreshHistory();
  await wait(30);

  assert.equal(dashboard.historyLoading.value, true);
  await Promise.all([fast, slow]);
  assert.equal(dashboard.historyLoading.value, false);
});
