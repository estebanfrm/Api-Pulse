# Registro de decisiones

**Corte:** 2026-09-19.

Estados:

- **Confirmada:** instrucción expresa del usuario.
- **Observada:** elección implementada; no se atribuye una aprobación histórica.
- **Propuesta:** recomendación para resolver una necesidad; pendiente de validación.
- **Abierta:** falta una elección que cambia el resultado.

## D01 — Resultado final

**Confirmada.** El proyecto debe servir como portafolio con despliegue público. Fuente: respuesta del usuario del 2026-09-14.

Consecuencia: el cierre requiere demo accesible, evidencia, documentación de presentación y controles apropiados para un backend expuesto.

## D02 — Stack actual

**Observada:** Vue 3 + Vite, FastAPI + httpx, SQLAlchemy + PostgreSQL, Docker Compose. Fuentes: manifests, Dockerfiles y código.

**Propuesta de continuidad:** conservar el stack durante el cierre para aprovechar la implementación existente. No se reconstruyó el razonamiento original ni una comparación de alternativas.

## D03 — Significado de success

**Observada:** indica que llegó una respuesta HTTP, también para 4xx y 5xx. Fuente: `api_client.py`.

Consecuencia: desde T02 la interfaz usa `Response received`/`No response` y explica los estados HTTP 4xx/5xx sin cambiar el contrato. La gráfica continúa incluyendo toda respuesta con tiempo válido. Cambiar la semántica requeriría actualizar API, pruebas y datos/documentación.

## D04 — Registro de errores de destino

**Observada:** bloqueos de seguridad y errores capturados de red producen un check guardado y una respuesta 200 de API Pulse; los rechazos de esquema producen 422. Fuente: `routers/checks.py`.

Consecuencia: la interfaz debe leer `check.success/error_message`, además del estado HTTP externo.

## D05 — Destinos y redirecciones

**Observada:** en el modo local heredado, solo HTTP(S), validación de IP/DNS y redirecciones desactivadas. Fuentes: `security.py` y `api_client.py`. Desde T05 el modo público aprobado usa un catálogo canónico y `MockTransport`, sin DNS ni socket saliente.

Consecuencia: una respuesta 3xx se presenta sin seguirla. El modo público elimina la separación entre destino validado y conexión al no abrirla. El modo local sigue con la separación DNS/httpx anterior y no debe exponerse.

## D06 — Historial y resumen

**Observada:** límite API 50 por defecto/100 máximo, UI 50; resumen de 2000 caracteres; gráfica de 12 respuestas con tiempo válido.

Consecuencia: en desarrollo, el resumen limita el dato guardado y no la descarga. En modo público T05 usa respuestas controladas/acotadas y resumen seguro, con retención confirmada en D10.

## D07 — Entorno de desarrollo y calidad

**Observada:** Docker usa herramientas de desarrollo; pruebas backend con SQLite en memoria y mocks; desde T02 hay pruebas frontend de coordinación de estado con el ejecutor de Node y servicios simulados. T03 añadió una configuración local separada que valida el stack con PostgreSQL 16 y un destino HTTP controlado. CI no levanta ese stack ni despliega.

Consecuencia: la evidencia local de T03 cubre persistencia y flujo integrado de navegador, pero pasar CI todavía no los reproduce y tampoco demuestra idoneidad del contenedor para producción. La configuración T03 usa una ruta de red sintética exclusiva de pruebas y no debe reutilizarse para exposición pública.

**T05 observado:** los Compose de desarrollo e integración fijan `PUBLIC_DEMO=false` y `VITE_PUBLIC_DEMO=false` explícitamente para conservar T03. El valor predeterminado del backend es modo público cerrado. La preparación de producción y su verificación siguen en T06/T07.

## D08 — Modo de demo pública

**Confirmada el 2026-09-19.** El usuario aprobó la demo pública acotada tras recibir la explicación de que no permitirá introducir cualquier URL externa. La demo será anónima, con GET/POST/PUT/DELETE únicamente contra escenarios controlados por API Pulse. Fuente: respuesta directa «listo, entonces si lo apruebo» al desglose de D08, D10, D11 y D12.

**Implementación local T05:** se conservaron los cuatro métodos y las redirecciones desactivadas. Los destinos públicos son respuestas sintéticas dentro del proceso mediante `MockTransport`, sin conexión ni DNS a un host indicado por el visitante. Se aplicaron 10 checks/minuto y 2 simultáneos por IP; 60/minuto y 10 simultáneos globales; entrada de 16 KiB, respuesta de 64 KiB y timeout configurado del cliente de 8 s. El transporte controlado no simula una espera de red real. Son parámetros técnicos iniciales de la [propuesta T04](PROPUESTA_T04.md#d08--modo-de-demo-destinos-métodos-y-acceso), pendientes de verificar tras el proxy público en T07. Las cuotas viven en memoria de un proceso.

La alternativa de permitir APIs públicas arbitrarias con autenticación y controles de red más amplios queda fuera del primer despliegue; necesitaría una nueva decisión.

## D09 — Alojamiento, coste y dominio

**Confirmada el 2026-09-15.** El usuario aprobó la opción de coste cero después de preguntar expresamente por tecnología open source sin pago: frontend en Render Static Free, backend en Render Web Service Free y PostgreSQL en Neon Free. Presupuesto inicial USD 0, subdominios gratuitos y ningún dominio comprado. El plan pagado queda como escalamiento futuro, no autorizado.

**Consecuencias:** usar Render Virginia y Neon `aws-us-east-1` (N. Virginia) para reducir la distancia entre backend y base, sujeto a disponibilidad del nivel gratuito al crear los recursos. La conexión PostgreSQL será TLS y agrupada. T06/T07 deben tratar el arranque en frío como estado esperado y comprobar cuotas, recuperación y persistencia. Render documenta que el web service Free se apaga después de 15 minutos sin tráfico y tarda alrededor de un minuto en reactivarse; Neon Free suspende su cómputo cuando está inactivo. No se usarán pings artificiales para eludir los límites gratuitos.

**Preparación T06:** `render.yaml` define solo Web Service Free y Static Site, con despliegue automático apagado. Neon se crea por separado y se suministra como secreto; Render → Neon no usa una red privada compartida. Producción exige URL pooled con TLS/channel binding, demo acotada y CORS HTTPS. Render [advierte que una cuenta con método de pago puede generar cargos por uso excedente](https://render.com/docs/faq); por tanto USD 0 es presupuesto inicial sujeto a supervisión de cuotas, no garantía de factura cero. No se creó ningún recurso ni se autorizó gasto.

**Revisión T07 del 2026-09-19:** se confirmó en fuentes públicas que Render todavía ofrece [Web Service Free y Static Site gratuito](https://render.com/docs/free), con suspensión de la API tras 15 minutos sin tráfico, y que [el ancho de banda puede facturarse al superar lo incluido si hay método de pago](https://render.com/docs/outbound-bandwidth). Neon describe [su plan Free vigente](https://neon.com/blog/neon-backend-is-ga). No se pudo confirmar el plan, cuotas disponibles ni método de pago de las cuentas concretas porque Render y Neon mostraron inicio de sesión. D09 no cambia y no autoriza excedentes ni planes pagados. La preparación está publicada en `1f373b4`/PR #4; no hay recursos de alojamiento creados.

**Alternativa conservada:** Render pagado completo, estimado el 2026-09-15 en USD 13,30/mes, solo si el arranque en frío perjudica el portafolio y el usuario aprueba el gasto en una decisión posterior.

Fuentes técnicas y límites: [propuesta T04](PROPUESTA_T04.md#d09--plataforma-coste-región-dominio-y-persistencia). Fuente de aprobación: respuesta directa del usuario del 2026-09-15, «la apruebo», a la recomendación explícita de cambiar D09 a USD 0 con Render + Neon.

## D10 — Historial público y datos

**Confirmada el 2026-09-19.** El usuario aprobó un historial compartido visible para todos los visitantes, con máximo 500 registros y retención máxima de 24 horas; la interfaz muestra los 50 más recientes. Fuente: aprobación directa posterior a la explicación de visibilidad, caducidad y datos guardados.

**Implementación local T05:** se persisten únicamente URL canónica del escenario, método, estado, latencia, resumen sintético, éxito/error genérico y fecha UTC; no cuerpo, cabeceras, IP, credenciales ni respuesta arbitraria. La IP se usa efímeramente en cuotas. Se borran filas mayores de 24 horas, filas heredadas fuera del formato público y exceso de 500 al iniciar, crear o listar; durante inactividad no hay borrado continuo. Falta verificar la política sobre Neon en T07. Detalle en la [propuesta T04](PROPUESTA_T04.md#d10--historial-público-y-datos).

La consulta del historial es de solo lectura, aunque cada check nuevo agrega una entrada; los visitantes no podrán editar ni borrar entradas individualmente.

## D11 — Idioma y presentación

**Observada:** interfaz en inglés; **confirmada por contexto de trabajo:** comunicación y documentación de esta organización en español.

**Confirmada el 2026-09-19:** mantener la interfaz de la demo en inglés, la documentación operativa en español y añadir un breve resumen en inglés al README final. Sin selector de idioma en este cierre. Fuente: aprobación directa del usuario tras el desglose de esta opción.

## D12 — Licencia

**Confirmada el 2026-09-19: MIT.** El usuario aprobó expresamente MIT después de recibir la explicación de que permite derivados comerciales/cerrados y no obliga a publicar modificaciones. Fuente: respuesta directa «listo, entonces si lo apruebo» al desglose que incluía MIT. La elección no implica que `LICENSE` ya exista ni que el repositorio esté formalmente licenciado.

**Pendiente para T08:** pedir al usuario el nombre público exacto del titular antes de crear `LICENSE` con el texto estándar MIT. No inventar el titular a partir del usuario de GitHub. Hasta que exista el archivo, no presentar el repositorio como ya licenciado bajo MIT. Referencia y consecuencias en la [propuesta T04](PROPUESTA_T04.md#d12--licencia).

AGPLv3 se consideró como alternativa, pero no fue la opción aprobada.

## D13 — Continuidad con GPT-5.6

**Confirmada:** el usuario quiere continuar con GPT-5.6. Se entrega contexto dentro del repositorio mediante AGENTS, estado y prompt de relevo. No se modificó la selección de modelo de la aplicación.

La elección de modelo del asistente no añade una dependencia de OpenAI al producto API Pulse.

## Plantilla para nuevas decisiones

~~~text
ID y título:
Estado: confirmada / observada / propuesta / abierta / reemplazada
Fecha:
Problema:
Decisión y fuente de aceptación:
Alternativas relevantes:
Consecuencias:
Requisitos/tareas afectados:
Evidencia:
~~~

Al reemplazar una decisión, conserva su referencia y enlaza la nueva.
