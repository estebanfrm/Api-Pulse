# T07 — Validación del despliegue público

**Corte:** 2026-09-20, America/Bogota. **Estado:** desplegado y verificado parcialmente; falta comprobar el arranque en frío tras más de 15 minutos sin tráfico y repetir CI/despliegue del ajuste de fechas en inglés.

## Recursos y versión observados

- Sitio: [https://api-pulse-web.onrender.com](https://api-pulse-web.onrender.com), Render Static Site.
- API: [https://api-pulse-api.onrender.com](https://api-pulse-api.onrender.com), Render Web Service **Free** en Virginia.
- Base: proyecto nuevo `api-pulse-demo`, Neon **Free**, PostgreSQL 16 en AWS US East 1 (N. Virginia), base vacía dedicada `api_pulse`. Solo el backend recibió la conexión agrupada con TLS y `channel_binding=require` como secreto `DATABASE_URL`; no se registró su valor en Git o en este documento.
- Se creó un workspace Render exclusivo `API Pulse`, plan Hobby, **sin método de pago**. No se seleccionaron servicios pagados ni Render Postgres. Render suspende servicios/builds al agotar cuotas en un workspace sin tarjeta, según su [documentación de Free](https://render.com/docs/free). El uso debe supervisarse; presupuesto inicial USD 0 no equivale a disponibilidad garantizada.
- Blueprint de la rama `codex/api-pulse-t07-publication` sincronizado por Render desde `98cb6f9dd012a43974ba2bf844d9875ff169abb8`. Los dos servicios se observaron con ese commit. `main` seguía en `7399e86` antes del despliegue; PR #4 continúa en borrador.
- Rollback del código: volver al deploy anterior compatible de **ambos** servicios en Render y conservar Neon. No borrar la base ni el proyecto; `create_all` no ejecuta migraciones de columnas. Solo hay una versión funcional inicial hasta este corte; no declarar un rollback probado.

## Calidad y despliegue

- Comandos locales ejecutados en `frontend/`: `node 'C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js' audit --omit=optional` (0 vulnerabilidades), `node --test` (8 aprobadas tras el ajuste), `node node_modules/eslint/bin/eslint.js .` (aprobado) y `node node_modules/vite/bin/vite.js build` con `RENDER=true`, `VITE_PUBLIC_DEMO=true` y `VITE_API_BASE_URL=https://api-pulse-api.onrender.com` (aprobado, 18 módulos). El shim global de npm sigue roto; no se ocultó con cambios de dependencias.
- El 2026-09-20, `npm audit --omit=optional` local devolvió **0 vulnerabilidades**. Se reintentaron los jobs fallidos de la [CI del commit `98cb6f9`](https://github.com/estebanfrm/Api-Pulse/actions/runs/35457537980): intento 2, estado `completed`, conclusión `success`. La CI incluye Backend, smoke PostgreSQL 16, Compose y Frontend. El fallo inicial de auditoría del 2026-09-19 se conserva en [estado actual](ESTADO_ACTUAL.md#t07--publicación-y-verificación); no se modificaron dependencias para eludirlo.
- Render aceptó semánticamente `render.yaml` al planificar/sincronizar el Blueprint. La primera ejecución del backend falló porque `FRONTEND_ORIGIN` aún no se había creado durante la sincronización inicial; Render programó un segundo deploy tras configurar la referencia cruzada. Ese segundo deploy quedó **Live**. El frontend compiló y quedó **Live**. `FRONTEND_ORIGIN` se observó como `https://api-pulse-web.onrender.com` y `VITE_API_BASE_URL` como `https://api-pulse-api.onrender.com`.
- La comprobación local del ajuste de fecha inglesa aprobó 8 pruebas frontend, ESLint y build público Vite de 18 módulos. Ese ajuste todavía no estaba en el commit desplegado al corte de este documento.

## Smoke público con datos sintéticos

Comandos base ejecutados con las URL observadas: `Invoke-RestMethod 'https://api-pulse-api.onrender.com/health'`, `Invoke-RestMethod 'https://api-pulse-api.onrender.com/ready'` y `Invoke-RestMethod 'https://api-pulse-api.onrender.com/api/checks?limit=50'`. Los checks POST se enviaron a `/api/checks` con `Invoke-WebRequest -Method Post -ContentType 'application/json' -Body $payload -SkipHttpErrorCheck`; `$payload` contenía solo métodos y URLs de escenarios sintéticos. Para CORS se usó `-Method Options` y cabeceras `Origin`, `Access-Control-Request-Method` y `Access-Control-Request-Headers`. No se usaron APIs públicas ajenas para métodos mutables.

| Comprobación | Resultado observado |
| --- | --- |
| `GET /health` y `GET /ready` | 200, `ok` y `ready`; confirma proceso y consulta a Neon |
| Interfaz en navegador | `Online`, GET controlado 200 y registro visible; sin errores/advertencias de consola |
| GET, POST, PUT y DELETE a `/echo` sintético | API Pulse 200; respuestas de destino 200, 201, 200 y 200; sin métodos mutables enviados a terceros |
| Escenarios 404/500/302 | API Pulse 200 y `success=true` con los códigos recibidos; 302 no siguió redirección |
| URL externa con token sintético | API Pulse 200, `success=false`, URL guardada como `/blocked`; ni token ni cuerpo sintético aparecen en el historial |
| CORS desde el sitio real | Preflight 200 y `Access-Control-Allow-Origin` exacto del sitio |
| CORS desde origen ajeno | Preflight 400, sin `Access-Control-Allow-Origin` |
| Cuerpo mayor de 16 KiB y método PATCH | 413 y 422; no añadieron filas |
| Ráfaga controlada | Secuencia `200, 200, 429`; 429 no añadió fila. El historial posterior tenía 11 registros, los 9 anteriores más dos admitidos |
| Historial y recarga | 11 filas compartidas tras recargar el sitio, orden descendente; 404/500 visibles como `Received` |
| Vista móvil | A 390×844, formulario, resultado y tabla accesibles mediante desplazamiento; se restauró el viewport normal |

Las solicitudes HTTP salientes de los checks usan `MockTransport`; el dominio `.invalid` es una etiqueta de escenario, no un destino de red. La política de poda 24 h/500 tiene pruebas automatizadas, pero todavía no se ha observado durante 24 horas en Neon. Las cuotas se probaron tras el proxy desde un cliente; aún no está demostrado que el límite por IP distinga correctamente a visitantes distintos detrás de Render.

## Pendiente para cerrar T07

1. Publicar el ajuste de fecha inglesa y confirmar CI del commit final, despliegue actualizado y smoke básico del sitio.
2. Dejar inactivo el backend al menos 15 minutos, luego visitar el sitio, comprobar recuperación de Render/Neon y que el historial permanezca. No usar keep-alive artificial.
3. Registrar la versión final y consumo de cuotas; conservar el PR en borrador si alguna comprobación falla. T08 seguirá con README, capturas y `LICENSE` al recibir el nombre público exacto del titular.
