<template>
  <main class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">HTTP monitor</p>
        <h1>API Pulse</h1>
      </div>
      <div class="service-status">
        <div class="service-pill" :class="serviceStatus" role="status" aria-live="polite">
          <span class="dot" aria-hidden="true"></span>
          <span>{{ serviceStatusLabel }}</span>
        </div>
        <button
          v-if="serviceStatus === 'offline'"
          class="secondary-button"
          type="button"
          @click="retryConnection"
        >
          Retry connection
        </button>
      </div>
    </header>

    <section class="workspace-grid">
      <ApiRequestForm :loading="requestLoading" @submit="runCheck" />
      <ResponsePanel :result="currentResult" :loading="requestLoading" :error="requestError" />
    </section>

    <section class="insights-grid">
      <ResponseTimeChart :history="history" />
      <HistoryTable
        :history="history"
        :public-demo="publicDemo"
        :loading="historyLoading"
        :error="historyError"
        @retry="refreshHistory"
      />
    </section>
  </main>
</template>

<script setup>
import { onMounted } from "vue";

import ApiRequestForm from "./components/ApiRequestForm.vue";
import HistoryTable from "./components/HistoryTable.vue";
import ResponsePanel from "./components/ResponsePanel.vue";
import ResponseTimeChart from "./components/ResponseTimeChart.vue";
import { useApiDashboard } from "./composables/useApiDashboard";
import { createCheck, fetchChecks, healthCheck } from "./services/api";

const publicDemo = import.meta.env.VITE_PUBLIC_DEMO !== "false";

const {
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
} = useApiDashboard({ createCheck, fetchChecks, healthCheck });

onMounted(initialize);
</script>
