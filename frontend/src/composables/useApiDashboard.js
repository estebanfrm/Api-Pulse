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

  const serviceStatusLabel = computed(() => SERVICE_STATUS_LABELS[serviceStatus.value]);

  async function refreshHealth() {
    serviceStatus.value = SERVICE_STATUS.CHECKING;
    try {
      await services.healthCheck();
      serviceStatus.value = SERVICE_STATUS.ONLINE;
      return true;
    } catch {
      serviceStatus.value = SERVICE_STATUS.OFFLINE;
      return false;
    }
  }

  async function refreshHistory() {
    historyLoading.value = true;
    historyError.value = "";
    try {
      const checks = await services.fetchChecks();
      if (!Array.isArray(checks)) {
        throw new Error("The history response was invalid.");
      }
      history.value = checks;
      return true;
    } catch (error) {
      historyError.value = errorMessage(error, "History could not be loaded.");
      return false;
    } finally {
      historyLoading.value = false;
    }
  }

  async function initialize() {
    await Promise.all([refreshHealth(), refreshHistory()]);
  }

  async function retryConnection() {
    await initialize();
  }

  async function runCheck(payload) {
    requestLoading.value = true;
    requestError.value = "";
    try {
      const result = await services.createCheck(payload);
      currentResult.value = result;
      serviceStatus.value = SERVICE_STATUS.ONLINE;
      await refreshHistory();
      return result;
    } catch (error) {
      requestError.value = errorMessage(error, "The request could not be completed.");
      await refreshHealth();
      return null;
    } finally {
      requestLoading.value = false;
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
