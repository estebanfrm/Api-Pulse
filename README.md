# API Pulse

API Pulse is a full-stack MVP for testing HTTP APIs, tracking response times, and reviewing request history from a polished dark-mode interface.

## Stack

- Frontend: Vue 3 + Vite
- Backend: FastAPI + httpx
- Database: PostgreSQL
- Infrastructure: Docker and Docker Compose

## Architecture

```text
Vue 3 UI
  -> FastAPI REST API
    -> SSRF validation
    -> httpx outbound request
    -> PostgreSQL history storage
```

## Project Structure

```text
api-pulse/
  docker-compose.yml
  .env.example
  README.md
  backend/
    Dockerfile
    requirements.txt
    app/
      main.py
      config.py
      database.py
      models.py
      schemas.py
      routers/checks.py
      services/api_client.py
      services/security.py
  frontend/
    Dockerfile
    package.json
    index.html
    vite.config.js
    src/
      App.vue
      main.js
      services/api.js
      components/
      styles/main.css
```

## Screenshots

Validated dashboard screenshot:

```text
docs/screenshots/dashboard.png
```

Placeholders for future product screenshots:

```text
docs/screenshots/request-result.png
docs/screenshots/history-chart.png
```

## Run With Docker

```bash
docker compose up --build
```

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8000
```

## Environment

Copy `.env.example` to `.env` if you want to override defaults.

```text
POSTGRES_USER=api_pulse
POSTGRES_PASSWORD=api_pulse_password
POSTGRES_DB=api_pulse
DATABASE_URL=postgresql+psycopg://api_pulse:api_pulse_password@postgres:5432/api_pulse
BACKEND_PORT=8000
FRONTEND_PORT=5173
VITE_API_BASE_URL=http://localhost:8000
```

## API Endpoints

`GET /health`

Returns service health.

`POST /api/checks`

Runs an API request and stores the result.

```json
{
  "url": "https://api.github.com",
  "method": "GET",
  "headers": {},
  "body": {}
}
```

`GET /api/checks?limit=50`

Returns recent request history.

## Security Rules

The backend includes SSRF protections for the MVP:

- Only `http` and `https` URLs are allowed.
- `localhost`, `127.0.0.1`, `0.0.0.0`, `::1`, and `.localhost` hosts are rejected.
- Hostnames are resolved with DNS before making the outbound request.
- Private, loopback, link-local, multicast, reserved, and unspecified IP targets are rejected.

## Validation Notes

- Phase 1 validated Docker Compose config and healthy PostgreSQL/backend containers.
- Phase 2 validated healthcheck, public API request, blocked local/private targets, and persisted history with `success` and `error_message`.
- Phase 3 validates the full stack, frontend request flow, backend errors, history refresh, and response-time chart.
