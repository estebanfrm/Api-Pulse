# Plan de cierre: portafolio con despliegue público

**Objetivo confirmado:** demo pública presentable, reproducible y documentada. Los bloques T00–T08 están completados en la rama; falta integrar el PR #4 en `main` y verificar la portada pública predeterminada.

## Secuencia y dependencias

~~~text
T00 Contexto y documentación (completado)
  -> T01 Pruebas y calidad (completado localmente)
  -> T02 Recuperación y claridad de interfaz (completado localmente)
  -> T03 Validación integrada local (completado localmente)
  -> T04 Decisiones de demo y alojamiento (completado)
  -> T05 Controles para exposición pública (completado localmente)
  -> T06 Configuración de producción (preparada localmente)
  -> T07 Despliegue y verificación (completado con límites documentados)
  -> T08 Presentación final del portafolio (contenido y CI aprobados; integración a main pendiente)
~~~

T04 puede prepararse durante T01–T03. T05/T06 dependen de sus decisiones; T07 requiere la preparación técnica de ambas.

## T00 — Organizar el relevo

**Estado: completado en esta tarea.**

Documentación indexada, requisitos, decisiones, arquitectura, API, desarrollo, plan y prompt para GPT-5.6. README anterior preservado; baseline local identificado.

T01 se ejecutó desde un worktree correcto de `api-pulse`. La ruta histórica `nwep` no debe recrearse ni usarse como repositorio vacío.

## T01 — Cerrar las pruebas incompletas y obtener una base de calidad

**Estado: completado localmente el 2026-09-15.** Requisitos RF01–RF06/RF09/RP07.

- Completar los tres casos de errores de httpx y el caso de DNS no resoluble que hoy no ejecutan ninguna comprobación.
- Asegurar que el test de redirecciones verifica la opción capturada, no solo la almacena.
- Cubrir contratos relevantes sin cobertura: respuesta 4xx/5xx, GET sin body, resumen recortado, límites del historial y fallo DNS.
- Considerar entradas de URL malformadas y resoluciones mixtas públicas/privadas al completar los casos de seguridad.
- Ejecutar pytest, Ruff, instalación reproducible, build y lint de frontend; revisar auditorías y CI del commit evaluado.

**Aceptación:** pruebas llaman al código real con mocks y comprueban resultados; sin red externa; todos los controles ejecutados con resultados registrados. Si alguno no puede ejecutarse, permanece explícitamente pendiente. No convertir un simple número de tests en prueba de calidad.

**Resultado:** tres casos de errores httpx y el caso DNS no resoluble quedaron reparados. También se comprobaron redirecciones desactivadas, 404/500 como respuestas recibidas, GET sin body, truncamiento, orden y límites del historial, y DNS mixto público/privado. `pytest` aprobó 40 casos; Ruff, compilación, Compose config, `npm ci`, build y lint aprobaron. La auditoría inicial encontró cinco vulnerabilidades; se actualizaron Vite 6.4.2 → 6.4.3 y cuatro transitivas dentro de sus rangos compatibles. La instalación limpia y `npm audit --omit=optional` finalizaron con cero vulnerabilidades. No hubo cambios de código de aplicación. Evidencia detallada en [estado actual](ESTADO_ACTUAL.md#t01--pruebas-y-calidad).

**Archivos:** `backend/tests/`, aplicación solo si una prueba demuestra un defecto.
**Entrega:** cambio acotado a `backend/tests/test_api_client.py`, `test_security.py`, `test_checks_api.py`, `frontend/package.json`, `frontend/package-lock.json` y documentación de seguimiento, sobre la base `7399e86`, todavía sin commit.

## T02 — Corregir recuperación y claridad de la interfaz

**Estado: completado localmente el 2026-09-15.** RF04/RF08/RP09.

- Separar fallo de historial de fallo al enviar una solicitud.
- Mostrar estados offline/error/reintento sin quedarse en Checking indefinidamente.
- Mantener visible una respuesta obtenida aunque falle su recarga del historial.
- Aclarar que una respuesta HTTP recibida puede ser 4xx/5xx.
- Revisar estados vacíos, navegación con teclado y móvil.

**Aceptación:** reproducir backend inaccesible, historial inaccesible y recuperación; evitar rechazos de promesas sin manejar; resultado no perdido; comportamiento verificado en navegador y con pruebas pertinentes.

**Resultado:** los estados de salud, solicitud e historial quedaron separados en un composable comprobable. La carga inicial y los reintentos absorben fallos esperados; una respuesta ya recibida y el historial previo permanecen visibles si falla la recarga. La interfaz distingue una respuesta HTTP 4xx/5xx de un fallo sin respuesta. Cuatro pruebas automatizadas aprobaron. En navegador se comprobó caída inicial, recuperación a Online, respuesta 500 conservada durante un 503 de historial, reintento por teclado, vista móvil y consola sin errores, usando únicamente un servidor simulado local.

**Archivos:** `App.vue`, `composables/useApiDashboard.js`, componentes de resultado/historial, estilos, pruebas y workflow de calidad.

## T03 — Validar el flujo integrado local

**Estado: completado localmente el 2026-09-15.** RF01–RF09.

- Levantar stack aislado con puertos disponibles.
- Probar health, GET público autorizado y métodos restantes contra un destino de prueba propio.
- Verificar rechazo local/privado, errores de formato, resultado 4xx/5xx y persistencia tras recarga/reinicio sin borrar volumen.
- Comprobar tabla, gráfica y orden de fechas.

**Aceptación:** comandos y resultados documentados, base PostgreSQL real, capturas representativas y pruebas de navegador proporcionales. Un error provocado no modifica servicios ajenos.

**Resultado:** se añadió `compose.integration.yml` con puertos alternativos, volumen propio, PostgreSQL 16 y un destino HTTP controlado sin puerto de host. Aprobaron health, GET/POST/PUT/DELETE con eco, 404/500 como respuestas recibidas, 302 sin seguimiento, localhost bloqueado, PATCH y límite 101 con 422, orden descendente y límites del historial. Diez registros UTC sobrevivieron al reinicio del stack y a la recarga del navegador. La UI mostró resultado, errores, gráfica y tabla; la consola no registró errores ni advertencias. No se enviaron métodos mutables a servicios públicos.

**Archivos:** `compose.integration.yml`, `tests/integration/controlled_target.py` y documentación de ejecución/evidencia.

## T04 — Resolver el modo público

**Estado: completado el 2026-09-19. D08–D12 confirmadas; implementación pendiente en T05–T08.**

Preparar una propuesta concreta sobre:

- Modo de demo, destinos, métodos y acceso.
- Plataforma, presupuesto, dominio, región y persistencia.
- Historial, redacción de datos y retención.
- Idioma final y licencia.

**Aceptación:** decisiones registradas con fuente de aprobación y consecuencias. Propuesta inicial: demo de portafolio con ejemplos/destinos acotados; no está aprobada aún. Verificar capacidades y costes actuales del proveedor al comparar.

**Resultado:** la [propuesta T04](PROPUESTA_T04.md) comparó opciones verificadas. El usuario aprobó D09 el 2026-09-15: frontend y backend Render Free, PostgreSQL Neon Free, Virginia y subdominios gratuitos con presupuesto USD 0. El 2026-09-19 aprobó D08 (demo pública anónima con destinos controlados y cuatro métodos), D10 (historial compartido 24 h/500 registros con datos mínimos), D11 (interfaz inglesa) y D12 (MIT). Las aprobaciones y consecuencias están registradas en [decisiones](DECISIONES.md). El nombre exacto del titular para `LICENSE` se solicitará en T08; no bloquea los controles de T05. No hubo gasto, recursos creados ni despliegue. El plan Render pagado sigue sin autorización.

## T05 — Preparar la API para exposición pública

**Estado: completado localmente el 2026-09-19; verificación en el dominio público pendiente para T07.** RF09/RP02–RP04.

- Asegurar el destino efectivo de conexión, además de validar DNS.
- Establecer límites de solicitudes, concurrencia, tiempo y bytes leídos, conforme a D08.
- Mantener bloqueo de redes internas y redirecciones.
- Implementar acceso/aislamiento de historial, redacción y retención según D10.
- Reducir detalle sensible en errores devueltos; comprobar configuración de proxies/salidas del entorno elegido.

**Aceptación local:** casos de pruebas de cada límite y ruta de rechazo, destinos de prueba controlados y valores documentados. La comprobación de los mismos controles en el entorno público corresponde a T07; no se declara aprobada anticipadamente.

**Resultado:** el modo público usa exclusivamente cuatro escenarios sintéticos por `httpx.MockTransport`, sin resolución DNS ni socket hacia hosts del visitante. Admite GET/POST/PUT/DELETE y conserva `success=true` para 404/500 y 302 sin seguimiento. URL fuera del catálogo se registra como rechazo seguro; el cuerpo de entrada tiene tope de 16 KiB (413), la respuesta de 64 KiB, timeout configurado de 8 s y cuotas en memoria por IP de 10/minuto y 2 concurrentes, más 60/minuto y 10 concurrentes globales (429). El historial compartido guarda solo URL canónica, método, estado, tiempo, resumen seguro y error genérico; poda filas de más de 24 h, filas heredadas no reconocidas y exceso sobre 500 al iniciar, crear o listar. El frontend público presenta un selector y aviso de privacidad; el Compose local/integrado conserva el modo anterior explícitamente. Se aprobaron 62 tests backend, Ruff, 5 tests frontend, lint, build y validación sintáctica de ambos Compose. Docker Engine no estaba disponible para repetir PostgreSQL o navegador en este bloque; Neon, proxy y cuotas con tráfico real quedan para T06/T07. La preparación se guardó después en el commit local `1f373b4` durante T07.

## T06 — Construir configuración reproducible de producción

**Estado: preparada localmente el 2026-09-19; validación real del Blueprint, PostgreSQL CI y Neon/Render pendientes para T07.** RP01/RP05–RP07.

- Servir frontend compilado; configurar URL pública del backend en el build.
- Backend con secretos/configuración externa y orígenes explícitos.
- Base de datos privada, persistencia y estrategia de migración acordes al despliegue.
- Conectar Neon mediante URL TLS agrupada y tolerar su suspensión por inactividad sin exponer credenciales.
- Health/readiness apropiados, logs y recuperación de datos de demo.
- Presentar el arranque en frío de Render Free como estado recuperable, sin pings artificiales para eludir cuotas.
- Automatizar build y verificaciones con la base elegida; documentar despliegue y rollback.

**Aceptación:** se puede crear el entorno siguiendo el procedimiento; no requiere credenciales en Git ni publicar el puerto de PostgreSQL; smoke test válido y recuperación descrita.

**Resultado local:** `render.yaml` define frontend estático Vite y backend FastAPI Free en Virginia, un worker, URLs HTTPS entre servicios y `DATABASE_URL` como secreto externo para Neon. El build público falla sin URL de API HTTPS; el backend en Render falla si no está en modo producción, y producción exige demo controlada, origen HTTPS único y URL Neon agrupada con TLS/channel binding. CORS público queda restringido. `/health` no consulta la base; `/ready` sí lo hace con error genérico. El pool recicla conexiones para tolerar suspensión. Se documentaron creación, cuotas, smoke, recuperación de base vacía y rollback sin borrar datos. CI añade smoke sobre PostgreSQL 16 efímero, pero no se pudo ejecutarlo localmente porque Docker Engine no estuvo disponible; tampoco se ejecutó la CI remota ni el validador semántico de Render. Pasaron 72 pruebas backend (1 smoke PostgreSQL omitido), Ruff, 7 frontend, lint, build público, CORS de producción en proceso aislado y parseo YAML local. T07 debe ejecutar el smoke real y comprobar Neon/proxy antes de considerar satisfecha la aceptación externa.

## T07 — Publicar y comprobar

**Estado: completado el 2026-09-20 con límites documentados.** RP01/RP03/RP05–RP07/RP09.

Publicar cuando las decisiones y condiciones de T04–T06 estén resueltas. Si una acción exige autorización adicional, preparar primero el resultado concreto que se va a publicar.

**Aceptación:** URL HTTPS real accesible; flujo completo, CORS y límites funcionando desde el dominio final; historial correcto según política; CI del commit publicado comprobada; registro de versión, fecha y rollback. En el plan gratuito, comprobar además una visita después de al menos 15 minutos de inactividad, recuperación del backend/Neon y consumo dentro de cuotas. No cerrar con una URL supuesta o únicamente localhost.

**Resultado:** `main` público seguía en `7399e86`; se creó y publicó `codex/api-pulse-t07-publication` con `1f373b4` de T00–T06 y el [PR #4 en borrador](https://github.com/estebanfrm/Api-Pulse/pull/4). El primer run de CI falló solo en auditoría por respuestas 503/400 de npm; la auditoría local posterior encontró cero vulnerabilidades, el [reintento completo de `98cb6f9`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35457537980) y la [CI de `a32bc4f`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35533084531) aprobaron. Se creó Neon Free en N. Virginia y un workspace Render Hobby aislado sin tarjeta, con API Free en Virginia y sitio estático. API `98cb6f9` y frontend `a32bc4f` quedaron Live. Las URL HTTPS, Neon, CORS, métodos, límites, privacidad, historial tras recarga y vista móvil se comprobaron con datos sintéticos. Tras más de 16 minutos sin tráfico, el sitio recuperó `Online`, mantuvo 11 filas y guardó la 12; la fecha se mostró en inglés. El panel Render mostraba USD 0 y uso dentro de cuotas. La primera ejecución backend falló por orden de creación de `FRONTEND_ORIGIN`, pero la siguiente quedó Live. [Validación T07](VALIDACION_T07.md) registra comandos, versiones, rollback y límites: no se observó la poda durante 24 horas ni un evento explícito de suspensión, y la cuota por IP no se midió desde visitantes distintos.

## T08 — Cerrar presentación y relevo final

**Estado: contenido y comprobaciones completados en la rama el 2026-09-20; integración a `main` pendiente.** RP08/RP10.

- README con enlaces reales a demo y repositorio.
- Capturas actuales y explicación breve del problema, recorrido y decisiones técnicas.
- Licencia elegida y límites de la demo documentados.
- Actualizar estado/decisiones; archivar documentación que ya no sea vigente.
- Registrar evidencia y mejoras opcionales fuera del alcance.

**Aceptación:** un visitante entiende el proyecto y puede evaluarlo desde el README sin leer conversaciones de desarrollo.

**Resultado en rama:** el usuario indicó «API PULSE» como titular público; `LICENSE` MIT, README con enlaces reales y resumen inglés, dos capturas actuales, límites y actualización de documentos están preparados. Los 11 enlaces relativos del README existen y su render/imágenes se comprobaron en GitHub; la [CI de `ef3fb29`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35540890598) aprobó los cuatro jobs. No se modificó la aplicación ni se requieren recursos pagados. Falta integrar el PR y verificar la portada predeterminada.

## Criterios para dar el proyecto por terminado

- [x] Requisitos funcionales del alcance elegidos y comprobados para la demo pública.
- [x] Pruebas incompletas reparadas y controles locales de calidad aprobados.
- [x] Decisiones de alojamiento, modo de demo y datos cerradas.
- [x] Controles de solicitudes salientes y acceso implementados localmente y comprobados en la demo pública; falta medir aislamiento entre visitantes distintos tras proxy.
- [x] URL pública HTTPS y versiones desplegadas verificadas: API `98cb6f9`, sitio `a32bc4f` con fechas inglesas.
- [x] Persistencia y recuperación de demo comprobadas sobre Neon tras inactividad; retención 24 h/500 cubierta por pruebas, no observada durante 24 h reales.
- [x] Flujo móvil/escritorio y recuperación tras inactividad validados; límites de la observación en T07.
- [x] README final, capturas, licencia MIT y documentación preparados y comprobados en la rama; integración a `main` pendiente.
- [x] Limitaciones y siguientes mejoras registradas sin pendientes críticos del alcance público elegido.

## Cómo cerrar una tarea

Registrar fecha, commit, archivos, requisito, comprobación ejecutada y resultado. Usar estados pendiente/en curso/completado/bloqueado con motivo. Actualizar [estado](ESTADO_ACTUAL.md) y [relevo](CONTINUIDAD_GPT_5_6.md) después de cada entrega.
