# Workflow: web-app
## Objetivo
Arquitectar desde bases conceptuales aplicaciones web asíncronas sólidas, escalables, responsivas y modulares asegurando una compatibilidad y sanidad sistémica global en ambos espectros. 

## Modelos por fase
- **Análisis basal:** (Sugerido por Estratega)
- **Lógica e interfaces crudas:** (Sugerido por Estratega)
- **Revisionismos sistémicos / QA general:** (Sugerido por Estratega)
- Ocurrencias Críticas/RFC Estructurales: (Sugerido por Estratega) (Solo bajo habilitación de operador y para dilemas irresolubles de infra).

## Agentes y orden de ejecución
`strategist` → `backend` → `frontend` → `ux` → `qa` → `docs`

## Paso a paso del flujo
1. El strategist forja un blueprint denso, estipulando frameworks tanto del servidor como cliente en `spec.md`. Alistar flag "blueprint listo".
2. Acude backend al relevo orquestador para diseñar la fontana primaria de datos. Cimentará views lógicas, APIs base e invoca fuertemente su `context7`. Una vez registrado como artefactos todos sus modelos, libera turno.
3. El frontend entra en juego al recibir especificaciones terminadas desde servidor para amarrar la UI. Si hay fallos en APIs, se comunica mediante flags escaladas la eventual refactorización a backend antes de culminar.
4. El revisor UX certifica únicamente front (interfaz visual) validando recorridos. 
5. Cede control formal al filtro del `qa` quien debe testear cohesión global cliente-servidor, seguridad subyacente de entorno y el escaneo de checksums mutuos.
6. Finalmente `docs` expende los repositorios analíticos: Documentación completa en `docs/frontend.md` y exhaustivo `docs/backend.md`.

## Criterios de completado
Ambos entornos operan interactuando impecablemente; los flujos están aislados debidamente. Endpoints responden estadios HTTP asimilables, sin arrastrar trazos codificados inoficiosos ni filtración cruda de data vital. Totalidad documental y chequeos firmados.

## Artefactos esperados en output/
- Las ramificaciones típicas front e back con subcarpetas para assets e interfaces programadas.
- Artefactos anexos de migración para las BD internas de la base principal operada.
- Bloques documentales totales en conjunto `specs.md` + todos los .md asociados en `/docs/`.
- Archivos `.env.example` referenciales en la capa nuclear de la APP excluyendo secretos.

## Condiciones de pausa / HITL
- Una discrepancia insalvable en la API que force al agente task a solicitar mudanzas severas de datos estructurales alterando significativamente el schema de base planeado o un RFC bloqueante.
- Fallos seriales de encriptación dictaminados sistemáticamente por el QA sin visos de resolución automática sensata.
