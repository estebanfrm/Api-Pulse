import http from "node:http";
import process from "node:process";
import { URL } from "node:url";

const host = "127.0.0.1";
const port = Number(process.env.MOCK_API_PORT || 8123);
let failNextHistory = false;
let nextId = 3;
let history = [
  {
    id: 2,
    url: "https://example.test/server-error",
    method: "GET",
    status_code: 500,
    response_time_ms: 48,
    created_at: "2026-09-15T18:20:00Z",
    response_summary: "Controlled server error",
    success: true,
    error_message: null
  },
  {
    id: 1,
    url: "http://localhost/private",
    method: "GET",
    status_code: null,
    response_time_ms: null,
    created_at: "2026-09-15T18:19:00Z",
    response_summary: "",
    success: false,
    error_message: "Blocked target. Localhost URLs are not allowed."
  }
];

const server = http.createServer(async (request, response) => {
  setCorsHeaders(response);
  if (request.method === "OPTIONS") {
    response.writeHead(204);
    response.end();
    return;
  }

  const url = new URL(request.url, `http://${host}:${port}`);
  if (request.method === "GET" && url.pathname === "/health") {
    sendJson(response, 200, { status: "ok" });
    return;
  }

  if (request.method === "GET" && url.pathname === "/api/checks") {
    if (failNextHistory) {
      failNextHistory = false;
      sendJson(response, 503, { detail: "Controlled history refresh failure." });
      return;
    }
    sendJson(response, 200, history);
    return;
  }

  if (request.method === "POST" && url.pathname === "/api/checks") {
    const payload = await readJson(request);
    const check = {
      id: nextId,
      url: payload.url,
      method: payload.method,
      status_code: 500,
      response_time_ms: 37,
      created_at: new Date().toISOString(),
      response_summary: "Controlled HTTP 500 response",
      success: true,
      error_message: null
    };
    nextId += 1;
    history = [check, ...history];
    failNextHistory = true;
    sendJson(response, 200, {
      check,
      response: { message: "Controlled HTTP 500 response" },
      response_headers: { "content-type": "application/json" }
    });
    return;
  }

  sendJson(response, 404, { detail: "Not found." });
});

server.listen(port, host, () => {
  process.stdout.write(`API Pulse mock server listening on http://${host}:${port}\n`);
});

function setCorsHeaders(response) {
  response.setHeader("Access-Control-Allow-Origin", "*");
  response.setHeader("Access-Control-Allow-Headers", "Content-Type");
  response.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
}

function sendJson(response, statusCode, payload) {
  response.writeHead(statusCode, { "Content-Type": "application/json" });
  response.end(JSON.stringify(payload));
}

async function readJson(request) {
  let body = "";
  for await (const chunk of request) {
    body += chunk;
  }
  return JSON.parse(body);
}
