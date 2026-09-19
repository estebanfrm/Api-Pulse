# Despliegue de la demo pública: Render + Neon

**Estado:** procedimiento preparado en T06; no se han creado recursos ni se ha publicado una URL. Ejecutar y verificar en T07. La decisión D09 autoriza solo planes gratuitos, Virginia/N. Virginia y subdominios incluidos, sin compra ni subida de plan.

## Topología y límites

- `render.yaml` define `api-pulse-api`: Web Service Python Free en Virginia, Uvicorn con un worker, y `api-pulse-web`: Static Site con el `dist` compilado de Vue. `autoDeployTrigger: off` conserva el control manual de la primera publicación. Render asigna los subdominios HTTPS reales; no asumirlos a partir de los nombres.
- El navegador llama a la URL **pública** de la API desde el sitio estático. `VITE_API_BASE_URL` se inyecta en el build con `RENDER_EXTERNAL_URL` de la API; `FRONTEND_ORIGIN` se obtiene de la URL del sitio. Al cambiar un dominio, resincronizar el Blueprint y reconstruir el frontend, porque Vite incorpora el valor al bundle. La compilación pública falla si la URL de API no es un origen HTTPS.
- Neon Free se crea por separado en `aws-us-east-1` (N. Virginia), si el plan/región siguen disponibles. Render y Neon son proveedores distintos: **no hay red privada entre ellos** en esta configuración. La base acepta conexiones por su endpoint de Neon con credenciales y TLS/canal vinculado; el secreto solo llega al backend. No se publica un puerto PostgreSQL propio ni se incluye la URL de conexión en el frontend o en Git.
- La demo no hace conexiones salientes a APIs arbitrarias: los escenarios son sintéticos. Las cuotas en memoria requieren exactamente un worker y una instancia. Detrás del proxy, varios visitantes podrían compartir la IP de par; el límite global sigue activo, pero la utilidad del límite por IP debe medirse en T07 sin confiar en `X-Forwarded-For` enviado por el visitante.

Render [documenta Blueprints, `rootDir`, variables y `sync: false`](https://render.com/docs/blueprint-spec), [FastAPI con Uvicorn y `$PORT`](https://render.com/docs/deploy-fastapi) y el patrón [sitio estático + API pública con CORS](https://render.com/tutorials/web-service-vs-static-site/the-hybrid-pattern). Neon [identifica el endpoint agrupado por `-pooler`](https://neon.com/blog/postgres-support-case-recap) y [explica `channel_binding=require` junto a TLS](https://neon.com/blog/postgres-needs-better-connection-security-defaults).

## Preparación antes de crear recursos

1. Publicar primero en el repositorio una revisión controlada del código T00–T06 y comprobar la CI del commit. El worktree actual está en `HEAD` separado y los cambios aún no tienen commit; el Blueprint no existe en el remoto hasta ese paso. No copiar `.env` ni secretos.
2. Revisar en Render y Neon que los planes gratuitos y las cuotas sigan vigentes. En Render, elegir Free para la API y Static Site gratuito; no crear Render Postgres. Confirmar que una cuenta con método de pago puede incurrir en cargos por uso excedente y establecer alertas/límites de gasto disponibles antes de publicar. Render [explica las horas y cuotas Free](https://render.com/docs/free) y [el posible cobro por ancho de banda](https://render.com/docs/outbound-bandwidth).
3. Validar `render.yaml` con `render blueprints validate` si se dispone de la CLI autenticada. La validación YAML local comprueba sintaxis, no reemplaza la validación semántica ni la sincronización real de Render.

## Crear Neon y configurar el secreto

1. Crear un proyecto Neon en el plan Free y región `aws-us-east-1`, sujeto a disponibilidad actual. Usar una base vacía dedicada a la demo; **no importar** datos locales o reales.
2. En Connection Details, seleccionar **Pooled connection**. Copiar la URL solo a un gestor de secretos o directamente al campo `DATABASE_URL` de Render durante la primera sincronización. Cambiar únicamente el prefijo `postgresql://` o `postgres://` por `postgresql+psycopg://` para SQLAlchemy/psycopg 3. Conservar el host `-pooler...neon.tech` y los parámetros `sslmode=require&channel_binding=require` que ofrezca Neon. Si faltan, añadirlos en el secreto, nunca en el repositorio. No imprimir la URL ni pegarla en capturas, issues o logs.
3. `APP_ENV=production` verifica al arrancar que la demo controlada esté activa, que `FRONTEND_ORIGIN` sea un único origen HTTPS y que la URL use psycopg, Neon agrupado, TLS y channel binding. Un valor inseguro causa fallo de arranque con un mensaje genérico. La validación de configuración no prueba conectividad; `/ready` sí la comprueba.

## Crear Render desde el Blueprint

1. En Render, vincular el repositorio y la rama con el commit verificado, crear un Blueprint a partir de `render.yaml` y revisar **antes de aceptar** que solo se crearán los dos servicios previstos y que la API tiene plan Free/región Virginia. No añadir una base Render ni servicios pagados.
2. Proporcionar `DATABASE_URL` como secreto cuando Render lo solicite (`sync: false`). Render [solo solicita esos valores en la creación inicial](https://render.com/docs/blueprint-spec); cambios posteriores de credenciales se hacen en Environment del servicio. Comprobar sin mostrar secretos que `FRONTEND_ORIGIN` coincide con la URL HTTPS del sitio y que `VITE_API_BASE_URL` coincide con la URL HTTPS pública de la API. Si las referencias cruzadas no se resuelven en la primera sincronización, detener la publicación, fijar las URL reales en Environment y resincronizar/reconstruir; no sustituirlas por `localhost`.
3. Confirmar que el proceso de API arranca con `--workers 1 --no-access-log --no-proxy-headers`. El acceso HTTP no se registra deliberadamente; los fallos de configuración y base no deben incluir credenciales en respuestas. El modo local `PUBLIC_DEMO=false` nunca debe exponerse.
4. Render usa `/health` para la disponibilidad del proceso. Este endpoint no consulta Neon: evita despertar la base por una sonda continua. `/ready` realiza un `SELECT 1`, devuelve 200/503 y se usa manualmente en smoke tests o diagnóstico, no como monitor periódico. El primer arranque crea la tabla faltante con `Base.metadata.create_all`, sin seed ni importación de registros.

## Smoke test de T07

Usar las dos URL reales asignadas por Render; no inventarlas. Desde PowerShell, con variables locales de sesión sin secretos:

~~~powershell
$apiUrl = 'https://URL-REAL-API.onrender.com'
$webUrl = 'https://URL-REAL-SITIO.onrender.com'
Invoke-RestMethod "$apiUrl/health"
Invoke-RestMethod "$apiUrl/ready"
$payload = @{ url = 'https://demo.api-pulse.invalid/echo'; method = 'POST'; body = @{ example = $true } } | ConvertTo-Json -Depth 4
Invoke-RestMethod "$apiUrl/api/checks" -Method Post -ContentType 'application/json' -Body $payload
Invoke-RestMethod "$apiUrl/api/checks?limit=50"
~~~

Sustituir los marcadores por los valores observados, no copiar el ejemplo tal cual. Abrir `$webUrl` y comprobar que el bundle llama a `$apiUrl`, CORS permite únicamente el origen del sitio, GET/POST/PUT/DELETE funcionan contra escenarios sintéticos, 404/500 son respuestas recibidas, 302 no se sigue, una URL fuera del catálogo se rechaza con URL canónica y el historial no contiene body/headers/IP. Verificar 413/429 con tráfico controlado y sin afectar otros proyectos. Repetir tras más de 15 minutos de inactividad: Render Free puede iniciar en frío y Neon puede reactivarse; la interfaz debe recuperarse con sus reintentos. No enviar POST/PUT/DELETE a servicios públicos ajenos ni hacer pings artificiales para mantener los planes despiertos.

## Persistencia, cambios de esquema y recuperación

- La versión v1 tiene una sola tabla creada con `create_all`. Esto **solo crea tablas faltantes**: no migra columnas existentes ni revierte cambios de esquema. T06 no cambia el modelo; para cualquier futura modificación de columnas, escribir y probar una migración explícita en una base de ensayo antes de publicar, con exportación previa y plan de reversión. No presentar `create_all` como sistema de migraciones.
- El historial se limita a metadatos sintéticos y se depura al iniciar/crear/listar. Si Neon pierde la base, se puede crear otra vacía y actualizar el secreto; el servicio recreará la tabla, pero el historial reciente se perderá. Registrar esa pérdida como incidencia, no simular una restauración que no existe. No borrar la base anterior ni su proyecto antes de validar la nueva conexión.
- Para revertir solo código, usar el deploy anterior de **ambos** servicios en Render y mantener la misma base, ya que T06 no altera el esquema. Confirmar que frontend y API vuelven a versiones compatibles. Si una migración futura sí alteró el esquema, el rollback de código podría no ser suficiente; seguir su plan de reversión y copia de seguridad específico.
- La CI añade un smoke con PostgreSQL 16 efímero: startup, `/ready`, check y persistencia tras recrear el cliente. Esto comprueba PostgreSQL/psycopg, **no Neon ni el proxy real**. T07 debe verificar Neon y registrar la versión/commit desplegados, URL, fecha, resultados y ruta de rollback.

## Operación y cuotas

Revisar errores genéricos, estado de despliegue y consumo en los paneles de Render/Neon sin copiar credenciales. Mantener `autoDeployTrigger: off` durante la primera publicación controlada; solo cambiar a `checksPass` tras comprobar que la CI del commit publicado es fiable y el usuario desea despliegues automáticos. Render [documenta ambas opciones](https://render.com/docs/deploys). No activar recursos pagados o compras para superar límites sin una decisión nueva.
