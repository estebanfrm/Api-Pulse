<template>
  <section class="panel history-panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">History</p>
        <h2>Recent checks</h2>
      </div>
      <span class="count">{{ history.length }}</span>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>State</th>
            <th>Method</th>
            <th>URL</th>
            <th>Status</th>
            <th>Time</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in history" :key="item.id">
            <td>
              <span class="tiny-state" :class="{ success: item.success, failed: !item.success }"></span>
            </td>
            <td><span class="method-tag">{{ item.method }}</span></td>
            <td class="url-cell" :title="item.error_message || item.url">{{ item.url }}</td>
            <td>{{ item.status_code ?? "N/A" }}</td>
            <td>{{ item.response_time_ms ?? "N/A" }} ms</td>
            <td>{{ formatDate(item.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
defineProps({
  history: {
    type: Array,
    default: () => []
  }
});

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}
</script>
