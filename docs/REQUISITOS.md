# Requisitos y alcance

**Objetivo confirmado:** proyecto de portafolio con despliegue público (usuario, 2026-09-14).

Los requisitos funcionales se reconstruyeron de README, código y pruebas; no existe una especificación original independiente. D08–D12 fueron aprobadas después y la [validación T07](VALIDACION_T07.md) registró su comprobación pública. Los límites observados permanecen explícitos.

## Usuario y recorrido principal

Persona que visita el portafolio o evalúa el trabajo técnico: abre la demo, ejecuta una solicitud de ejemplo, interpreta su respuesta y latencia, consulta el historial y entiende la arquitectura y sus límites.

## Funciones del MVP

| ID | Requisito / criterio de aceptación | Situación actual | Cierre |
| --- | --- | --- | --- |
| RF01 | Aceptar URL HTTP(S) y GET/POST/PUT/DELETE; rechazar otros métodos con 422 | Cuatro métodos y rechazo PATCH comprobados en T03; T05 limita las URL del modo público al catálogo aprobado | T01/T03/T05 completados localmente |
| RF02 | Headers y body deben ser objetos JSON; errores visibles; GET no envía body | Eco controlado confirmó cabeceras/cuerpo y GET sin body; error JSON visible | T01/T03 completados |
| RF03 | Mostrar código, tiempo y cuerpo de respuesta JSON/texto | Comprobado con navegador y stack real | T03 completado |
| RF04 | Distinguir respuesta HTTP de error de red o seguridad; 4xx/5xx conservan su código | 404/500 recibidos y bloqueo local sin respuesta comprobados | T02/T03 completados |
| RF05 | Guardar resultado, fecha UTC y resumen; fallos de destino también quedan registrados | Diez filas verificadas en PostgreSQL UTC tras reinicio y recarga | T03 completado |
| RF06 | Listar últimas comprobaciones por fecha descendente, límite 1–100, defecto 50 | Orden, límite 3 y rechazo 101 comprobados contra PostgreSQL | T01/T03 completados |
| RF07 | Mostrar hasta 12 tiempos válidos con promedio; excluir fallos sin respuesta | Gráfica y promedio comprobados con respuestas mixtas | T03 completado |
| RF08 | Mostrar carga, vacío, error y recuperación sin perder un resultado guardado | Completado en T02 con estados independientes, conservación y reintentos | T02 completado |
| RF09 | Bloquear destinos locales/privados y desactivar redirecciones | Localhost bloqueado y 302 no seguido en T03; T05 usa catálogo sintético sin DNS/socket y comprueba 302 sin seguir | T01/T03/T05 completados localmente |

## Requisitos de publicación y portafolio

| ID | Criterio propuesto de aceptación | Estado | Cierre |
| --- | --- | --- | --- |
| RP01 | URL pública HTTPS accesible y enlazada desde README | [Sitio](https://api-pulse-web.onrender.com) y API comprobados en T07; README enlaza el sitio | T07/T08 |
| RP02 | Modo de demo definido: acceso, destinos y métodos permitidos | Demo anónima acotada; cuatro escenarios y cuatro métodos comprobados públicamente | T05/T07 |
| RP03 | Solicitudes salientes acotadas: destino, frecuencia/concurrencia, tiempo y bytes | Sin egress a destinos de usuario; 413 y 429 observados públicamente. Separación por IP entre distintos visitantes tras proxy no demostrada | T05/T07, límite documentado |
| RP04 | Historial público con política explícita de visibilidad, redacción y retención; sin tokens de terceros | Neon y redacción verificados; 24 h/500 probado automáticamente, no observado durante 24 horas reales | T05/T07, límite documentado |
| RP05 | Entorno de producción: frontend compilado, configuración de orígenes y backend, base no expuesta al navegador y secretos externos | Render Free y Neon Free desplegados; secreto solo en backend, CORS exacto y `/ready` comprobados. Entre proveedores no hay red privada | T06/T07 |
| RP06 | Restaurar/recrear una demo con datos no sensibles y documentar rollback | Recreación de base vacía y rollback de código documentados; no se ejecutó un rollback real ni se promete recuperar historial perdido | T06/T07, límite documentado |
| RP07 | CI satisfactoria para el commit publicado y prueba integrada con la base de datos elegida | CI de commits desplegados aprobada, incluido smoke PostgreSQL 16; Neon real comprobado en T07 | T03/T06/T07 |
| RP08 | README final con demo, capturas reales, arquitectura, uso, límites y evidencia de calidad | README/capturas en `main`, portada pública verificada y CI del merge `0cb28cf` aprobada | T08 completado |
| RP09 | Flujo principal usable en móvil y escritorio, con teclado y estados de carga/error comprensibles | Recuperación local y vista móvil/escritorio pública comprobadas; tras inactividad se recuperaron datos | T02/T07 |
| RP10 | Licencia y condiciones de uso de la demo decididas antes de anunciar su reutilización | MIT elegida; usuario indicó «API PULSE» y se creó `LICENSE` en T08 | T04/T08 |

## Alcance público decidido e implementado localmente

- La demo pública es anónima y está acotada a escenarios controlados; no acepta hosts arbitrarios. Se verificó en Render.
- Render Free + Neon Free conservaron historial tras más de 16 minutos sin tráfico; no se observó un evento independiente de suspensión efectiva ni se promete disponibilidad.
- El historial compartido público se limita a 24 horas y 500 filas; la redacción y poda se implementaron en T05. El borrado ocurre al iniciar/crear/listar, no durante inactividad.
- La interfaz está en inglés. MIT usa el nombre público «API PULSE» indicado por el usuario.

La [propuesta T04](PROPUESTA_T04.md) contiene el alcance inicial y las alternativas examinadas; [decisiones](DECISIONES.md) registra las opciones aprobadas.

## Extensiones sin prioridad aprobada

Monitorización programada, alertas, equipos, facturación, colecciones guardadas, exportación, PATCH/HEAD/OPTIONS y carga de archivos no existen ni forman parte del cierre actual. Se pueden incorporar después mediante un requisito y una decisión explícitos.

## Definición de terminado

Cumplir la [lista de cierre](PLAN_DE_CIERRE.md#criterios-para-dar-el-proyecto-por-terminado), incluida la URL pública validada y su evidencia. Tener documentación organizada no equivale a haber terminado el producto.
