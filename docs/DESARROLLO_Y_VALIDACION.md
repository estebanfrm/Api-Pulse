# Desarrollo y validación

Ejecutar desde la raíz del repositorio, salvo indicación. Comandos orientados a PowerShell. La configuración versionada es la fuente para las versiones; estos comandos no afirman que los controles ya hayan pasado.

## Ruta correcta

En el equipo revisado, el trabajo T01–T06 continúa en el worktree actual:

~~~powershell
Set-Location 'C:\Users\giral\.codex\worktrees\7c72\api-pulse'
git status --short --branch
~~~

El checkout fuente histórico `C:\Users\giral\OneDrive\Documentos\Esteban\api-pulse` también existe, pero no contiene automáticamente los cambios de este worktree. La carpeta `nwep` no existe; no recrearla.

## Requisitos del entorno

- Docker Engine activo y Docker Compose para el entorno principal.
- Python 3.12 para ejecución nativa equivalente a CI.
- Node 22 y npm para frontend (CI y contenedores usan esa versión mayor).
- Dependencias de backend en requirements; frontend en package-lock.json.

## Variables

| Variable | Valor local por defecto | Dónde se utiliza |
| --- | --- | --- |
| POSTGRES_USER | api_pulse | Contenedor PostgreSQL |
| POSTGRES_PASSWORD | api_pulse_password | Contenedor PostgreSQL |
| POSTGRES_DB | api_pulse | Contenedor PostgreSQL |
| DATABASE_URL | URL SQLAlchemy al host postgres:5432 | Backend |
| BACKEND_PORT | 8000 | Puerto de host del backend |
| FRONTEND_PORT | 5173 | Puerto de host del frontend |
| FRONTEND_ORIGIN | http://localhost:5173 | CORS backend |
| APP_ENV | development | `production` exige configuración pública segura y CORS estricto |
| VITE_API_BASE_URL | http://localhost:8000 | Cliente del navegador |
| REQUEST_TIMEOUT_SECONDS | 20.0 | Settings backend; Compose no la transmite actualmente |
| RESPONSE_SUMMARY_MAX_CHARS | 2000 | Settings backend; Compose no la transmite actualmente |
| PUBLIC_DEMO | true en backend nativo; false explícito en Compose local/integración | Solo escenarios controlados, sin salida de red |
| VITE_PUBLIC_DEMO | true si no se fija; false en Compose local/integración | Selector de escenarios en vez de URL arbitraria |
| DEMO_REQUESTS_PER_MINUTE_IP / GLOBAL | 10 / 60 | Cuotas iniciales en el worker de demo |
| DEMO_CONCURRENT_IP / GLOBAL | 2 / 10 | Admisión simultánea inicial |
| DEMO_MAX_REQUEST_BYTES / RESPONSE_BYTES | 16384 / 65536 | Límites de entrada y resultado controlado |
| HISTORY_RETENTION_HOURS / HISTORY_MAX_RECORDS | 24 / 500 | Historial público compartido |
| PYTHON_VERSION / NODE_VERSION | No requeridas en local | `render.yaml` fija 3.12.14 / 22.14.0 para los builds de Render |

`.env.example` contiene las variables de infraestructura iniciales salvo FRONTEND_ORIGIN. Puedes añadir esta última a tu `.env` o establecerla en la sesión. REQUEST_TIMEOUT_SECONDS y RESPONSE_SUMMARY_MAX_CHARS requieren entorno del proceso backend o modificar la configuración que los transmite: añadirlos solo al .env de Compose no los inyecta automáticamente.

Los Compose locales fijan `PUBLIC_DEMO=false` para reproducir T03 con destinos controlados. `render.yaml` fija `APP_ENV=production`, `PUBLIC_DEMO=true` y `VITE_PUBLIC_DEMO=true`. Nunca usar el modo de URLs arbitrarias en una URL pública: su transporte sigue separando validación DNS y conexión. Los límites por IP se calculan con el par observado por ASGI, no con cabeceras aportadas por el cliente; T07 comprobó un 429 tras el proxy, pero no la separación entre visitantes distintos. El límite global permanece activo en una instancia/worker.

Para producción, `DATABASE_URL` se introduce en Render como secreto con esquema `postgresql+psycopg`, hostname agrupado `-pooler...neon.tech`, `sslmode=require` y `channel_binding=require` (o TLS verificado con los parámetros exigidos por la validación). No guardar ni imprimir esa URL. `FRONTEND_ORIGIN` debe ser un único origen HTTPS. Ver [guía de despliegue](DESPLIEGUE_RENDER_NEON.md).

Las credenciales anteriores son valores de desarrollo. Cambiar POSTGRES_* exige mantener DATABASE_URL coherente. Modificar esas variables no cambia automáticamente usuarios/credenciales de una base ya inicializada en un volumen.

## Arranque local

~~~powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose config --quiet
docker compose up --build -d
docker compose ps
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/ready
~~~

El archivo .env no se versiona. Backend y frontend esperan a los servicios de los que dependen.

### Puertos alternativos

~~~powershell
$env:FRONTEND_PORT = "5174"
$env:FRONTEND_ORIGIN = "http://localhost:5174"
docker compose up --build -d
~~~

Abrir http://localhost:5174. Si cambias BACKEND_PORT, actualiza también VITE_API_BASE_URL. PostgreSQL tiene el puerto de host 5432 fijo en Compose; si está ocupado, preparar un override acotado a API Pulse.

No detengas contenedores de otros proyectos. Como el código se copia a las imágenes, reconstruye después de modificarlo.

### Ejecución nativa opcional

Con PostgreSQL accesible y variables propias del entorno:

~~~powershell
# Desde backend; requiere Python 3.12 instalado.
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:DATABASE_URL = "postgresql+psycopg://api_pulse:api_pulse_password@localhost:5432/api_pulse"
$env:FRONTEND_ORIGIN = "http://localhost:5173"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
~~~

En otra terminal, desde frontend:

~~~powershell
npm ci
npm run dev
~~~

No copies valores de producción a este ejemplo.

## Controles de calidad con el stack activo

~~~powershell
docker compose exec -T backend python -m compileall app tests
docker compose exec -T backend pytest
docker compose exec -T backend ruff check app tests
docker compose exec -T frontend npm ci
docker compose exec -T frontend npm test
docker compose exec -T frontend npm run build
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm audit --omit=optional
~~~

Comprueba el código de salida de cada comando antes de continuar. Un fallo de Docker no debe confundirse con un resultado de pytest.

Alternativa nativa desde backend: usar `.\.venv\Scripts\python.exe -m pytest`, `-m ruff check app tests ..\tests\integration` y `-m compileall app tests ..\tests\integration`. Desde frontend: `npm ci`, `npm test`, `npm run build`, `npm run lint`, `npm audit --omit=optional`.

## Qué cubre la CI actual

`.github/workflows/quality.yml` se ejecuta en PR hacia main y push a main:

- Backend: compilación, pytest y Ruff, incluido el fixture Python de integración; Python 3.12.
- Frontend: npm ci, pruebas de estado de la interfaz, build, lint y audit; Node 22.
- Docker Compose: sintaxis/interpolación de las configuraciones base e integrada.
- PostgreSQL smoke: levanta PostgreSQL 16 efímero, arranca la aplicación en demo controlada, comprueba `/ready`, creación e historial tras reiniciar el cliente. No usa Neon ni destinatarios externos.

No publica. La suite backend general usa SQLite en memoria, sustituye la dependencia de sesión y simula DNS/HTTP; el job PostgreSQL separado cubre startup/persistencia con PostgreSQL real mediante `TestClient` como context manager. No verifica Neon, Render ni el dominio final. Las pruebas frontend usan el ejecutor integrado de Node y servicios simulados; comprueban la coordinación de estados, no sustituyen la validación en navegador.

`npm audit --omit=optional` cubre el conjunto de dependencias que analiza ese comando; no certifica el backend, las imágenes o toda la seguridad del producto.

## Comprobación integrada

1. Confirmar servicios y health.
2. Enviar GET a un destino de prueba autorizado; comprobar código/cuerpo/tiempo.
3. Usar un destino propio para POST/PUT/DELETE y respuestas 4xx/5xx.
4. Intentar localhost/IP privada y verificar rechazo persistido.
5. Verificar historial, límites y recuperación tras recargar/reiniciar sin eliminar datos.
6. Verificar móvil, teclado, errores y gráfico.
7. Para producción, repetir desde el dominio final y comprobar políticas/límites acordados.

### Stack aislado reproducible de T03

La configuración de integración evita los puertos predeterminados y no reutiliza el volumen de desarrollo:

~~~powershell
docker compose -p api-pulse-t03 -f compose.integration.yml config --quiet
docker compose -p api-pulse-t03 -f compose.integration.yml up -d --build --wait --wait-timeout 180
docker compose -p api-pulse-t03 -f compose.integration.yml ps
Invoke-RestMethod http://127.0.0.1:18000/health
~~~

Servicios del navegador: frontend `http://127.0.0.1:15173`, backend `http://127.0.0.1:18000`; PostgreSQL se publica solo en loopback como `15432`. Se pueden cambiar con `T03_FRONTEND_PORT`, `T03_BACKEND_PORT` y `T03_POSTGRES_PORT` antes de levantar el proyecto.

El destino `http://controlled-target.test:8080` solo se resuelve desde el backend de este stack. La red interna asigna una IP sintética clasificada como pública para comprobar el transporte sin usar POST/PUT/DELETE contra servicios ajenos. Rutas: `/echo`, `/status/404`, `/status/500` y `/redirect`. Esta subred es exclusiva de pruebas y no debe usarse en producción.

Para comprobar persistencia, reinicia sin borrar el volumen:

~~~powershell
docker compose -p api-pulse-t03 -f compose.integration.yml restart
docker compose -p api-pulse-t03 -f compose.integration.yml up -d --wait --wait-timeout 120
~~~

Al terminar, detener y retirar únicamente los contenedores/redes del proyecto. No añadir `--volumes`; el volumen `api-pulse-t03_t03_postgres_data` queda disponible para revalidación:

~~~powershell
docker compose -p api-pulse-t03 -f compose.integration.yml down
~~~

## Diagnóstico

| Síntoma | Revisar |
| --- | --- |
| Error al iniciar terminal en nwep | Abrir la carpeta real api-pulse |
| No se conecta al daemon Docker | Disponibilidad de Docker Engine y permisos; config válido no implica daemon activo |
| Navegador no llega al backend | VITE_API_BASE_URL, BACKEND_PORT, protocolo y red |
| CORS al cambiar puerto | FRONTEND_ORIGIN debe coincidir exactamente con origen de la UI |
| Datos/credenciales inconsistentes | DATABASE_URL, configuración y volumen existente |
| Configuración cambiada sin efecto | Reconstrucción y variables transmitidas al contenedor |

Para ver logs: `docker compose logs --tail 100 backend` o el servicio afectado. Evitar copiar datos sensibles al informe. No usar eliminación de volúmenes como solución de diagnóstico.

## Registro de una validación

~~~text
Fecha/zona:
Commit:
Entorno y versiones:
Comando o caso:
Resultado y código de salida:
Evidencia:
Límite o fallo:
Tarea que queda:
~~~

Los resultados de esta organización están en [estado actual](ESTADO_ACTUAL.md); la próxima sesión debe reemplazarlos o complementarlos con ejecución real.
