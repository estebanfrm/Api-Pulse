<template>
  <section class="panel chart-panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">Latency</p>
        <h2>Response times</h2>
      </div>
      <strong>{{ averageTime }} ms avg</strong>
    </div>

    <svg class="chart" viewBox="0 0 640 220" role="img" aria-label="Response time chart">
      <line x1="32" y1="188" x2="612" y2="188" class="axis" />
      <polyline v-if="points" :points="points" class="line" />
      <circle
        v-for="point in pointList"
        :key="point.key"
        :cx="point.x"
        :cy="point.y"
        r="4"
        class="marker"
      />
    </svg>
  </section>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  history: {
    type: Array,
    default: () => []
  }
});

const successfulChecks = computed(() =>
  props.history
    .filter((item) => item.success && Number.isFinite(item.response_time_ms))
    .slice(0, 12)
    .reverse()
);

const pointList = computed(() => {
  const data = successfulChecks.value;
  if (!data.length) {
    return [];
  }
  const max = Math.max(...data.map((item) => item.response_time_ms), 1);
  const step = data.length === 1 ? 0 : 580 / (data.length - 1);
  return data.map((item, index) => ({
    key: item.id,
    x: 32 + step * index,
    y: 188 - (item.response_time_ms / max) * 150
  }));
});

const points = computed(() => pointList.value.map((point) => `${point.x},${point.y}`).join(" "));

const averageTime = computed(() => {
  const data = successfulChecks.value;
  if (!data.length) {
    return 0;
  }
  const total = data.reduce((sum, item) => sum + item.response_time_ms, 0);
  return Math.round(total / data.length);
});
</script>
