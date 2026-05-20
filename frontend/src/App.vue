<template>
  <main class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">HTTP monitor</p>
        <h1>API Pulse</h1>
      </div>
      <div class="service-pill" :class="{ online: apiOnline }">
        <span class="dot"></span>
        <span>{{ apiOnline ? "Online" : "Checking" }}</span>
      </div>
    </header>

    <section class="workspace-grid">
      <ApiRequestForm :loading="loading" @submit="runCheck" />
      <ResponsePanel :result="currentResult" :loading="loading" :error="error" />
    </section>

    <section class="insights-grid">
      <ResponseTimeChart :history="history" />
      <HistoryTable :history="history" />
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from "vue";

import ApiRequestForm from "./components/ApiRequestForm.vue";
import HistoryTable from "./components/HistoryTable.vue";
import ResponsePanel from "./components/ResponsePanel.vue";
import ResponseTimeChart from "./components/ResponseTimeChart.vue";
import { createCheck, fetchChecks, healthCheck } from "./services/api";

const history = ref([]);
const currentResult = ref(null);
const loading = ref(false);
const error = ref("");
const apiOnline = ref(false);

onMounted(async () => {
  await refreshHealth();
  await refreshHistory();
});

async function refreshHealth() {
  try {
    await healthCheck();
    apiOnline.value = true;
  } catch {
    apiOnline.value = false;
  }
}

async function refreshHistory() {
  history.value = await fetchChecks();
}

async function runCheck(payload) {
  loading.value = true;
  error.value = "";
  try {
    currentResult.value = await createCheck(payload);
    await refreshHistory();
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    loading.value = false;
  }
}
</script>
