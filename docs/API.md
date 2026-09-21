# Contrato actual de la API

Base local: `http://localhost:8000`. Fuente: schemas, routers y services de `backend/app`.

## GET /health

~~~json
{"status":"ok"}
~~~

HTTP 200. Indica que el proceso responde; no comprueba la disponibilidad de PostgreSQL.

## GET /ready

Ejecuta `SELECT 1` contra PostgreSQL y devuelve `{"status":"ready"}` con HTTP 200, o `{"detail":"Database unavailable."}` con HTTP 503 sin datos de conexión. Es una comprobación manual de disponibilidad de base, no el healthcheck periódico de Render; este último usa `/health` para no despertar Neon continuamente.

## POST /api/checks

`/api/checks` y `/api/checks/` se atienden igual: la aplicación desactiva la redirección de barra final para no emitir un `Location` con esquema `http` cuando el proceso corre detrás de un proxy TLS con `--no-proxy-headers`. Cualquier otra ruta con barra final sobrante devuelve 404.

En modo público (`PUBLIC_DEMO=true`, valor predeterminado), `url` solo acepta los cuatro escenarios canónicos de `https://demo.api-pulse.invalid`: `/echo`, `/status/404`, `/status/500` y `/redirect`. El esquema y el host se comparan sin distinguir mayúsculas; la ruta sí distingue. Se ejecutan con un transporte HTTP simulado dentro del proceso: **no hay resolución DNS ni conexión saliente**. El hostname `.invalid` es un identificador de escenario, no un sitio que el visitante deba abrir. El modo de desarrollo (`PUBLIC_DEMO=false`) conserva las URLs HTTP(S) arbitrarias y los controles previos, pero no debe desplegarse públicamente.

Ejecuta una solicitud y guarda su resultado. Ejemplo para un GET público:

~~~json
{
  "url": "https://demo.api-pulse.invalid/echo",
  "method": "GET",
  "headers": {},
  "body": {}
}
~~~

### Entrada

| Campo | Regla |
| --- | --- |
| url | String obligatorio, 1–2048 caracteres; en modo público debe ser un escenario canónico sin query, fragmento, credenciales ni puerto |
| method | GET, POST, PUT o DELETE; minúsculas se normalizan |
| headers | Objeto opcional/null; nombres no vacíos; valores escalares convertidos a string; null a string vacío. Nombres y valores deben usar ASCII imprimible: se rechaza con 422 cualquier carácter de control (incluidos `\r` y `\n`) o no ASCII, salvo el tabulador |
| body | Objeto opcional/null; listas y valores escalares se rechazan |

El `url` que se persiste y se devuelve nunca conserva credenciales: un prefijo `usuario:contraseña@` se elimina antes de guardar, aunque la solicitud saliente sí use la URL tal como se recibió. En modo público se guarda además la URL canónica del escenario, no la enviada.

GET no envía cuerpo. POST, PUT y DELETE envían `body` como JSON cuando procede. La validación del frontend permite objetos JSON, pero la validación final de cabeceras está en el backend.

### Respuesta ilustrativa

~~~json
{
  "check": {
    "id": 1,
    "url": "https://demo.api-pulse.invalid/echo",
    "method": "GET",
    "status_code": 200,
    "response_time_ms": 123,
    "created_at": "2026-09-14T00:00:00Z",
    "response_summary": "Demo GET /echo: HTTP 200",
    "success": true,
    "error_message": null
  },
  "response": {"method": "GET", "body": null},
  "response_headers": {"content-type": "application/json"}
}
~~~

Los valores anteriores son ilustrativos, no un resultado medido. En modo público, `response` proviene únicamente de escenarios controlados y el resumen histórico es fijo. El modo local puede devolver JSON, texto o null del destino y conserva su resumen recortado.

Solo se devuelven las cabeceras `content-type`, `content-length` y `server` si el destino las proporciona. El panel actual no las presenta por separado.

### Dos niveles de estado

| Caso | HTTP de API Pulse | check.success | check.status_code | Persistencia |
| --- | --- | --- | --- | --- |
| Destino responde 2xx | 200 | true | Código recibido | Sí |
| Destino responde 3xx/4xx/5xx | 200 | true | Código recibido | Sí |
| Destino bloqueado o URL rechazada por validador | 200 | false | null | Sí; en modo público se guarda una URL y mensaje genéricos |
| Fallo de conexión, timeout u otro error capturado de httpx | 200 | false | null | Sí |
| Entrada inválida según esquema | 422 | Sin check | Sin check | No |

Una respuesta 404 del destino no convierte la respuesta de API Pulse en HTTP 404. No se siguen redirecciones. Un bloqueo antes de conectar tiene tiempo null; un fallo durante la llamada suele incluir tiempo transcurrido.

En modo público, el cuerpo HTTP de creación no puede superar 16 KiB (413 antes de validar esquema), hay un techo de respuesta de 64 KiB, y los límites de admisión iniciales son 10 checks/minuto y 2 simultáneos por cliente, además de 60/minuto y 3 simultáneos globales (429 sin check persistido). El tope global de concurrencia se mantiene igual a la capacidad del pool de conexiones (`pool_size=2` más `max_overflow=1`): admitir más convertiría el excedente en una espera de `pool_timeout` y después un 500, en vez de un 429 honesto. El cliente se identifica por el par de conexión visto por ASGI; no se confía en `X-Forwarded-For`. T07 comprobó un 429 tras el proxy desde un cliente, pero no el aislamiento entre IP de visitantes distintos; el límite global permanece efectivo con un solo worker. El timeout configurado para el transporte de demo es 8 s, aunque los escenarios son locales y deterministas. Estos valores técnicos pueden ajustarse a la baja tras pruebas de capacidad.

Las excepciones no gestionadas y los fallos de base de datos pueden producir un 500; no hay un contrato uniforme implementado para todos ellos.

## GET /api/checks?limit=50

Devuelve un array de objetos `check` con los campos anteriores, ordenado por `created_at` descendente.

- Límite por defecto: 50; mínimo: 1; máximo: 100.
- Un límite fuera del rango produce 422.
- No devuelve el cuerpo completo ni `response_headers` históricos.
- No hay filtros por propietario, cursor, detalle por ID ni borrado individual.
- No requiere autenticación. En modo público todos ven el mismo historial: 50 por defecto, 100 máximo por API, 500 filas físicas como techo y 24 horas de visibilidad. Se elimina el exceso al iniciar, crear y listar; mientras el backend gratuito duerme, una fila vencida puede permanecer físicamente en Neon hasta el siguiente arranque o acceso, pero nunca se devuelve tras vencer.
- En modo público solo se conservan URL canónica del escenario, método, código, latencia, fecha, resultado y resumen seguro. Se eliminan las filas heredadas que no cumplan el formato seguro; no se guardan cuerpos, cabeceras, IP ni URLs arbitrarias.

## Restricciones del cliente saliente

- HTTP y HTTPS.
- Bloquea localhost, subdominios .localhost e IPs privadas, loopback, link-local, multicast, reservadas o no especificadas.
- Un hostname se rechaza si cualquiera de las IPs comprobadas pertenece a una categoría bloqueada.
- DNS y httpx realizan pasos separados; ver limitación en [estado actual](ESTADO_ACTUAL.md).
- El modo público no sale a la red, por lo que no existe una separación DNS/conexión explotable en esa ruta. El modo de desarrollo heredado sí conserva esa limitación y no debe publicarse.
- El modo de desarrollo conserva timeout httpx de 20 segundos y carece de cuotas/allowlist. No es un servicio seguro para exposición pública.

Los cambios aprobados para demo pública están registrados en D08–D10. El modo local conserva el contrato anterior para pruebas controladas, no para publicación.

## Verificación manual mínima

~~~powershell
Invoke-RestMethod http://localhost:8000/health

$payload = @{
  url = "https://demo.api-pulse.invalid/echo"
  method = "GET"
  headers = @{}
  body = @{}
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/api/checks -Method Post -ContentType "application/json" -Body $payload
Invoke-RestMethod http://localhost:8000/api/checks?limit=5
~~~

Este ejemplo corresponde a `PUBLIC_DEMO=true`: no realiza una solicitud externa. En Compose local (`PUBLIC_DEMO=false`), usar el destino controlado de `compose.integration.yml`; no usar servicios públicos ajenos para POST/PUT/DELETE.
