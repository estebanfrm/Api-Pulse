# T07 — Validación del despliegue público

**Corte:** 2026-09-20, America/Bogota. **Estado:** T07 completado con limitaciones explícitas; T08 sigue pendiente.

## Recursos y versión observados

- Sitio: [https://api-pulse-web.onrender.com](https://api-pulse-web.onrender.com), Render Static Site.
- API: [https://api-pulse-api.onrender.com](https://api-pulse-api.onrender.com), Render Web Service **Free** en Virginia.
- Base: proyecto nuevo `api-pulse-demo`, Neon **Free**, PostgreSQL 16 en AWS US East 1 (N. Virginia), base vacía dedicada `api_pulse`. Solo el backend recibió la conexión agrupada con TLS y `channel_binding=require` como secreto `DATABASE_URL`; no se registró su valor en Git o en este documento.
- Se creó un workspace Render exclusivo `API Pulse`, plan Hobby, **sin método de pago**. No se seleccionaron servicios pagados ni Render Postgres. Render suspende servicios/builds al agotar cuotas en un workspace sin tarjeta, según su [documentación de Free](https://render.com/docs/free). El uso debe supervisarse; presupuesto inicial USD 0 no equivale a disponibilidad garantizada.
- Blueprint de la rama `codex/api-pulse-t07-publication` sincronizado inicialmente por Render desde `98cb6f9dd012a43974ba2bf844d9875ff169abb8`. La API sigue Live en ese commit; el frontend se desplegó manualmente desde `a32bc4f4470ccfc2bfc190b3921542a0bfafcf4c` y quedó Live. El cambio posterior no tocó backend. `main` seguía en `7399e86` antes del despliegue; PR #4 continúa en borrador.
- Rollback del código: volver al deploy anterior compatible de **ambos** servicios en Render y conservar Neon. No borrar la base ni el proyecto; `create_all` no ejecuta migraciones de columnas. El frontend dispone de los deploys funcionales `98cb6f9` y `a32bc4f`; para la API solo se observó como funcional `98cb6f9`. No declarar un rollback probado.

## Calidad y despliegue

- Comandos locales ejecutados en `frontend/`: `node 'C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js' audit --omit=optional` (0 vulnerabilidades), `node --test` (8 aprobadas tras el ajuste), `node node_modules/eslint/bin/eslint.js .` (aprobado) y `node node_modules/vite/bin/vite.js build` con `RENDER=true`, `VITE_PUBLIC_DEMO=true` y `VITE_API_BASE_URL=https://api-pulse-api.onrender.com` (aprobado, 18 módulos). El shim global de npm sigue roto; no se ocultó con cambios de dependencias.
- El 2026-09-20, `npm audit --omit=optional` local devolvió **0 vulnerabilidades**. Se reintentaron los jobs fallidos de la [CI del commit `98cb6f9`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35457537980): intento 2, estado `completed`, conclusión `success`. La CI incluye Backend, smoke PostgreSQL 16, Compose y Frontend. El fallo inicial de auditoría del 2026-09-19 se conserva en [estado actual](ESTADO_ACTUAL.md#t07--publicación-y-verificación); no se modificaron dependencias para eludirlo.
- Render aceptó semánticamente `render.yaml` al planificar/sincronizar el Blueprint. La primera ejecución del backend falló porque `FRONTEND_ORIGIN` aún no se había creado durante la sincronización inicial; Render programó un segundo deploy tras configurar la referencia cruzada. Ese segundo deploy quedó **Live**. El frontend compiló y quedó **Live**. `FRONTEND_ORIGIN` se observó como `https://api-pulse-web.onrender.com` y `VITE_API_BASE_URL` como `https://api-pulse-api.onrender.com`.
- La comprobación local del ajuste de fecha inglesa aprobó 8 pruebas frontend, ESLint y build público Vite de 18 módulos. La [CI de `a32bc4f`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35533084531) terminó `success` con Frontend, Backend, PostgreSQL smoke y Docker Compose aprobados; el Static Site se observó `Deploy succeeded | Live` en ese commit.
- Tras el smoke, el panel del workspace Render mostraba plan Hobby sin tarjeta, 0,37/750 horas de instancia Free, 1/500 minutos de build, ancho de banda redondeado a 0 MB, cargo acumulado y proyección mensual de **USD 0**. El panel de Neon mantenía plan Free y métricas redondeadas a 0; advierte que pueden retrasarse una hora. Es una observación puntual, no una garantía futura de consumo o disponibilidad.

## Smoke público con datos sintéticos

Comandos base ejecutados con las URL observadas: `Invoke-RestMethod 'https://api-pulse-api.onrender.com/health'`, `Invoke-RestMethod 'https://api-pulse-api.onrender.com/ready'` y `Invoke-RestMethod 'https://api-pulse-api.onrender.com/api/checks?limit=50'`. Los checks POST se enviaron a `/api/checks` con `Invoke-WebRequest -Method Post -ContentType 'application/json' -Body $payload -SkipHttpErrorCheck`; `$payload` contenía solo métodos y URLs de escenarios sintéticos. Para CORS se usó `-Method Options` y cabeceras `Origin`, `Access-Control-Request-Method` y `Access-Control-Request-Headers`. No se usaron APIs públicas ajenas para métodos mutables.

| Comprobación | Resultado observado |
| --- | --- |
| `GET /health` y `GET /ready` | 200, `ok` y `ready`; confirma proceso y consulta a Neon |
| Interfaz en navegador | `Online`, GET controlado 200 y registro visible; consola inicial sin errores/advertencias (ver salvedad de la recarga abajo) |
| GET, POST, PUT y DELETE a `/echo` sintético | API Pulse 200; respuestas de destino 200, 201, 200 y 200; sin métodos mutables enviados a terceros |
| Escenarios 404/500/302 | API Pulse 200 y `success=true` con los códigos recibidos; 302 no siguió redirección |
| URL externa con token sintético | API Pulse 200, `success=false`, URL guardada como `/blocked`; ni token ni cuerpo sintético aparecen en el historial |
| CORS desde el sitio real | Preflight 200 y `Access-Control-Allow-Origin` exacto del sitio |
| CORS desde origen ajeno | Preflight 400, sin `Access-Control-Allow-Origin` |
| Cuerpo mayor de 16 KiB y método PATCH | 413 y 422; no añadieron filas |
| Ráfaga controlada | Secuencia `200, 200, 429`; 429 no añadió fila. El historial posterior tenía 11 registros, los 9 anteriores más dos admitidos |
| Historial y recarga | 11 filas compartidas tras recargar el sitio, orden descendente; 404/500 visibles como `Received` |
| Vista móvil | A 390×844, formulario, resultado y tabla accesibles mediante desplazamiento; se restauró el viewport normal |
| Visita tras más de 16 minutos sin tráfico a la API | Recarga del sitio en ~14 s, `Online`, 11 filas previas conservadas en Neon; un nuevo GET controlado se guardó como fila 12 |
| Fecha inglesa tras desplegar `a32bc4f` | Navegador con idioma español mostró `Sep 20, 02:34 PM`, no `sept` |
| Readiness e historial tras inactividad | `/ready` respondió `ready`, `limit=1` devolvió una fila y `limit=101` devolvió 422 |

Las solicitudes HTTP salientes de los checks usan `MockTransport`; el dominio `.invalid` es una etiqueta de escenario, no un destino de red. La política de poda 24 h/500 tiene pruebas automatizadas, pero no se observó durante 24 horas en Neon. Las cuotas se probaron tras el proxy desde un cliente; no está demostrado que el límite por IP distinga correctamente a visitantes distintos detrás de Render. La visita se hizo tras más de 16 minutos sin tráfico y recuperó la aplicación; el panel de Render no mostró un evento independiente que confirmase si la instancia había pasado al estado suspendido. Los primeros logs de consola del sitio no tuvieron advertencias/errores; tras la recarga aparecieron tres mensajes genéricos del canal asíncrono del navegador/extensiones, sin traza de la aplicación y sin impedir el flujo. No se atribuyen de forma concluyente al código de API Pulse.

## Siguiente bloque

T08: enlazar la demo real desde el README, añadir capturas, resumir límites y crear `LICENSE` MIT únicamente tras recibir el nombre público exacto del titular. El PR #4 permanece en borrador; T07 no fusionó `main`. Como seguimiento no bloqueante, observar la poda al cumplirse 24 horas y, si se amplía el uso público, medir clientes distintos detrás del proxy y preparar migraciones explícitas antes de cambiar el esquema.
