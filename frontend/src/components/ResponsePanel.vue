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

    <div v-if="loading" class="empty-state">Sending request...</div>
    <div v-else-if="error" class="empty-state error-text">{{ error }}</div>
    <div v-else-if="check" class="result-stack">
      <div class="metric-row">
        <div>
          <span>Status</span>
          <strong>{{ check.status_code ?? "N/A" }}</strong>
        </div>
        <div>
          <span>Time</span>
          <strong>{{ check.response_time_ms ?? "N/A" }} ms</strong>
        </div>
      </div>

      <p v-if="check.error_message" class="error-text">{{ check.error_message }}</p>

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
