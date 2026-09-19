# Arquitectura actual y preparación del despliegue

Descripción del código local tras T06; la infraestructura pública aún no está desplegada.

## Flujo

~~~mermaid
flowchart LR
    V[Visitante] --> UI[Vue 3 / Vite]
    UI --> API[FastAPI]
    API --> MODE{Modo}
    MODE -->|Demo pública| FIXED[Escenarios canónicos]
    FIXED --> MOCK[httpx MockTransport sin salida de red]
    MODE -->|Desarrollo local| VALID[Validación URL e IP/DNS]
    VALID --> HTTP[Cliente httpx]
    HTTP --> DEST[API de destino]
    API --> DB[(PostgreSQL: api_checks)]
    DB --> API
    API --> UI
~~~

Una petición rechazada por seguridad también se guarda en la base. El frontend no llama directamente a la API de destino.

## Componentes y responsabilidades

| Ruta desde la raíz | Responsabilidad |
| --- | --- |
| `frontend/src/App.vue` | Composición de la pantalla y conexión de los estados con los componentes |
| `frontend/src/composables/useApiDashboard.js` | Coordinación independiente de solicitud, resultado, historial, salud y reintentos |
| `frontend/src/components/ApiRequestForm.vue` | Formulario y validación local de URL/JSON |
| `frontend/src/components/ResponsePanel.vue` | Resultado, carga y errores |
| `frontend/src/components/HistoryTable.vue` | Historial y códigos HTTP |
| `frontend/src/components/ResponseTimeChart.vue` | SVG y promedio de las últimas 12 respuestas válidas |
| `frontend/src/services/api.js` | fetch, errores y resolución de URL del backend |
| `backend/app/main.py` | FastAPI, CORS por entorno, inicio de tablas, health y readiness |
| `backend/app/config.py` | Configuración con pydantic-settings y validación de producción cerrada |
| `backend/app/schemas.py` | Validación y contratos de entrada/salida |
| `backend/app/routers/checks.py` | Ejecutar, persistir y listar comprobaciones |
| `backend/app/services/security.py` | Esquema, hostname e IPs resueltas |
| `backend/app/services/api_client.py` | Solicitud saliente, errores, resumen y cabeceras permitidas |
| `backend/app/services/demo.py` | Escenarios finitos sin conexión externa y resúmenes seguros |
| `backend/app/services/limits.py` | Cuotas por par y globales, además de concurrencia del worker único |
| `backend/app/database.py` | Engine y sesiones SQLAlchemy |
| `backend/app/models.py` | Tabla ApiCheck |
| `compose.integration.yml` | Stack T03 aislado con PostgreSQL real y destino HTTP controlado |
| `tests/integration/controlled_target.py` | Eco de métodos/cuerpo/cabeceras y respuestas 302/4xx/5xx sin usar servicios públicos |
| `.github/workflows/quality.yml` | Calidad más smoke PostgreSQL 16 efímero; no despliega |
| `render.yaml` | Dos servicios Render Free, URL pública cruzada y secreto Neon fuera de Git |

## Ciclo de una comprobación

1. El formulario verifica URL completa y objetos JSON.
2. `POST /api/checks` aplica el esquema de Pydantic. Un esquema inválido devuelve 422 sin guardar un check.
3. En modo público, se exige una URL canónica del catálogo y se aplica el límite de admisión; en desarrollo se conserva la validación de destino. Un rechazo de seguridad se persiste con URL genérica segura; un 429/413 no crea check.
4. En modo público, httpx usa `MockTransport` y no realiza DNS ni socket. En desarrollo, usa una solicitud real síncrona con redirecciones desactivadas.
5. Se mide el tiempo del cliente HTTP, se interpreta JSON o texto y se recorta el resumen.
6. En modo público se guarda solo un resumen fijo del escenario, se elimina el exceso de 24 h/500 filas y se devuelve la respuesta acotada. No se guarda cuerpo/cabeceras/IP. Los registros heredados inseguros se eliminan antes de listar.
7. La interfaz muestra el resultado y vuelve a pedir el historial. Si esa recarga falla, conserva el resultado y el historial anterior, y ofrece un reintento separado.

## Topología de integración T03

`compose.integration.yml` usa el proyecto Docker `api-pulse-t03`, puertos alternativos ligados a `127.0.0.1` y un volumen PostgreSQL propio. El destino `controlled-target.test` no publica puertos en el host: vive en una red interna y recibe la IP sintética `8.8.8.8` para atravesar, solo durante esta prueba, la política actual que exige una dirección clasificada como pública. El backend resuelve ese nombre mediante `extra_hosts` y conecta al servidor controlado; no existe reenvío a Internet.

La subred sintética sombrea ese rango únicamente dentro de los contenedores conectados a la red de integración. Esta configuración es una herramienta de prueba, no una propuesta de producción ni una excepción que deba incorporarse al servicio público.

El tiempo no incluye la validación DNS previa, la persistencia ni la actualización de la interfaz. El timeout configurado en httpx no debe interpretarse como un presupuesto global que cubra DNS, transferencia completa y base de datos.

## Datos persistidos

Tabla `api_checks`:

| Campo | Tipo | Observación |
| --- | --- | --- |
| id | Integer PK | Identificador |
| url | Text | URL original recibida, puede contener parámetros sensibles |
| method | Text | Método normalizado |
| status_code | Integer nullable | Código de la API consultada |
| response_time_ms | Integer nullable | Puede ser null en rechazo previo a conexión |
| created_at | DateTime con zona | Valor inicial en UTC |
| response_summary | Text | Máximo 2000 caracteres por defecto |
| success | Boolean | Respuesta HTTP recibida |
| error_message | Text nullable | Fallo de seguridad o cliente |

No se persisten como columnas el body ni las cabeceras de la solicitud. En modo público, URL y resumen se vuelven valores canónicos del escenario, y la limpieza se realiza al iniciar/crear/listar. No hay propietarios ni borrado individual. En desarrollo local las URLs y respuestas originales pueden seguir guardándose: no usar ese modo con datos reales ni exponerlo a Internet.

## Entorno local

- PostgreSQL 16 Alpine, volumen `postgres_data`, puerto de host 5432.
- Backend Python 3.12, Uvicorn, puerto interno 8000.
- Frontend Node 22, servidor Vite, puerto interno 5173.
- PostgreSQL tiene healthcheck; backend depende de ese estado.
- Frontend depende del healthcheck HTTP del backend.
- `GET /health` solo devuelve estado del proceso; no consulta la base.
- `Base.metadata.create_all` crea tablas faltantes, no es un sistema de migraciones.
- Los contenedores reciben código mediante COPY; no hay montaje de fuentes ni recarga de backend configurada.

## Topología de producción preparada en T06

`render.yaml` prepara un Static Site Render con `frontend/dist` y un Web Service Render Python Free en Virginia. El navegador llama a la URL HTTPS pública de la API; el sitio estático no usa la red privada de Render. La API usa un Neon Free separado en N. Virginia mediante endpoint PostgreSQL agrupado, credenciales externas y TLS con channel binding. La conexión Render → Neon sale por Internet; **no es una base en red privada**. No hay servicio PostgreSQL ni puerto 5432 en Render.

La URL de API se incorpora al build de Vite por `VITE_API_BASE_URL`; si falta o no es un único origen HTTPS, la compilación pública falla. `FRONTEND_ORIGIN` limita CORS en producción a un único origen HTTPS, métodos GET/POST y cabecera `Content-Type`, sin credenciales ni regex de redes locales. `APP_ENV=production` exige modo público controlado y Neon pooled/TLS. Uvicorn corre con un solo worker y sin access log ni confianza ciega en cabeceras de proxy. El pool SQLAlchemy usa `pool_pre_ping`, recicla conexiones a 240 s y acota a 2 conexiones base más 1 temporal para tolerar suspensión/inicio en frío.

`/health` es liveness sin consulta de base para Render; `/ready` ejecuta un `SELECT 1` y devuelve 503 genérico si Neon no responde. El backend sigue usando `create_all` para el esquema v1, que no migra cambios de columnas; antes de un futuro cambio de esquema se requiere migración explícita y plan de reversión. La CI nueva comprueba startup/persistencia con PostgreSQL 16 efímero, pero no reemplaza la prueba real con Neon y proxy en T07. Ver [procedimiento de despliegue](DESPLIEGUE_RENDER_NEON.md).

La ruta pública evita la separación DNS/conexión al no tener salidas de red para checks. La ruta local con URLs arbitrarias conserva esa limitación y debe permanecer privada. T07 verificará los controles, el arranque en frío y la persistencia detrás del proxy real y con Neon.
