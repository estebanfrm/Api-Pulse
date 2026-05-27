<template>
  <section class="panel response-panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">Response</p>
        <h2>Result</h2>
      </div>
      <span v-if="check" class="status-badge" :class="{ success: check.success, failed: !check.success }">
        {{ check.success ? "Success" : "Error" }}
      </span>
    </div>

    <div v-if="loading" class="empty-state loading-state">
      <span class="spinner" aria-hidden="true"></span>
      <span>Sending request...</span>
    </div>
    <div v-else-if="error" class="empty-state">
      <div class="error-card">
        <span class="error-label">Request error</span>
        <strong>{{ error }}</strong>
      </div>
    </div>
    <div v-else-if="check" class="result-stack">
      <div class="metric-row">
        <div class="metric-card" :class="statusClass">
          <span>Status</span>
          <strong>{{ check.status_code ?? "N/A" }}</strong>
        </div>
        <div class="metric-card">
          <span>Time</span>
          <strong>{{ check.response_time_ms ?? "N/A" }} ms</strong>
        </div>
      </div>

      <div v-if="check.error_message" class="error-card compact">
        <span class="error-label">{{ errorType }}</span>
        <strong>{{ check.error_message }}</strong>
      </div>

      <pre class="response-body">{{ formattedResponse }}</pre>
    </div>
    <div v-else class="empty-state">No result yet.</div>
  </section>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  result: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ""
  }
});

const check = computed(() => props.result?.check ?? null);

const statusClass = computed(() => {
  const status = check.value?.status_code;
  if (!status) {
    return "status-muted";
  }
  if (status >= 200 && status < 300) {
    return "status-2xx";
  }
  if (status >= 300 && status < 400) {
    return "status-3xx";
  }
  if (status >= 400 && status < 500) {
    return "status-4xx";
  }
  return "status-5xx";
});

const errorType = computed(() => {
  const message = check.value?.error_message ?? "";
  if (message.startsWith("Blocked target")) {
    return "Blocked by security rules";
  }
  if (message.includes("timeout") || message.includes("Timeout")) {
    return "Timeout";
  }
  if (message.startsWith("Invalid URL")) {
    return "Invalid URL";
  }
  if (message.startsWith("Connection") || message.startsWith("Network")) {
    return "Network error";
  }
  return "Request error";
});

const formattedResponse = computed(() => {
  const response = props.result?.response;
  if (response === null || response === undefined) {
    return "";
  }
  if (typeof response === "string") {
    return response;
  }
  return JSON.stringify(response, null, 2);
});
</script>
