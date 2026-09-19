# Propuesta T04 — Demo pública y alojamiento

**Corte de precios y capacidades:** 2026-09-15.
**Estado:** D09 confirmada el 2026-09-15; D08, D10, D11 y la elección MIT de D12 confirmadas el 2026-09-19. T04 completada. El titular del aviso MIT queda pendiente para T08. Las aprobaciones no equivalen a implementación ni autorizan recursos pagados o publicación sin verificación.

## Recomendación ejecutiva

Publicar una **demo anónima y acotada**, no un proxy abierto: conservar GET, POST, PUT y DELETE, pero ejecutarlos únicamente contra escenarios controlados por API Pulse. La infraestructura aprobada usa frontend y backend gratuitos en Render y PostgreSQL gratuito en Neon, con subdominios HTTPS sin compra de dominio. Mantener un historial compartido de metadatos no sensibles durante 24 horas, la interfaz en inglés y la documentación principal en español con un resumen en inglés. **MIT está elegida**; falta el nombre que figurará como titular antes de crear `LICENSE`.

El presupuesto inicial confirmado es **USD 0/mes**. Esto acepta arranques en frío y cuotas de los proveedores gratuitos; no supone disponibilidad garantizada ni autoriza recursos pagados. El nivel pagado estimado en USD 13,30/mes se conserva únicamente como alternativa futura.

## D08 — Modo de demo, destinos, métodos y acceso

| Tema | Propuesta | Consecuencia para T05 |
| --- | --- | --- |
| Acceso | Público, anónimo y sin cuenta | La primera visita puede probar el producto sin fricción |
| Destinos | Solo rutas HTTPS controladas y propiedad del proyecto, elegidas desde ejemplos explícitos | No se aceptan hosts arbitrarios ni se convierte el servicio en proxy público |
| Métodos | Mantener GET, POST, PUT y DELETE | Se conserva el contrato actual y se demuestra el manejo de cuerpos JSON |
| Escenarios | Éxito/eco y respuestas 302, 404 y 500 con rutas finitas; ninguna ruta puede apuntar de nuevo al ejecutor de checks | Permite enseñar los estados ya comprobados sin acceso libre a Internet |
| Datos de entrada | JSON de ejemplo y cabeceras de prueba; aviso visible para no enviar secretos, credenciales ni datos personales | Cuerpo y cabeceras no se guardan en historial ni se escriben deliberadamente en logs |
| Controles iniciales | 10 checks/minuto e IP, máximo 2 simultáneos por IP; 60/minuto y 10 simultáneos globales | Rechazo explícito y probado cuando se supera un límite |
| Límites de transporte | Cuerpo de solicitud máximo 16 KiB, respuesta leída máximo 64 KiB y espera total máxima 8 s | Evita descargas o trabajos desproporcionados para una demo pequeña |
| Red | Mantener bloqueo local/privado y redirecciones desactivadas; ligar validación y conexión al destino efectivo | Cierra la separación DNS/conexión identificada en T05 |

Los valores de frecuencia, concurrencia y transporte son parámetros técnicos iniciales, no límites numéricos aceptados individualmente por el usuario. T05 debe verificarlos y puede reducirlos si una prueba controlada demuestra que exceden la capacidad del plan gratuito; no se abrirán destinos arbitrarios sin una nueva decisión.

## D09 — Plataforma, coste, región, dominio y persistencia

### Opción aprobada: Render Free + Neon Free

| Recurso | Configuración aprobada | Estimado mensual |
| --- | --- | ---: |
| Frontend | Static Site; build de Vue/Vite y contenido de `dist` | USD 0 |
| Backend | Web Service Free de Render | USD 0 |
| Base | Neon Free: PostgreSQL, 0,5 GB y 100 CU-horas mensuales por proyecto según el corte | USD 0 |
| Dominio | Subdominios gratuitos del proveedor | USD 0 |
| Total base | Dentro de cuotas y sin recursos adicionales | **USD 0** |

- Región: Render **Virginia** y Neon **AWS US East 1 (N. Virginia, `aws-us-east-1`)**, sujetos a disponibilidad del plan gratuito. La proximidad reduce la latencia de una conexión que cruza la red pública.
- Base: usar el string agrupado de Neon con TLS; nunca guardar esa URL en Git ni exponerla al frontend.
- Frontend: CDN estática de Render. Backend: subdominio `onrender.com` con TLS administrado. No comprar dominio en T04.
- Arranque en frío: el frontend debe explicar el estado y tolerar hasta aproximadamente un minuto de activación del backend. Neon también escala su cómputo a cero cuando está inactivo.
- Cuotas: no usar pings artificiales para mantener vivo el servicio. T06 debe configurar límites y T07 comprobar el comportamiento tras inactividad y al acercarse a cuotas.
- Persistencia: Neon Free no tiene el límite de expiración de 30 días de Render Postgres Free, pero depende de las cuotas vigentes. T06 debe documentar exportación/recreación y T07 verificarla.
- Escalamiento: cualquier recurso pagado, dominio propio o proveedor adicional requiere una nueva aprobación.

Render advierte que un web service Free se apaga tras 15 minutos sin tráfico y puede tardar alrededor de un minuto en reactivarse. También puede suspender un servicio gratuito si inicia un volumen inusual de tráfico público. Por ello D08 mantiene destinos y cuotas estrictos.

Una base gratuita de Render no es una alternativa persistente aceptable para el portafolio: expira a los 30 días, tiene 14 días de gracia y luego se elimina; tampoco incluye backups.

### Alternativa futura: Render pagado mínimo

Si los arranques en frío perjudican la evaluación del portafolio, se puede solicitar una nueva aprobación para: sitio estático USD 0, backend de 512 MB USD 7/mes y PostgreSQL de 256 MB USD 6/mes más 1 GB a USD 0,30. El estimado al corte es **USD 13,30/mes** antes de impuestos y excedentes. No está autorizado.

## D10 — Historial público y datos

- Historial compartido y de solo lectura para visitantes; no se crean cuentas ni sesiones persistentes.
- Guardar solo: método, identificador/etiqueta del escenario, estado HTTP si existió, latencia, resultado recibido/no recibido y fecha UTC.
- No guardar cabeceras, cuerpo, IP, query arbitraria, credenciales ni cuerpo completo de respuesta. El resumen histórico actual debe reemplazarse por un resumen seguro y predecible del escenario controlado.
- Mostrar las últimas 50 filas, conservar como máximo 500 y eliminar datos con más de 24 horas. T05 debe ejecutar limpieza periódica y también al iniciar/leer/escribir para que la política no dependa de una operación manual.
- La IP se usa de forma efímera para cuotas y no se persiste en la tabla de checks. La configuración de logs debe evitar entradas y respuestas aportadas por visitantes.
- Al recrear la demo se pueden cargar ejemplos sintéticos sin información personal. La recuperación no necesita preservar actividad histórica de visitantes más allá de la ventana de 24 horas.
- Aviso visible: demo de portafolio sin SLA; no introducir secretos, credenciales ni datos personales.

## D11 — Idioma y presentación

- Mantener la interfaz en **inglés** para que la demo sea evaluable internacionalmente y evitar duplicar el alcance de T05–T07.
- Mantener la documentación operativa en **español** y añadir en T08 un resumen ejecutivo breve en inglés al README público.
- No añadir selector de idioma en este cierre; queda como mejora posterior.

## D12 — Licencia

Se compararon dos licencias coherentes con la prioridad open source del usuario; **MIT fue la elegida el 2026-09-19**:

| Licencia | Efecto principal | Cuándo elegirla |
| --- | --- | --- |
| MIT | Permisiva: facilita uso, modificación y distribución, incluso dentro de productos cerrados, conservando el aviso | Priorizar adopción y sencillez para portafolio |
| AGPLv3 | Copyleft: una versión modificada ofrecida por red debe facilitar su código fuente correspondiente a sus usuarios | Priorizar que mejoras de servicios derivados sigan disponibles |

La elección de licencia no paga ni vuelve open source a Render/Neon; regula el código de API Pulse. La infraestructura confirmada usa servicios gratuitos propietarios para ejecutar un stack de aplicación open source.

La licencia del código no sustituye las condiciones de la demo alojada. El aviso de uso limitado descrito en D08/D10 debe permanecer en la interfaz y el README.

Antes de crear `LICENSE` falta el nombre público exacto que debe aparecer en `Copyright (c) 2026 ...`. Se pedirá en T08. Hasta crear el archivo, no describir el repositorio como ya licenciado bajo MIT.

## Evidencia consultada

- [Render Pricing](https://render.com/pricing): planes de cómputo, PostgreSQL, almacenamiento, ancho de banda, dominios y minutos incluidos.
- [Render Free](https://render.com/docs/free): apagado por inactividad, límites de tráfico y expiración/ausencia de backups de PostgreSQL Free.
- [Render Regions](https://render.com/docs/regions): regiones disponibles, CDN estática y restricción para cambiar región.
- [Create and Connect to Render Postgres](https://render.com/docs/postgresql-creating-connecting): región compartida, URL interna y almacenamiento inicial.
- [Render Postgres Recovery and Backups](https://render.com/docs/postgresql-backups): recuperación de tres días en Hobby para bases pagadas.
- [Render Static Sites](https://render.com/docs/static-sites), [Vue](https://render.com/docs/deploy-vue-js) y [FastAPI](https://render.com/docs/deploy-fastapi): compatibilidad de los componentes actuales.
- [Render Custom Domains](https://render.com/docs/custom-domains) y [TLS](https://render.com/docs/tls): subdominios, dominios propios y HTTPS administrado.
- [Neon Pricing](https://neon.com/pricing) y [Connection Pooling](https://neon.com/docs/connect/connection-pooling): límites y capacidad de la alternativa gratuita.
- [SPDX MIT](https://spdx.org/licenses/MIT): identificador y texto normalizado de MIT.
- [GNU AGPL](https://www.gnu.org/licenses/): propósito y texto oficial de AGPLv3 para software usado por red.

## Aprobación y ejecución pendiente

D08–D12 quedaron confirmadas mediante respuestas del usuario del 2026-09-15 y 2026-09-19, según [el registro de decisiones](DECISIONES.md). T05 ya implementó y probó localmente controles e historial; T06 preparó `render.yaml` y la [guía Render/Neon](DESPLIEGUE_RENDER_NEON.md). T07 verificará el despliegue; T08 pedirá el titular exacto y creará `LICENSE`. No se han creado recursos externos.
