<template>
  <section class="panel history-panel" :aria-busy="loading">
    <div class="panel-header">
      <div>
        <p class="eyebrow">History</p>
        <h2>Recent checks</h2>
      </div>
      <div class="history-meta">
        <span v-if="loading" class="inline-status" role="status">Refreshing...</span>
        <span class="count">{{ history.length }}</span>
      </div>
    </div>

    <div v-if="error" class="error-card compact history-error" role="alert">
      <div>
        <span class="error-label">History unavailable</span>
        <strong>{{ error }}</strong>
      </div>
      <button class="secondary-button" type="button" :disabled="loading" @click="emit('retry')">
        Retry history
      </button>
    </div>

    <div v-if="loading && !history.length" class="empty-state compact loading-state" role="status">
      <span class="spinner" aria-hidden="true"></span>
      <span>Loading history...</span>
    </div>

    <div v-else-if="!history.length && !error" class="empty-state compact">No checks yet.</div>

    <div v-if="history.length" class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Outcome</th>
            <th>Method</th>
            <th>{{ publicDemo ? "Scenario" : "URL" }}</th>
            <th>Status</th>
            <th>Time</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in history" :key="item.id">
            <td>
              <span class="state-badge" :class="{ received: item.success, failed: !item.success }">
                {{ item.success ? "Received" : "No response" }}
              </span>
            </td>
            <td><span class="method-tag">{{ item.method }}</span></td>
            <td class="url-cell" :title="item.error_message || item.url">{{ item.url }}</td>
            <td><span class="http-status" :class="statusClass(item.status_code)">{{ item.status_code ?? "N/A" }}</span></td>
            <td>{{ formatDuration(item.response_time_ms) }}</td>
            <td>{{ formatHistoryDate(item.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { formatDuration } from "./formatDuration.js";
import { formatHistoryDate } from "./historyDate.js";

defineProps({
  publicDemo: {
    type: Boolean,
    default: false
  },
  history: {
    type: Array,
    default: () => []
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

const emit = defineEmits(["retry"]);

function statusClass(status) {
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
}
</script>
