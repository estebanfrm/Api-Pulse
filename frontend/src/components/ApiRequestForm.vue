<template>
  <form class="panel request-form" @submit.prevent="submitRequest">
    <div class="panel-header">
      <div>
        <p class="eyebrow">Request</p>
        <h2>Probe</h2>
      </div>
      <button class="primary-button" type="submit" :disabled="loading" :aria-busy="loading">
        <span v-if="loading" class="button-spinner" aria-hidden="true"></span>
        <span>{{ loading ? "Sending" : "Send" }}</span>
      </button>
    </div>

    <label class="field">
      <span>{{ publicDemo ? "Scenario" : "URL" }}</span>
      <select v-if="publicDemo" v-model="url">
        <option v-for="item in DEMO_SCENARIOS" :key="item.url" :value="item.url">{{ item.label }}</option>
      </select>
      <input v-else v-model.trim="url" type="url" placeholder="https://api.github.com" />
    </label>

    <p v-if="publicDemo" class="demo-notice">
      Public demo: only built-in scenarios run. Shared history keeps metadata for up to 24 hours / 500 checks.
      Do not enter secrets or personal data.
    </p>

    <label class="field">
      <span>Method</span>
      <select v-model="method">
        <option v-for="item in methods" :key="item" :value="item">{{ item }}</option>
      </select>
    </label>

    <label class="field">
      <span>Headers JSON</span>
      <textarea v-model="headersText" spellcheck="false" rows="5"></textarea>
    </label>

    <label class="field">
      <span>Body JSON</span>
      <textarea v-model="bodyText" spellcheck="false" rows="7"></textarea>
    </label>

    <p v-if="localError" class="error-text">{{ localError }}</p>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { DEMO_SCENARIOS } from "../services/demoScenarios.js";

defineProps({
  loading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(["submit"]);
const methods = ["GET", "POST", "PUT", "DELETE"];

const publicDemo = import.meta.env.VITE_PUBLIC_DEMO !== "false";
const url = ref(publicDemo ? DEMO_SCENARIOS[0].url : "https://api.github.com");
const method = ref("GET");
const headersText = ref("{}");
const bodyText = ref("{}");
const localError = ref("");

function submitRequest() {
  localError.value = "";
  const parsedUrl = publicDemo ? DEMO_SCENARIOS.find((item) => item.url === url.value)?.url : parseUrl(url.value);
  if (!parsedUrl) {
    localError.value = "Invalid URL format. Enter a complete http or https URL.";
    return;
  }

  const headers = parseJsonObject(headersText.value, "Headers");
  if (headers.error) {
    localError.value = headers.error;
    return;
  }

  const body = parseJsonObject(bodyText.value, "Body");
  if (body.error) {
    localError.value = body.error;
    return;
  }

  emit("submit", {
    url: parsedUrl,
    method: method.value,
    headers: headers.value,
    body: body.value
  });
}

function parseUrl(rawValue) {
  try {
    const candidate = new URL(rawValue);
    if (!["http:", "https:"].includes(candidate.protocol)) {
      return null;
    }
    return candidate.toString();
  } catch {
    return null;
  }
}

function parseJsonObject(rawValue, label) {
  const trimmed = rawValue.trim();
  if (!trimmed) {
    return { value: {} };
  }
  try {
    const parsed = JSON.parse(trimmed);
    if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
      return { error: `${label} must be a JSON object.` };
    }
    return { value: parsed };
  } catch {
    return { error: `${label} contains invalid JSON.` };
  }
}
</script>
