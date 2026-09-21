# Continuidad con GPT-5.6

## Resumen para retomar

**API Pulse:** probador manual de APIs HTTP, con Vue 3/Vite, FastAPI/httpx y PostgreSQL. Objetivo confirmado por el usuario: **proyecto de portafolio con despliegue público**.

Base inicial `7399e86`; corte 2026-09-20. T00–T08 quedaron integrados en `main` mediante el [PR #4](https://github.com/estebanfrm/Api-Pulse/pull/4), merge `0cb28cf`, con [CI final verde](https://github.com/estebanfrm/Api-Pulse/actions/runs/35541246577). D08–D12 están confirmadas: demo acotada, Render Free + Neon Free (USD 0 inicial), historial compartido 24 h/500 registros, interfaz inglesa y MIT. T07 publicó [sitio](https://api-pulse-web.onrender.com) desde `a32bc4f` y [API](https://api-pulse-api.onrender.com) desde `98cb6f9`; ver [validación T07](VALIDACION_T07.md). T08 llevó README, capturas y `LICENSE` con el titular público «API PULSE» a la portada predeterminada de GitHub.

## Antes de iniciar

Trabaja en un checkout o worktree del repositorio `api-pulse`. La ruta histórica `C:\Users\giral\OneDrive\Documentos\Esteban\nwep` es inexistente y no debe recrearse. T01 se ejecutó en `C:\Users\giral\.codex\worktrees\7c72\api-pulse`.

Selecciona GPT-5.6 en la aplicación. Si se ofrece la variante Sol, esa es la familia a la que corresponde el alias GPT-5.6 en la documentación de OpenAI. Este documento no cambia el modelo seleccionado ni la configuración de Codex. [Referencia oficial](https://developers.openai.com/api/docs/models/gpt-5.6-sol).

`AGENTS.md` concentra instrucciones del repositorio para que Codex las encuentre al trabajar en la carpeta correcta. [Guía oficial de AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Lectura mínima

1. [Estado actual](ESTADO_ACTUAL.md): evidencia y problemas.
2. [Plan de cierre](PLAN_DE_CIERRE.md): secuencia y aceptación.
3. [Decisiones](DECISIONES.md): diferenciar acuerdo, observación y propuesta.

Para implementar: [API](API.md), [arquitectura](ARQUITECTURA.md), [requisitos](REQUISITOS.md) y [comandos](DESARROLLO_Y_VALIDACION.md).

## T01, T02 y T03 completados

- Se repararon los tres casos parametrizados de errores httpx y el caso DNS no resoluble.
- Se añadieron comprobaciones de `follow_redirects=False`, 404/500 con `success=true`, GET sin body, resumen recortado, límites y orden del historial, y DNS mixto público/privado.
- `pytest`: 40 passed con tres avisos de deprecación. Ruff y compilación Python: aprobados.
- Compose config, `npm ci`, build, lint y `npm audit --omit=optional`: aprobados; auditoría final con cero vulnerabilidades.
- Se actualizó Vite 6.4.2 → 6.4.3 y cuatro dependencias transitivas compatibles en el lockfile. No se modificaron código de aplicación ni contratos; no hubo tráfico HTTP externo en pruebas.
- Se separaron los estados de solicitud, historial y salud; la interfaz ya sale de `Checking`, permite reintentar y conserva el resultado/historial anterior ante fallos de recarga.
- Las etiquetas distinguen `Response received` de `No response`; un 4xx/5xx mantiene su código y se explica como respuesta HTTP recibida.
- Cuatro pruebas frontend comprueban caída, conservación y recuperación. La validación controlada en navegador cubrió caída inicial, recuperación, HTTP 500, historial 503, reintento por teclado y vista móvil, sin errores de consola.
- El workflow de CI se amplió para ejecutar `npm test`; T03 comprobó por separado el stack real con PostgreSQL.
- Se añadió un stack de integración aislado con PostgreSQL 16 y un destino HTTP controlado, sin puertos públicos ni métodos mutables contra servicios ajenos.
- Aprobaron GET/POST/PUT/DELETE, 404/500/302, bloqueo local, validaciones 422, orden/límites, gráfica y fechas. Diez registros sobrevivieron al reinicio del stack y a la recarga del navegador; consola limpia.

## T05 completado localmente

El modo público usa cuatro escenarios sintéticos con `MockTransport`, sin DNS ni socket hacia destinos arbitrarios. Tiene cuotas por IP/global, límites de bytes, timeout configurado, errores genéricos, historial compartido redactado con poda de 24 h/500 filas y selector frontend. El modo local se conserva en los Compose. Aprobaron 62 tests backend, Ruff, 5 frontend, lint/build y Compose config. Docker Engine no estuvo disponible para repetir PostgreSQL; Neon y dominio final no se probaron. Ver [estado T05](ESTADO_ACTUAL.md#t05--controles-de-exposición-pública).

## T06 preparado localmente

`render.yaml` declara frontend estático y backend Python Free, ambos con despliegue automático apagado. URLs públicas cruzadas alimentan Vite/CORS; Neon se suministra como secreto pooled con TLS/channel binding. Producción falla si usa el modo local, origen HTTP o URL DB insegura. `/health` es liveness sin base; `/ready` comprueba PostgreSQL. La CI añade smoke PostgreSQL efímero. Aprobaron 72 pruebas backend (1 smoke omitido), Ruff, 7 frontend, lint, build público, CORS de producción y parseo YAML. Docker Engine no estuvo disponible para ejecutar el smoke PostgreSQL, y Render/Neon no se han creado. Ver [estado T06](ESTADO_ACTUAL.md#t06--configuración-reproducible-de-producción) y [guía](DESPLIEGUE_RENDER_NEON.md).

## T07 desplegado y verificado

Al cierre de T07, `main` seguía en `7399e86` y el PR #4 estaba en borrador; después se integró en T08. La auditoría npm local devolvió cero vulnerabilidades; el [reintento de CI de `98cb6f9`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35457537980) y la [CI de `a32bc4f`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35533084531) aprobaron Backend, PostgreSQL smoke, Compose y Frontend. Render sincronizó semánticamente el Blueprint y desplegó API Free/Static Site en un workspace Hobby nuevo sin tarjeta; Neon Free usa PostgreSQL 16 en N. Virginia. La primera ejecución API falló porque `FRONTEND_ORIGIN` todavía no estaba listo; el segundo deploy quedó Live. `/health`, `/ready`, cuatro métodos, escenarios de error/redirección, CORS, 413/422/429, privacidad, historial tras recarga y vista móvil aprobaron en las URL reales. Tras más de 16 minutos sin tráfico, la web recuperó `Online`, preservó 11 filas y guardó la 12; el frontend `a32bc4f` mostró `Sep` en el navegador español. Render mostraba USD 0 y cuotas dentro del plan. Ver [evidencia y límites T07](VALIDACION_T07.md).

## T09 — Auditoría de bugs

Auditoría sobre `c9685de` con lectura de código, sondas exploratorias y verificación de la demo publicada. Nueve defectos confirmados y corregidos en el worktree: redirección de barra final que degradaba HTTPS a `http://`, límite de tamaño que no cubría esa ruta, cabeceras con CR/LF o no ASCII aceptadas por el esquema, credenciales de URL persistidas en modo local, host de demo sensible a mayúsculas, error de formulario pintado fuera de pantalla, promedio «0 ms avg», fechas no interpretables y `on_event` deprecado. Aprobaron 80 pruebas backend (1 omitida), Ruff, compileall, 9 frontend, lint, build y ambos Compose. **Nada de esto está desplegado:** Render mantiene `autoDeployTrigger: "off"`. Ver [estado T09](ESTADO_ACTUAL.md#t09--auditoría-de-bugs-y-correcciones).

## T10 — Segunda pasada de auditoría

Concurrencia, fuzzing y cadena de suministro. Siete defectos más corregidos: dos excepciones no controladas que devolvían HTTP 500 en modo local (`socket.getaddrinfo` lanza `UnicodeError` con etiquetas DNS vacías o de más de 63 caracteres; `urlsplit` lanza `ValueError` con una autoridad malformada como `http://[`), cuatro condiciones de carrera del frontend por respuestas fuera de orden —la más visible dejaba la insignia en **Offline** con el backend disponible tras pulsar «Retry connection» durante un arranque en frío— y un workflow de CI sin `permissions`. El fuzzing de 25 760 combinaciones quedó en cero respuestas 5xx. `starlette==0.41.3`, anclada por `fastapi==0.115.6`, arrastra siete avisos GHSA (tres HIGH): se comprobó uno por uno que **ninguno es explotable aquí**, y que `fastapi==0.141.1` los cierra con las 89 pruebas en verde; la actualización está propuesta, no aplicada. Ver [estado T10](ESTADO_ACTUAL.md#t10--segunda-pasada-concurrencia-fuzzing-y-dependencias).

## Siguiente acción si se retoma

**Pendiente concreto:** decidir la actualización de FastAPI propuesta en T10 y desplegar manualmente en Render las correcciones de T09 y T10 y repetir contra la demo publicada la comprobación de `/api/checks/`, las cabeceras rechazadas con 422 y la visibilidad del error del formulario. Después, si el usuario solicita seguimiento, comprobar cuotas gratuitas y observar la poda de 24 horas en Neon; más adelante, medir la separación de cuotas entre visitantes detrás del proxy y añadir migraciones explícitas antes de cambiar columnas. No habilitar destinos arbitrarios ni servicios pagados sin decisión nueva.

## Lo que debe recordarse

- `success` significa respuesta HTTP recibida; un 404/500 también lo cumple.
- La API de creación puede devolver 200 con `check.success=false`.
- La validación DNS del modo local ocurre antes de httpx; no fija el destino de conexión. No desplegar ese modo. El modo público usa respuestas sintéticas sin egress a destinos arbitrarios.
- El resumen local de 2000 caracteres no limita el cuerpo descargado. En público la respuesta sintética tiene tope y no llama a Internet.
- La demo pública sigue anónima; sus cuotas viven en memoria de un proceso. La retención se aplica al iniciar, crear y listar, no por job continuo.
- Docker frontend ejecuta Vite dev; producción usa Render Static Site y build `dist`.
- La integración con PostgreSQL real quedó comprobada en T03. El job CI PostgreSQL 16 de T06 aprobó en el primer run del PR #4; aún no prueba Neon.
- `compose.integration.yml` y su subred sintética son solo para pruebas, no para producción.
- Proveedor, acceso, historial, idioma y licencia MIT están confirmados; T05/T06 implementaron controles/configuración y T07 desplegó la demo pública. El workspace Render exclusivo no tiene tarjeta; al agotar cuotas puede suspenderse. Vigilar uso.
- El usuario indicó «API PULSE» como nombre público del titular; `LICENSE` MIT ya está en `main`. No sustituirlo por el usuario de GitHub.
- Render pagado por USD 13,30/mes es solo una alternativa futura y no está autorizado.
- T07 comprobó una visita tras más de 16 minutos sin tráfico, sin pings artificiales. No hubo evento independiente de Render que demuestre si la instancia llegó a suspenderse; las cuotas visibles estaban dentro del plan.
- La auditoría frontend quedó en cero tras actualizar Vite y cuatro transitivas; conservar el manifiesto y lockfile juntos.

## Prompt listo para pegar

~~~text
Continúa API Pulse desde este repositorio con GPT-5.6 si solicito una mejora
o seguimiento. El cierre de portafolio público T00–T08 ya está completado.

Lee AGENTS.md, docs/CONTINUIDAD_GPT_5_6.md, docs/ESTADO_ACTUAL.md y
docs/PLAN_DE_CIERRE.md. Comprueba la ruta real y git status. Usa el código
como evidencia del comportamiento actual y distingue las decisiones
confirmadas de las propuestas.

T00–T08 están completados con evidencia/limitaciones en docs/ESTADO_ACTUAL.md.
El PR #4 se integró en main como 0cb28cf y su CI aprobó. La demo vive en
api-pulse-web.onrender.com y la API en api-pulse-api.onrender.com, usando
Render/Neon Free. Lee docs/VALIDACION_T07.md antes de cambiar producción.
El titular público de LICENSE MIT es «API PULSE», indicado por el usuario.

Conserva los contratos y la distinción entre modo público acotado y modo local.
No confundas la versión de API `98cb6f9` con la del sitio `a32bc4f`;
T08 solo cambió documentación y capturas. Si hay una nueva tarea, actualiza
estado, plan y decisiones afectadas y deja una siguiente acción concreta.
~~~

## Cómo mantener el relevo

Al cerrar cada bloque, actualizar base/fecha, trabajo completado, resultados de validación, decisiones nuevas y primera tarea pendiente. Mantener este documento breve; los contratos y comandos completos viven en los documentos enlazados.
