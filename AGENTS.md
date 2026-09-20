# Instrucciones del proyecto API Pulse

## Contexto y objetivo

El usuario quiere cerrar API Pulse como proyecto de portafolio con despliegue público y continuar su desarrollo con GPT-5.6. Trabaja en español; conserva el idioma y estilo actuales de la interfaz salvo que la tarea pida cambiarlos.

## Lectura al comenzar

1. `docs/CONTINUIDAD_GPT_5_6.md`: resumen y siguiente tarea.
2. `docs/ESTADO_ACTUAL.md`: evidencia, límites y fallos conocidos.
3. `docs/PLAN_DE_CIERRE.md`: orden de trabajo y aceptación.
4. Lee requisitos, decisiones, arquitectura o API según la tarea.

El código y las pruebas muestran el comportamiento actual. Los requisitos describen lo que debe alcanzarse. En `docs/DECISIONES.md`, distingue decisiones confirmadas, elecciones observadas en código y propuestas pendientes. No conviertas propuestas en acuerdos del usuario.

## Antes de editar

- Confirma la raíz y ejecuta `git status --short --branch`.
- Conserva los cambios ajenos que encuentres.
- La ruta histórica `nwep` ya no existe en el equipo revisado. La carpeta real es `api-pulse`; no crees un repositorio vacío en la ruta antigua.
- Completa un bloque del plan por vez; evita rediseños ajenos al objetivo.
- No cambies dependencias o contratos solo para hacer desaparecer una comprobación fallida.

## Contratos que deben conservarse salvo cambio explícito

- Métodos: GET, POST, PUT y DELETE. Cuerpo JSON objeto; GET no envía cuerpo.
- `success` representa respuesta HTTP recibida, incluso para 4xx/5xx.
- Un rechazo de seguridad se persiste como comprobación fallida y actualmente responde HTTP 200 desde API Pulse; una entrada inválida por esquema responde 422.
- Historial: orden descendente por fecha, límite por defecto 50 y máximo 100.
- Destinos locales/privados bloqueados y redirecciones desactivadas.
- No registres credenciales de APIs reales en documentación, capturas ni fixtures.
- Conserva las protecciones de solicitudes salientes al diseñar el despliegue.

## Validación y operación

Consulta comandos exactos en `docs/DESARROLLO_Y_VALIDACION.md`. Para cambios de backend, ejecuta pytest y Ruff; para frontend, build y lint, más las pruebas relevantes al comportamiento cambiado. Para infraestructura, valida Compose y el arranque que corresponda. Las pruebas del cliente HTTP deben usar mocks o destinos controlados.

No uses servicios públicos ajenos para comprobar POST, PUT o DELETE. En Docker respeta los contenedores de otros proyectos; usa puertos alternativos cuando sea necesario. No elimines volúmenes para resolver fallos de arranque.

No declares listas la aplicación, la CI o la publicación sin evidencia. Informa por separado comprobaciones aprobadas, fallidas y no ejecutadas. Un test que no llama al código ni verifica resultados no demuestra cobertura.

## Cierre de cada bloque

- Actualiza estado, tareas y decisiones afectadas.
- Registra comandos, resultados y limitaciones de validación.
- Deja una siguiente acción concreta.
- La finalización requiere la lista de aceptación del portafolio público en el plan.
