# Estado actual

**Corte:** 2026-09-20, America/Bogota. **Objetivo:** proyecto de portafolio con despliegue público. Ver la [evidencia pública de T07](VALIDACION_T07.md).

## Base de la revisión

- Worktree utilizado para T01–T06: `C:\Users\giral\.codex\worktrees\7c72\api-pulse`.
- El checkout fuente histórico está en `C:\Users\giral\OneDrive\Documentos\Esteban\api-pulse`; la ruta antigua `nwep` no existe.
- Repositorio: [estebanfrm/Api-Pulse](https://github.com/estebanfrm/Api-Pulse).
- Base inicial: commit `7399e86`; T00–T06 se guardaron en `1f373b4`. El [PR #4](https://github.com/estebanfrm/Api-Pulse/pull/4) integró T00–T08 en `main` mediante el merge `0cb28cf`.
- Git confirmó `origin/main` en `7399e86` el 2026-09-19. La primera consulta dentro del sandbox falló por red; fuera del sandbox se confirmó el hash y se publicó la rama sin modificar `main`.
- T01 modificó pruebas, documentación y las versiones frontend necesarias para cerrar la auditoría. T02 modificó la coordinación y presentación de estados frontend, añadió sus pruebas y extendió la CI. T03 añadió un stack de integración aislado y su destino controlado. T04 preparó la propuesta aprobada. T05 implementó el modo público acotado y su historial. T06 preparó Render/Neon, configuración cerrada de producción, readiness y smoke CI de PostgreSQL, ejecutado después en GitHub Actions. Se preservaron los contratos locales al fijar `PUBLIC_DEMO=false` en los Compose de desarrollo/integración.

## Implementado por inspección

| Área | Evidencia | Estado |
| --- | --- | --- |
| Formulario HTTP | `frontend/src/components/ApiRequestForm.vue` | Selector de escenarios públicos; URL libre solo en modo local, cuatro métodos y JSON validado |
| Resultados | `ResponsePanel.vue`, `useApiDashboard.js` | Cuerpo, código, tiempo y error de solicitud independiente |
| Historial | `routers/checks.py`, `models.py`, `HistoryTable.vue` | Persistencia, listado, error independiente y reintento; poda/redacción en modo público |
| Gráfica | `ResponseTimeChart.vue` | Hasta 12 respuestas con tiempo válido |
| Solicitudes salientes | `services/api_client.py`, `services/demo.py` | httpx sin redirecciones; escenario público sintético sin socket ni DNS hacia el destino |
| Destinos permitidos | `services/security.py`, `services/demo.py` | Modo local con validación IP/DNS; modo público con catálogo fijo |
| Calidad y validación | Workflow, suites y `compose.integration.yml` | T08 local: 72 backend aprobados, 1 smoke omitido por falta de Docker, 8 frontend, lint/build; PostgreSQL smoke y los cuatro jobs aprobaron en CI del merge |
| Despliegue público | `render.yaml`, [guía](DESPLIEGUE_RENDER_NEON.md) y [evidencia T07](VALIDACION_T07.md) | Sitio/API HTTPS en Render Free con Neon Free; presentación T08 y licencia MIT visibles desde `main` |

## Hallazgos prioritarios

1. **Portafolio público cerrado con límites explícitos.** D08–D12 están aprobadas. Sitio `a32bc4f` y API `98cb6f9` siguen Live en Render con Neon Free. La visita tras más de 16 minutos sin tráfico conservó historial y permitió escribir otra fila. README, capturas y `LICENSE` MIT con «API PULSE» son visibles desde `main`, y la [CI de `main`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35541246577) aprobó. Ver [validación T07](VALIDACION_T07.md).
2. **Cuotas por proceso/proxy.** Los límites por IP y global son en memoria y no coordinan réplicas. El Blueprint fija un worker y una instancia Free. Un cliente recibió 429 tras el límite en Render, pero no se ha demostrado aislamiento entre visitantes distintos que puedan compartir la IP de par. No se confía en `X-Forwarded-For` enviado por el visitante.
3. **Modo local distinto del público.** En local continúa la validación DNS antes de httpx sin fijar la IP efectiva; no se ha probado una explotación. No exponer ese modo. En público el catálogo sintético usa `MockTransport`, sin DNS ni socket para los destinos de comprobación.
4. **Esquema v1 sin migraciones.** `create_all` crea tablas vacías al arrancar, no cambia columnas existentes. T06 no altera el modelo y documenta que un cambio futuro requiere migración explícita, copia previa y rollback. La base Neon no está en la red privada de Render: se protege con credenciales/TLS, no con aislamiento de red entre proveedores.
5. **CI ampliada y aprobada.** La primera CI del PR #4 falló en `npm audit` por respuestas 503/400 del registro; se resolvió en reintento sin cambiar dependencias. La CI final de T08 y la del merge `0cb28cf` aprobaron los cuatro jobs. La auditoría local devolvió cero hallazgos. La CI no cubre navegador/Neon; ambos se probaron manualmente en T07. Ver [evidencia](VALIDACION_T07.md).
6. **Avisos de deprecación en pruebas.** T09 migró `on_event` a `lifespan`; pytest ya solo informa el aviso de `BlockingPortal` de Starlette. No es un fallo actual, pero debe considerarse al actualizar ese stack.
7. **Correcciones de T09 sin desplegar.** Las correcciones de la auditoría T09 están en el worktree y no se han publicado. El sitio y la API en Render siguen sirviendo `0cb28cf`/`a32bc4f`; `autoDeployTrigger: "off"` exige un despliegue manual para que lleguen a la demo pública.

## T01 — Pruebas y calidad

**Estado: completado localmente el 2026-09-15.** Se repararon los tres casos parametrizados de errores de httpx y el caso DNS no resoluble. Se añadió cobertura de `follow_redirects=False`, respuestas 404/500 con `success=true`, GET sin cuerpo, truncamiento del resumen, orden y límites 1–100 del historial, y DNS con resolución mixta pública/privada. Todos los clientes HTTP y DNS externos están simulados; el historial se pobló con URLs de localhost rechazadas antes de cualquier conexión. La extensión de cierre actualizó Vite y cuatro dependencias transitivas para llevar la auditoría de cinco hallazgos a cero.

Actualizaciones: Vite 6.4.2 → 6.4.3, `brace-expansion` 5.0.6 → 5.0.12, `nanoid` 3.3.12 → 3.3.19, `postcss` 8.5.15 → 8.5.28 y `postcss-selector-parser` 7.1.1 → 7.1.6. Solo Vite es dependencia directa; las demás versiones están fijadas por `package-lock.json`.

Entorno: Python 3.12.14, Node 22.14.0, npm 10.9.2 y Docker CLI 29.3.1. Base `7399e86`, cambios sin commit.

### Comprobaciones aprobadas

| Comando o control | Resultado | Alcance |
| --- | --- | --- |
| `.\.venv\Scripts\python.exe -m pytest` | 40 passed, código 0, 3 avisos de deprecación | Suite backend con SQLite en memoria, mocks HTTP/DNS y sin tráfico externo |
| `.\.venv\Scripts\python.exe -m ruff check app tests` | All checks passed, código 0 | Aplicación y pruebas |
| `.\.venv\Scripts\python.exe -m compileall app tests` | Código 0 | Sintaxis de aplicación y pruebas |
| `docker compose config --quiet` | Código 0 | Sintaxis e interpolación; emitió advertencia de acceso a la configuración global de Docker |
| `npm ci` | 114 paquetes instalados y 115 auditados, 0 vulnerabilidades, código 0 | Instalación limpia desde el lockfile actualizado |
| `npm run build` | Build de Vite 6.4.3 aprobado, 15 módulos, código 0 | Artefacto de producción local; requirió ejecución fuera del sandbox por lectura del runtime de esbuild |
| `npm run lint` | Código 0 | ESLint sobre frontend |
| `npm audit --omit=optional` | 0 vulnerabilidades, código 0 | Consulta final al registro después de instalación limpia |
| `git diff --check` | Código 0 | Sin errores de espacios en los cambios versionables |

### Incidencias de ejecución resueltas

| Comando o control | Resultado | Consecuencia |
| --- | --- | --- |
| Auditoría inicial | Código 1: 5 vulnerabilidades, 1 baja y 4 altas | Se aplicaron actualizaciones mínimas, instalación limpia y auditoría final con código 0 |
| `pip install -r requirements-dev.txt` con el índice predeterminado | El índice no ofrecía `ruff==0.8.4` | Se instaló el mismo conjunto declarado usando el índice oficial para Ruff; no se modificaron manifests |
| Primeros intentos de `npm ci` y build dentro del sandbox | Acceso de red/lectura denegado | Ambos controles se repitieron fuera del sandbox y terminaron aprobados |
| Repetición intermedia de pytest | Un caso nuevo supuso desempate por inserción cuando varias fechas eran iguales | Se ajustó al contrato real de fechas descendentes; la aplicación no cambió y la suite final aprobó |

### No ejecutado

| Comprobación | Motivo |
| --- | --- |
| Arranque de Compose y PostgreSQL real | Docker Engine no estaba disponible; corresponden a T03 |
| Navegador | No se ejecutó durante T01; se validó después como parte de T02 |
| GitHub Actions remoto | No hay commit de T01 publicado ni se modificaron refs remotas |
| Despliegue | Fuera de alcance de T01; T05–T07 siguen pendientes al corte actual |

El README previo menciona auditorías históricas y una CI aún sin ejecución exitosa. No se presenta ninguna de esas afirmaciones como evidencia actual.

## T02 — Recuperación y claridad de interfaz

**Estado: completado localmente el 2026-09-15.** Se extrajo la coordinación a `frontend/src/composables/useApiDashboard.js` para mantener separados solicitud, historial y salud. La inicialización y los reintentos manejan sus fallos sin propagar rechazos esperados; un fallo del historial conserva tanto el resultado actual como los registros previos. El indicador ahora distingue Checking/Online/Offline, permite reconexión y la tabla ofrece un reintento propio. `Response received`/`No response` reemplaza la etiqueta ambigua de éxito, y una respuesta HTTP 4xx/5xx conserva y explica su código.

La cobertura frontend usa el ejecutor integrado de Node y servicios simulados, sin dependencias nuevas. La CI ejecutará esta suite antes del build. La comprobación del navegador utilizó Vite y un servidor HTTP simulado enlazado solo a `127.0.0.1`; no realizó solicitudes externas.

### Comprobaciones aprobadas

| Comando o control | Resultado | Alcance |
| --- | --- | --- |
| `npm test` | 4 passed, 0 failed | Caída inicial, resultado conservado, recuperación y separación de errores |
| `npm run lint` | Código 0 | Aplicación, composable, pruebas y fixture local |
| `npm run build` | Build de Vite 6.4.3 aprobado, 16 módulos | Compilación de los cambios de interfaz |
| `npm audit --omit=optional` | 0 vulnerabilidades | Manifiesto y lockfile finales de T01/T02 |
| Suite backend, Ruff y compilación | 40 passed, 3 avisos; código 0 en los tres controles | Regresión final después de T02; backend sin cambios de aplicación |
| `docker compose config --quiet` y `git diff --check` | Código 0; Compose emitió solo la advertencia de acceso a configuración global | Configuración interpolada y cambios versionables |
| Navegador, backend detenido | Offline, error de historial y botones de reintento visibles | La carga inicial terminó sin quedar en Checking |
| Navegador, recuperación controlada | Online y dos entradas recuperadas | Salud e historial se recuperaron sin recargar la página |
| Navegador, HTTP 500 + historial 503 | Resultado 500 visible como respuesta recibida; historial anterior y error separado visibles | Conservación y semántica RF04/RF08 |
| Reintento con teclado | Enter sobre `Retry history` recuperó tres entradas | Navegación semántica del control |
| Vista móvil 390 × 844 | Panel de respuesta legible, tarjetas apiladas y sin desbordamiento horizontal observado | Comprobación visual local de RP09 |
| Consola del navegador | 0 errores, 0 advertencias | Escenarios anteriores |

### Incidencias de ejecución resueltas

| Comando o control | Resultado | Consecuencia |
| --- | --- | --- |
| Primera aserción de identidad sobre un `ref` de Vue | Falló porque Vue devuelve un proxy reactivo | Se corrigió a comparación estructural; la suite final aprobó |
| Primer lint del fixture local | Detectó globales no declaradas | Se importaron las APIs de Node de forma explícita; lint final aprobado |
| Lanzamiento del fixture mediante el shim de npm | El shim global apuntaba a un módulo inexistente | Se ejecutó el mismo script con el binario Node del sistema; el escenario de navegador aprobó |

### No ejecutado

| Comprobación | Motivo |
| --- | --- |
| Stack Docker y PostgreSQL real | No se intentó en T02; la última comprobación de T01 no tenía Docker Engine y el alcance corresponde a T03 |
| Suite E2E automatizada | T02 añadió pruebas de estado y validación manual controlada; evaluar automatización proporcional en T03/T07 |
| GitHub Actions remoto | Los cambios siguen sin commit publicado |
| Despliegue | Fuera de alcance de T02; T05–T07 siguen pendientes al corte actual |

## T03 — Validación integrada local

**Estado: completado localmente el 2026-09-15.** Se creó `compose.integration.yml` con el proyecto exclusivo `api-pulse-t03`, puertos 15173/18000/15432 ligados a loopback, volumen propio y PostgreSQL 16. El destino `controlled-target.test` vive sin puerto de host en una red Docker interna y sirve eco, 302, 404 y 500. Su IP sintética solo permite atravesar el filtro de direcciones para probar el transporte real; no reenvía tráfico a Internet y la configuración no es apta para producción.

El flujo creó diez registros: cuatro métodos correctos, respuestas HTTP de error/redirección y dos bloqueos locales comprobados desde terminal/navegador. Una petición PATCH y un límite 101 devolvieron 422 sin convertirse en checks. PostgreSQL confirmó zona UTC, conteos y persistencia después de reiniciar todo el stack; una recarga nueva del navegador recuperó los diez registros.

### Comprobaciones aprobadas

| Comando o control | Resultado | Alcance |
| --- | --- | --- |
| `docker info` | Engine 29.3.1, Docker Desktop | Motor real disponible después de iniciarlo |
| `docker compose -p api-pulse-t03 -f compose.integration.yml config --quiet` | Código 0 | Configuración aislada válida |
| `up -d --build --wait --wait-timeout 180` | Cuatro servicios iniciados; postgres/backend/destino sanos | Build reproducible y arranque con dependencias |
| Health e historial inicial | `ok`, API y PostgreSQL con 0 filas | Baseline limpio del volumen nuevo |
| GET/POST/PUT/DELETE | 200/201; método, JSON y cabecera reflejados | Destino propio; GET confirmó body ausente |
| 404/500/302 | `success=true`, códigos conservados; 302 no seguido | Contratos RF04/RF09 |
| Localhost bloqueado | `success=false`, sin código, mensaje de seguridad y registro persistido | Bloqueo antes de conexión |
| Validación y límites | PATCH 422 sin registro; límite 3 devuelve 3 y 101 devuelve 422 | Esquema e historial |
| Orden y base | API en fecha descendente; PostgreSQL UTC y 8/8 filas antes del navegador | Persistencia real |
| Reinicio sin borrar volumen | Health `ok`; API/PostgreSQL conservaron 8/8 filas | Recuperación de todo el stack |
| Navegador integrado | 500 recibido, bloqueo visible, error JSON, gráfica, fechas e historial de 10 filas | UI contra FastAPI/PostgreSQL reales |
| Recarga del navegador | 10 filas recuperadas | Persistencia visible en una carga nueva |
| Consola del navegador | 0 errores, 0 advertencias | Recorrido integrado |
| Ruff/compile del destino | Aprobados | Fixture de integración |

### Incidencias de ejecución resueltas

| Incidencia | Resultado | Consecuencia |
| --- | --- | --- |
| Docker Engine inicialmente detenido | Docker Desktop se inició y Engine 29.3.1 respondió | T03 pudo ejecutarse; no era un fallo de API Pulse |
| Primera construcción Python lenta | Terminó correctamente y dejó las capas cacheadas | Demora de red, sin cambio de dependencias |
| Conteo inicial del arnés PowerShell mostró 1 | `Invoke-RestMethod` envolvió el array como un único objeto | Se repitió con JSON explícito; API y PostgreSQL confirmaron 8 y después 10 filas |
| Log PostgreSQL coincidió con `FATAL` | `terminating connection due to administrator command` durante el reinicio solicitado | Evento esperado de la prueba de persistencia; servicios volvieron sanos |

### No ejecutado

| Comprobación | Motivo |
| --- | --- |
| GitHub Actions remoto | Los cambios continúan sin commit publicado |
| Suite E2E automatizada en CI | El navegador se validó manualmente; la CI aún no levanta el stack T03 |
| Despliegue | Fuera de alcance de T03; T05–T07 siguen pendientes al corte actual |

Al cerrar T03 se retiraron solo los contenedores y redes con `docker compose ... down`, sin `--volumes`. El volumen `api-pulse-t03_t03_postgres_data`, con los diez registros controlados, se conserva para revalidación; los contenedores ajenos permanecieron activos.

## T04 — Decisiones de demo y alojamiento

**Estado: completado el 2026-09-19.** Se compararon precios y capacidades actuales usando fuentes oficiales y se creó [la propuesta completa](PROPUESTA_T04.md). El usuario aprobó D09 el 2026-09-15 y D08, D10, D11 y MIT en D12 el 2026-09-19, después de un desglose explícito de sus consecuencias. Los valores numéricos de cuotas/bytes/timeout siguen como parámetros técnicos iniciales sujetos a pruebas de T05.

### Decisiones y recomendaciones

| Decisión | Elección confirmada |
| --- | --- |
| D08 | Demo pública anónima; GET/POST/PUT/DELETE solo contra escenarios controlados, con límites de frecuencia, concurrencia, tiempo y bytes |
| D09 | **Confirmada:** frontend/backend Render Free, Neon Free, Virginia, subdominios gratuitos y presupuesto USD 0 |
| D10 | Historial compartido de datos mínimos, 50 visibles, 500 máximo, retención 24 h; sin cuerpo, cabeceras, IP ni credenciales persistidas |
| D11 | Interfaz en inglés; documentación española con resumen ejecutivo en inglés |
| D12 | MIT elegida; nombre público del titular y archivo `LICENSE` pendientes para T08 |

La opción confirmada añade arranques en frío, una base externa y dos proveedores. T06/T07 incorporan esas condiciones sin crear tareas nuevas. Se descartó Render Postgres Free para una demo persistente porque su documentación indica expiración a 30 días y ausencia de backups. Render pagado queda como escalamiento futuro no autorizado.

### Comprobaciones aprobadas

| Control | Resultado |
| --- | --- |
| Precios oficiales de Render | USD 7 web 512 MB; USD 6 PostgreSQL 256 MB; USD 0,30/GB de almacenamiento; estático gratuito |
| Capacidades de Render | Vue/FastAPI/PostgreSQL compatibles; TLS/subdominios, red privada regional, health y rollback documentados |
| Límites gratuitos de Render | Backend se apaga tras 15 min y tarda alrededor de 1 min en iniciar; PostgreSQL Free expira a 30 días y no tiene backups |
| Alternativa Neon Free | 0,5 GB, 100 CU-horas/proyecto y pooling disponible según fuentes oficiales consultadas |
| Licencia | SPDX confirma el identificador y texto estándar MIT |
| Integridad documental | Enlaces locales de la propuesta y referencias D08–D12 comprobados |
| Confirmación de decisiones | Respuestas expresas del usuario del 2026-09-15 y 2026-09-19 registradas en D08–D12 |

### No ejecutado

| Acción | Motivo |
| --- | --- |
| Crear cuentas o recursos | La elección de proveedor está aprobada, pero la creación/publicación corresponde a T07 y requiere acceso a las cuentas |
| Comprar dominio | La propuesta usa subdominios Render en v1; no hay compra aprobada |
| Implementar límites, retención o infraestructura | Corresponde a T05/T06; T04 fue de decisiones y documentación |
| Crear `LICENSE` | Falta el nombre público exacto del titular; se solicitará en T08 |
| Pruebas de código | T04 solo cambia documentación; no se modificó comportamiento de aplicación |

## T05 — Controles de exposición pública

**Estado: completado localmente el 2026-09-19; prueba sobre Neon y dominio final pendiente para T07.** Se añadió un catálogo de `/echo`, `/status/404`, `/status/500` y `/redirect` bajo `https://demo.api-pulse.invalid`. Es un destino sintético: `httpx.MockTransport` responde dentro del proceso, sin resolver DNS ni abrir conexiones hacia hosts arbitrarios. Los cuatro métodos aprobados siguen disponibles; una URL fuera del catálogo se persiste como comprobación fallida con URL canónica `/blocked`, HTTP 200 de API Pulse, sin registrar el valor enviado. Entrada inválida por esquema mantiene 422; exceso de cuerpo 413 y cuota 429 no crean fila. La redirección 302 se recibe sin seguirla.

Límites iniciales: 16 KiB de cuerpo HTTP de creación, 64 KiB de respuesta de escenario, timeout configurado en el cliente de 8 s, 10 comprobaciones/minuto y 2 concurrentes por IP de par, 60/minuto y 10 concurrentes globales. El transporte sintético es determinista, por lo que el timeout no representa una prueba de espera real de red. Los contadores viven en memoria de un proceso y se reinician con él; para v1 T06 debe mantener una sola instancia/worker. Los fallos de httpx ya no devuelven detalles de excepción que podrían incluir datos de transporte. El modo público no acepta destinos arbitrarios; el Compose local/integrado conserva el modo de T03 explícitamente.

El historial público es compartido y conserva URL canónica, método, estado, tiempo, resumen sintético y mensaje genérico. No guarda headers ni body. Al iniciar el backend, al crear y al listar se eliminan filas mayores de 24 h, filas heredadas fuera del formato público y exceso sobre las 500 más recientes. Esto limita la visibilidad tras cada acceso; no equivale a un job de borrado continuo mientras el servicio duerme. Se añadió selector de escenarios y aviso para no enviar secretos. Ver [contrato de API](API.md) y [arquitectura](ARQUITECTURA.md).

| Comprobación | Resultado |
| --- | --- |
| `backend/.venv/Scripts/python.exe -m pytest -q` desde `backend` | 62 passed; tres avisos preexistentes de Starlette/FastAPI |
| Ruff y `compileall` | Aprobados |
| `node --test` desde `frontend` | 5 passed |
| ESLint y Vite build mediante los scripts de Node locales | Aprobados; el build necesitó autorización para leer `esbuild` fuera del sandbox |
| `docker compose config --quiet` y configuración de integración | Aprobadas con aviso de lectura de la configuración local de Docker |
| `git diff --check` | Aprobado; solo avisos de conversión LF/CRLF en archivos ya modificados |

**No ejecutado:** arranque Docker/PostgreSQL de T05 porque Docker Engine estaba apagado; verificación con Neon, proxy Render, cuotas en producción, navegador del dominio final y CI de un commit publicado corresponden a T06/T07. La suite T03 sí comprobó previamente el flujo con PostgreSQL, pero no prueba los cambios nuevos sobre Neon. El shim global de npm apunta a un `npm-cli.js` inexistente; se ejecutaron las herramientas instaladas directamente con Node y aprobaron. No hubo recursos creados, gasto ni publicación.

## T06 — Configuración reproducible de producción

**Estado: preparada localmente el 2026-09-19; no desplegada.** `render.yaml` define `api-pulse-api` como Python Web Service Free en Virginia y `api-pulse-web` como Static Site con `frontend/dist`. Las URL HTTPS asignadas por Render se referencian entre servicios para configurar CORS y el build de Vite; no se inventó un dominio. `DATABASE_URL` se solicitará como secreto al sincronizar el Blueprint tras crear Neon Free en N. Virginia. El inicio de API usa un worker, modo demo público, sin access log ni confianza ciega en cabeceras de proxy. En modo producción se exige URL Neon agrupada con psycopg, TLS/channel binding, origen frontend HTTPS único y CORS restringido; en Render no se permite `APP_ENV=development`. El build público falla sin una URL de API HTTPS no local.

Se añadió `/ready` con `SELECT 1` y 503 genérico si la base falla. `/health` permanece como liveness sin consulta a Neon para no despertarla con sondeos periódicos. SQLAlchemy mantiene `pool_pre_ping` y añade reciclaje a 240 segundos con pool acotado 2+1. No se cambió el esquema: `create_all` sigue siendo bootstrap de la tabla v1, no migración. La [guía](DESPLIEGUE_RENDER_NEON.md) cubre secretos, cuotas, creación, smoke test, base vacía, rollback y la limitación de que Neon no está en la red privada de Render. La CI añade un job PostgreSQL 16 efímero para startup/readiness/persistencia, sin enviar HTTP a servicios ajenos.

| Comprobación | Resultado |
| --- | --- |
| `backend/.venv/Scripts/python.exe -m pytest -o addopts='' -q` | 72 passed, 1 skipped (smoke PostgreSQL requiere base dedicada); 3 avisos preexistentes |
| Ruff y compilación Python | Aprobados |
| Frontend `node --test` y ESLint local | 7 passed; lint aprobado |
| Vite build con `VITE_PUBLIC_DEMO=true` y URL HTTPS sintética Render | Aprobado, 17 módulos; bundle contiene URL de API configurada, no `localhost:8000` |
| Vite build público sin URL de API | Falló como se esperaba con error de configuración; se ejecutó con acceso a esbuild fuera del sandbox |
| CORS de producción en proceso aislado | Origen HTTPS configurado: preflight 200; `http://localhost:5173`: 400, sin cabecera de autorización |
| `render.yaml` y workflow parseados con PyYAML | Dos servicios, referencias internas, auto-deploy apagado y job PostgreSQL esperados; solo validación estructural local |
| Compose base/integración y `git diff --check` | Aprobados; Compose advirtió que no podía leer la configuración global de Docker y Git avisó solo sobre LF/CRLF |

**Al cierre de T06 no ejecutado:** `render blueprints validate` porque la CLI/servicio Render no estaba configurada; sincronización de Blueprint, creación Neon y despliegue corresponden a T07. Docker Desktop no habilitó el motor Linux y `com.docker.service` no pudo iniciarse por permisos del sistema, así que el nuevo smoke PostgreSQL no se pudo ejecutar localmente. La CI todavía no había corrido; su primer resultado está registrado en T07 abajo. No declarar Neon ni la URL pública como aprobados. T06 no creó recursos de alojamiento.

## T07 — Publicación y verificación

**Estado: completado el 2026-09-20 con limitaciones registradas; el PR #4 estaba en borrador al cierre de T07 y se fusionó después en T08.** Git confirmó entonces `main` en `7399e86`, la misma base local. Se creó y publicó `codex/api-pulse-t07-publication` con la preparación T00–T06 en `1f373b4`, y se abrió el [PR #4](https://github.com/estebanfrm/Api-Pulse/pull/4). El escaneo de patrones de claves en archivos versionables no encontró coincidencias; `.env` está ignorado. La revisión staged detectó y corrigió un espacio final en la documentación antes del commit.

| Comprobación T07 | Resultado |
| --- | --- |
| Backend pytest | 72 passed, 1 skipped (smoke PostgreSQL dedicado); 3 avisos de deprecación |
| Ruff y compilación Python | Aprobados |
| Frontend `node --test` y ESLint | 7 passed; lint aprobado |
| Vite build público con origen HTTPS sintético | Aprobado, 17 módulos; requirió acceso de esbuild fuera del sandbox |
| Compose base/integración | Config aprobada; advertencia de lectura de la configuración global Docker |
| `git diff --cached --check` | Aprobado tras corregir un espacio final documental |
| GitHub `main` público | `7399e86` confirmado con `git ls-remote` fuera del sandbox; la primera consulta dentro del sandbox falló por red |
| Esquema JSON oficial de Render | Intento no concluyente: el esquema actual usa JSON Schema 2020-12 y el Ajv 6.15 disponible solo comprende versiones anteriores; no se alteró `render.yaml` ni se declaró validación semántica |

La [primera CI del PR #4](https://github.com/estebanfrm/Api-Pulse/actions/runs/35457179818) terminó con 3 de 4 jobs aprobados: Backend, PostgreSQL smoke y Docker Compose. Frontend instaló dependencias, pasó 7 pruebas, build y lint; falló solo `npm audit --omit=optional`. El log mostró 503 al consultar `/-/npm/v1/security/advisories/bulk` y luego 400 en `/-/npm/v1/security/audits/quick`, el endpoint alterno. Se reprodujo localmente con npm 10.9.2: el log local también mostró bulk 503 y quick 400. `npm ls --depth=0` presentó las dependencias raíz sin errores. No se modificó el lockfile ni se suprimió la auditoría. [npm explica el fallback](https://docs.npmjs.com/cli/audit/) y muestra mantenimiento programado para el 2026-09-19 en [su página de estado](https://status.npmjs.org/).

**Actualización 2026-09-20:** `npm audit --omit=optional` local devolvió cero vulnerabilidades; el [segundo intento de CI de `98cb6f9`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35457537980) y la [CI de `a32bc4f`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35533084531) terminaron `success`. Se crearon únicamente Render Free/Static Site en un workspace Hobby nuevo sin tarjeta y Neon Free en N. Virginia. Render sincronizó el Blueprint y desplegó [API](https://api-pulse-api.onrender.com) desde `98cb6f9` y [sitio](https://api-pulse-web.onrender.com) desde `a32bc4f`; este último commit solo cambió frontend/documentación. La primera ejecución de la API falló porque `FRONTEND_ORIGIN` todavía no se había fijado; la segunda quedó Live con CORS correcto. `/health`, `/ready`, cuatro métodos, escenarios 404/500/302, rechazo seguro, 413/422/429, privacidad, recarga y vista móvil aprobaron con datos sintéticos. Tras más de 16 minutos sin tráfico, la web recuperó `Online` en ~14 s, conservó 11 filas de Neon y guardó una nueva; la fecha mostró `Sep` en vez de `sept`. Render mostró USD 0 y cuotas dentro del plan al corte. No se usó la CLI Render; el plan/sync del Dashboard validó semánticamente el Blueprint. **Límites no demostrados:** observar 24 horas de poda real, aislamiento de IP entre visitantes distintos y evento explícito de spin-down. Detalles en [validación T07](VALIDACION_T07.md).

## T08 — Presentación final del portafolio

**Estado: completado en `main` el 2026-09-20.** El usuario indicó «API PULSE» como nombre público del titular. Se creó `LICENSE` MIT con `Copyright (c) 2026 API PULSE`, contrastado con [SPDX](https://spdx.org/licenses/MIT). El README enlaza demo/código/licencia, incluye resumen inglés, recorrido, arquitectura, uso local, controles, límites y evidencia. Se conservaron las fuentes históricas sin presentarlas como actuales.

**Capturas:** `docs/screenshots/dashboard-public.png` (1536×1700, 318 979 bytes) y `dashboard-compact.png` (800×1800, 141 489 bytes) provienen del sitio público, con historial sintético y sin credenciales. Se inspeccionaron visualmente. Una primera captura headless de 390 px salió recortada por el tamaño interno del navegador y se descartó; una observación separada de la página real con viewport 390×844 mostró el contenido ajustado y sin desbordamiento horizontal. No se cambió código de frontend/backend ni se requirió nuevo deploy de Render.

**Comprobaciones T08:** `git diff --cached --check` aprobó; un escaneo de Markdown encontró 11 enlaces relativos y 0 ausentes. El README renderizado y la imagen principal abrieron desde GitHub en la rama y, después del merge `0cb28cf`, desde `main`; GitHub reconoció MIT. Se repitieron localmente pytest (72 passed, 1 skipped, 3 avisos), Ruff, 8 tests frontend, ESLint, build público Vite (18 módulos) y `docker compose config --quiet` (aprobado con aviso de acceso a configuración global Docker). Docker Engine no estuvo disponible para repetir PostgreSQL localmente. La [CI del commit T08](https://github.com/estebanfrm/Api-Pulse/actions/runs/35541101176) y la [CI del merge](https://github.com/estebanfrm/Api-Pulse/actions/runs/35541246577) aprobaron Backend, Frontend, Docker Compose y PostgreSQL smoke. El campo Homepage del repositorio enlaza la demo. No se cambió código de aplicación ni se requirió nuevo deploy de Render.

## T09 — Auditoría de bugs y correcciones

**Estado: correcciones aplicadas en el worktree el 2026-09-20; no desplegadas.** Auditoría sobre `c9685de` que combinó lectura de código, sondas exploratorias contra la aplicación en modo público y local, y verificación de la demo publicada.

### Defectos confirmados y corregidos

| # | Defecto | Evidencia | Corrección |
| --- | --- | --- | --- |
| 1 | `/api/checks/` respondía `307` con `Location: http://…`: degradación de HTTPS a texto plano. `--no-proxy-headers` deja el esquema del origen sin cifrar y Starlette construye con él la redirección de barra final | `curl -i https://api-pulse-api.onrender.com/api/checks/` devolvió `location: http://api-pulse-api.onrender.com/api/checks` | `redirect_slashes=False` en `main.py` y alias `"/"` de las rutas de comprobaciones; `/health/` pasa a `404` en vez de redirigir |
| 2 | El límite de tamaño de la demo comparaba la ruta exacta `/api/checks`, así que no cubría el alias con barra final | Sonda local: cuerpo mayor que `DEMO_MAX_REQUEST_BYTES` sobre `/api/checks/` | El middleware normaliza la barra final antes de comparar |
| 3 | El esquema aceptaba nombres y valores de cabecera con CR/LF: inyección de cabeceras que solo detenía h11 en el socket, con mensaje «Network error» | Sonda local contra un destino controlado con `X-Bad: a
Injected: 1` | `schemas.py` rechaza caracteres de control y no ASCII con 422 y mensaje explícito |
| 4 | Una cabecera con acentos devolvía 200 y «Unexpected request error.», sin indicar la causa | Sonda local con `{"X-Ñ": "ü"}` | Misma validación de esquema del punto 3 |
| 5 | En modo local la URL guardada conservaba `usuario:contraseña@`, y el historial la devolvía en claro | Sonda local: `https://user:SUPERSECRET@example.invalid/x` quedó íntegra en `/api/checks` | `redact_url_credentials` en `security.py` elimina las credenciales antes de persistir; la solicitud sigue usando la URL tal cual |
| 6 | `https://DEMO.API-PULSE.INVALID/echo` se bloqueaba pese a ser equivalente: `netloc` se comparaba respetando mayúsculas | Sonda local contra `validate_demo_url` | Comparación de esquema y `netloc` en minúsculas; la ruta sigue siendo sensible a mayúsculas |
| 7 | El error de validación del formulario se pintaba al final, bajo «Body JSON», mientras el botón «Send» está arriba: al pulsar parecía no ocurrir nada | Demo publicada con `{not json` en «Headers JSON»; el mensaje quedó fuera de pantalla | El mensaje se movió bajo la cabecera del panel, junto al botón, con `role="alert"` |
| 8 | La gráfica mostraba «0 ms avg» junto a una línea con variación, porque los escenarios sintéticos responden en menos de un milisegundo | Demo publicada: 12 puntos de 0–1 ms y promedio redondeado a 0 | `ResponseTimeChart.vue` muestra `<1 ms` cuando el promedio es positivo y menor que 1 |
| 9 | `formatHistoryDate` habría pintado «Invalid Date» ante un valor no interpretable | Revisión de código; `new Date(null)` además devuelve la época en vez de un valor inválido | La función devuelve `N/A` salvo para cadenas o números interpretables |

### Comprobado sin hallazgos

- Protección de destinos en modo local: `localhost`, `127.0.0.1`, `0.0.0.0`, `[::1]`, `[::ffff:127.0.0.1]`, `169.254.169.254`, IP decimal/octal, `file://` y `gopher://` quedaron rechazados y registrados como comprobación fallida.
- Validación de esquema: método no permitido, cuerpo que no es objeto, JSON mal formado, `limit` fuera de rango y falta de `url` responden 422.
- CORS de producción: el preflight desde el origen del sitio devuelve `GET, POST` y `Content-Type` sin credenciales.
- Vista móvil de la demo publicada a 375 px: sin desbordamiento horizontal ni errores de consola.
- El contador de concurrencia del limitador vuelve a cero tras una excepción y la limpieza periódica no deja claves activas huérfanas.

### Comprobaciones ejecutadas

- `pytest -p no:cacheprovider`: 80 aprobados, 1 omitido (smoke de PostgreSQL sin `TEST_POSTGRES_SMOKE`), 1 aviso.
- `ruff check app tests ../tests/integration` y `python -m compileall app tests ../tests/integration`: aprobados.
- `npm test` (9 aprobados), `npm run lint` y `npm run build` (18 módulos): aprobados.
- `docker compose config -q` y `docker compose -p api-pulse-t03 -f compose.integration.yml config --quiet`: aprobados.
- Verificación visual del punto 7 con Vite en el puerto 5199 y `VITE_PUBLIC_DEMO=true`.

### No ejecutado

- No se desplegó nada en Render ni se tocó Neon; la demo pública sigue con el código anterior.
- No se ejecutó el smoke de PostgreSQL con base efímera local.
- No se modificó la política de cuotas por IP: detrás de Render y Cloudflare `request.client.host` es la IP del proxy, de modo que los límites por IP (10/min, 2 concurrentes) actúan como límite compartido más estricto que el global (60/min, 10 concurrentes). Cambiarlo exigiría confiar en `X-Forwarded-For`, lo que contradice `test_spoofed_forwarded_header_does_not_bypass_rate_limit`.
- `/docs` y `/openapi.json` siguen públicos en la API desplegada; no se decidió cerrarlos.

## Historial comprobado con Git

| Commit | Fecha local | Resultado |
| --- | --- | --- |
| `8ce96ee` | 2026-05-20 | MVP inicial |
| `33de381`, merge `4bdd924` | 2026-05-27 | Refinamiento de validación y estados de interfaz, PR #1 |
| `a216136`, merge `29bdc6b` | 2026-05-27 | Herramientas y pruebas, PR #2 |
| `475f513`, merge `7399e86` | 2026-05-28 | Workflow de CI, PR #3 |
| `1f373b4` | 2026-09-19 | Preparación T00–T06 publicada en rama y PR #4 en borrador; no desplegada |
| `ef3fb29`, `a4d6be2` | 2026-09-20 | README/capturas/licencia T08 y cierre documental, CI aprobada |
| Merge `0cb28cf` | 2026-09-20 | PR #4 integrado a `main`; CI de cuatro jobs aprobada |

Estos nombres de fases provienen de commits. La numeración de validaciones del README histórico describe otra secuencia; no debe usarse como prueba de finalización.

## Siguiente punto de entrada

Desplegar manualmente las correcciones de T09 en Render (Blueprint con `autoDeployTrigger: "off"`) y repetir sobre la demo publicada las comprobaciones 1, 3 y 7. No queda un bloque obligatorio T00–T08. Como seguimiento opcional, vigilar cuotas gratuitas, observar la poda tras 24 horas reales, medir aislamiento de cuotas entre visitantes distintos y preparar migraciones explícitas antes de cambios de esquema. No seleccionar servicios pagados ni ampliar la demo a destinos arbitrarios sin una nueva decisión. La aceptación completa está en [el plan](PLAN_DE_CIERRE.md).

## Comprobación de la entrega documental

Se preservó el relevo documental y el README histórico. T01 cambió pruebas y dependencias frontend; T02 cambió la coordinación/presentación de estados y CI; T03 añadió integración; T04 documentó decisiones; T05 añadió modo público acotado; T06 preparó Blueprint, controles de producción, readiness, build cerrado, smoke CI y guía. T07 publicó y verificó la demo; T08 completó presentación/licencia y el PR #4 integró todo a `main`.
