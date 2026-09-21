import { computed, ref } from "vue";

export const SERVICE_STATUS = Object.freeze({
  CHECKING: "checking",
  ONLINE: "online",
  OFFLINE: "offline"
});

const SERVICE_STATUS_LABELS = {
  [SERVICE_STATUS.CHECKING]: "Checking",
  [SERVICE_STATUS.ONLINE]: "Online",
  [SERVICE_STATUS.OFFLINE]: "Offline"
};

export function useApiDashboard(services) {
  const history = ref([]);
  const currentResult = ref(null);
  const requestLoading = ref(false);
  const requestError = ref("");
  const historyLoading = ref(false);
  const historyError = ref("");
  const serviceStatus = ref(SERVICE_STATUS.CHECKING);

  // Responses can land out of order: a slow probe started first may resolve after a
  // faster one started later. Each concern keeps a token so only the newest call is
  // allowed to write shared state; superseded calls report their own outcome and
  // leave the refs alone.
  let healthToken = 0;
  let historyToken = 0;
  let requestToken = 0;

  const serviceStatusLabel = computed(() => SERVICE_STATUS_LABELS[serviceStatus.value]);

  function markOnline() {
    healthToken += 1;
    serviceStatus.value = SERVICE_STATUS.ONLINE;
  }

  async function refreshHealth() {
    const token = (healthToken += 1);
    serviceStatus.value = SERVICE_STATUS.CHECKING;
    try {
      await services.healthCheck();
      if (token === healthToken) {
        serviceStatus.value = SERVICE_STATUS.ONLINE;
      }
      return true;
    } catch {
      if (token === healthToken) {
        serviceStatus.value = SERVICE_STATUS.OFFLINE;
      }
      return false;
    }
  }

  async function refreshHistory() {
    const token = (historyToken += 1);
    historyLoading.value = true;
    historyError.value = "";
    try {
      const checks = await services.fetchChecks();
      if (!Array.isArray(checks)) {
        throw new Error("The history response was invalid.");
      }
      if (token === historyToken) {
        history.value = checks;
        historyError.value = "";
      }
      return true;
    } catch (error) {
      if (token === historyToken) {
        historyError.value = errorMessage(error, "History could not be loaded.");
      }
      return false;
    } finally {
      if (token === historyToken) {
        historyLoading.value = false;
      }
    }
  }

  async function initialize() {
    await Promise.all([refreshHealth(), refreshHistory()]);
  }

  async function retryConnection() {
    await initialize();
  }

  async function runCheck(payload) {
    const token = (requestToken += 1);
    requestLoading.value = true;
    requestError.value = "";
    try {
      const result = await services.createCheck(payload);
      if (token === requestToken) {
        currentResult.value = result;
        requestError.value = "";
        markOnline();
      }
      await refreshHistory();
      return result;
    } catch (error) {
      if (token === requestToken) {
        requestError.value = errorMessage(error, "The request could not be completed.");
      }
      await refreshHealth();
      return null;
    } finally {
      if (token === requestToken) {
        requestLoading.value = false;
      }
    }
  }

  return {
    currentResult,
    history,
    historyError,
    historyLoading,
    initialize,
    requestError,
    requestLoading,
    refreshHistory,
    retryConnection,
    runCheck,
    serviceStatus,
    serviceStatusLabel
  };
}

function errorMessage(error, fallback) {
  return error instanceof Error && error.message ? error.message : fallback;
}
