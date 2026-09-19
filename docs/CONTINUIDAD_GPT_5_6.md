# Continuidad con GPT-5.6

## Resumen para retomar

**API Pulse:** probador manual de APIs HTTP, con Vue 3/Vite, FastAPI/httpx y PostgreSQL. Objetivo confirmado por el usuario: **proyecto de portafolio con despliegue público**.

Base revisada: commit `7399e86`, worktree en `HEAD` separado, corte 2026-09-19. El MVP existe y T01–T05 quedaron completados localmente; T06 quedó preparado localmente con validación externa pendiente. D08–D12 están confirmadas: demo acotada, Render Free + Neon Free (USD 0 inicial), historial compartido 24 h/500 registros, interfaz inglesa y MIT. El titular para `LICENSE` se pedirá en T08. Publicación, CI del commit y verificación pública siguen pendientes. Los cambios continúan sin commit y no se ejecutó un despliegue.

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

## Primera tarea concreta

**T07: publicar y verificar.** Revisar/guardar los cambios en un commit, comprobar la CI incluida la prueba PostgreSQL, validar y sincronizar `render.yaml`, crear Neon Free solo tras confirmar cuotas/precio vigente y ejecutar el smoke con URL reales. Verificar CORS, cuota tras proxy, persistencia, historial y arranque en frío; sin pings artificiales ni gasto pagado no autorizado. El nombre MIT se pide en T08.

## Lo que debe recordarse

- `success` significa respuesta HTTP recibida; un 404/500 también lo cumple.
- La API de creación puede devolver 200 con `check.success=false`.
- La validación DNS del modo local ocurre antes de httpx; no fija el destino de conexión. No desplegar ese modo. El modo público usa respuestas sintéticas sin egress a destinos arbitrarios.
- El resumen local de 2000 caracteres no limita el cuerpo descargado. En público la respuesta sintética tiene tope y no llama a Internet.
- La demo pública sigue anónima; sus cuotas viven en memoria de un proceso. La retención se aplica al iniciar, crear y listar, no por job continuo.
- Docker frontend ejecuta Vite dev; producción usa Render Static Site y build `dist`.
- La integración con PostgreSQL real quedó comprobada en T03. T06 agregó un job CI PostgreSQL 16, sin ejecución remota aún.
- `compose.integration.yml` y su subred sintética son solo para pruebas, no para producción.
- Proveedor, acceso, historial, idioma y licencia MIT están confirmados; T05/T06 implementaron controles/configuración locales, falta publicación y verificación externa. USD 0 no es garantía si se superan cuotas con método de pago; vigilar uso.
- El titular exacto de `LICENSE` no se ha recibido; pedirlo en T08, sin inventarlo desde GitHub.
- Render pagado por USD 13,30/mes es solo una alternativa futura y no está autorizado.
- T07 debe comprobar arranque en frío y cuotas sin usar pings artificiales para mantener servicios gratuitos activos.
- La auditoría frontend quedó en cero tras actualizar Vite y cuatro transitivas; conservar el manifiesto y lockfile juntos.

## Prompt listo para pegar

~~~text
Continúa API Pulse desde este repositorio. Quiero terminarlo como proyecto
de portafolio con despliegue público, trabajando con GPT-5.6.

Lee AGENTS.md, docs/CONTINUIDAD_GPT_5_6.md, docs/ESTADO_ACTUAL.md y
docs/PLAN_DE_CIERRE.md. Comprueba la ruta real y git status. Usa el código
como evidencia del comportamiento actual y distingue las decisiones
confirmadas de las propuestas.

T01–T05 están completados localmente y T06 está preparado con verificación
externa pendiente. D08–D12 están confirmadas; ver docs/DECISIONES.md.
Empieza por T07: revisa el commit, comprueba CI (incluido smoke PostgreSQL),
valida/sincroniza render.yaml y sigue docs/DESPLIEGUE_RENDER_NEON.md para
crear los recursos gratuitos y verificar las URL reales, Neon, CORS,
cuotas/proxy, historial y arranque en frío. MIT está elegida, pero el nombre
del titular se pedirá en T08 antes de crear LICENSE.

Conserva los cambios locales de T00–T06, el manifiesto/lockfile actualizado y
los contratos descritos. La auditoría frontend quedó en cero. Actualiza estado,
plan y decisiones afectadas, y deja la siguiente tarea concreta. No declares
desplegada ni verificada públicamente la aplicación sin comprobar T07.
~~~

## Cómo mantener el relevo

Al cerrar cada bloque, actualizar base/fecha, trabajo completado, resultados de validación, decisiones nuevas y primera tarea pendiente. Mantener este documento breve; los contratos y comandos completos viven en los documentos enlazados.
