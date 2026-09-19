# Requisitos y alcance

**Objetivo confirmado:** proyecto de portafolio con despliegue público (usuario, 2026-09-14).

Los requisitos funcionales actuales se reconstruyen de README, código y pruebas; no existe una especificación original independiente. Los criterios de publicación y cierre son una propuesta técnica para alcanzar el objetivo, y sus decisiones de producto pendientes se identifican expresamente.

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
| RP01 | URL pública HTTPS accesible y enlazada desde README | D09 confirma Render Free + Neon Free y subdominios gratuitos; publicación pendiente | T04 completado, T07 |
| RP02 | Modo de demo definido: acceso, destinos y métodos permitidos | D08 aprobada; cuatro escenarios sintéticos y cuatro métodos implementados; dominio final sin probar | T04/T05 locales, T07 público |
| RP03 | Solicitudes salientes acotadas: destino validado al conectar, frecuencia/concurrencia, tiempo y bytes | T05 evita conexión saliente a destinos de usuario; cuotas/bytes y timeout del cliente probados localmente; proxy público pendiente | T05 local, T07 público |
| RP04 | Historial público con política explícita de visibilidad, redacción y retención; sin tokens de terceros | T05 guarda campos mínimos y poda 24 h/500 al iniciar/crear/listar; Neon no probado | T05 local, T07 público |
| RP05 | Entorno de producción: frontend compilado, configuración de orígenes y backend, base no expuesta al navegador y secretos externos | T06 preparó Blueprint, build/cors y Neon secreto TLS; Render/Neon sin crear. Entre proveedores no hay red privada | T06 local, T07 público |
| RP06 | Restaurar/recrear una demo con datos no sensibles y documentar rollback | T06 documentó recreación vacía y rollback de código; procedimiento real no ejecutado | T06 local, T07 público |
| RP07 | CI satisfactoria para el commit publicado y prueba integrada con la base de datos elegida | T06 añadió job PostgreSQL 16 efímero; no ejecutado local/remoto. Neon final pendiente | T03 local, T06 preparado, T07 público |
| RP08 | README final con demo, capturas reales, arquitectura, uso, límites y evidencia de calidad | Base documental lista; evidencia final pendiente | T08 |
| RP09 | Flujo principal usable en móvil y escritorio, con teclado y estados de carga/error comprensibles | Recuperación validada localmente en escritorio, vista móvil y teclado; dominio final pendiente | T02 completado, T07 |
| RP10 | Licencia y condiciones de uso de la demo decididas antes de anunciar su reutilización | MIT aprobada; falta titular y archivo `LICENSE` | T04 completado, T08 |

## Alcance público decidido e implementado localmente

- La demo pública es anónima y está acotada a escenarios controlados; no acepta hosts arbitrarios. Falta verificarlo en producción.
- Render Free + Neon Free requieren comprobar persistencia, recuperación y arranque en frío dentro de sus cuotas.
- El historial compartido público se limita a 24 horas y 500 filas visibles; la redacción y poda se implementaron en T05. El borrado ocurre al iniciar/crear/listar, no durante inactividad.
- La interfaz seguirá en inglés. MIT fue elegida, pero el titular y el archivo `LICENSE` se resolverán en T08.

La [propuesta T04](PROPUESTA_T04.md) contiene el alcance inicial y las alternativas examinadas; [decisiones](DECISIONES.md) registra las opciones aprobadas.

## Extensiones sin prioridad aprobada

Monitorización programada, alertas, equipos, facturación, colecciones guardadas, exportación, PATCH/HEAD/OPTIONS y carga de archivos no existen ni forman parte del cierre actual. Se pueden incorporar después mediante un requisito y una decisión explícitos.

## Definición de terminado

Cumplir la [lista de cierre](PLAN_DE_CIERRE.md#criterios-para-dar-el-proyecto-por-terminado), incluida la URL pública validada y su evidencia. Tener documentación organizada no equivale a haber terminado el producto.
