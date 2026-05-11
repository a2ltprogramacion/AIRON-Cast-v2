# Workflow: custom
## Objetivo
Proveedor el puente comodín metodológico genérico y altamente adaptable para resolver proyectos inusuales, requerimientos adiscionales urgentes preexistentes u soluciones corporativas atípicas no categorizables en los otros rubros principales que opera normalmente el sistema.

## Modelos por fase
- **Estructuración Genérica:** (Sugerido por Estratega)
- **Resolución Constante:** (Sugerido por Estratega)
- **Auditoría Final Estándar:** (Sugerido por Estratega)

## Agentes y orden de ejecución
`strategist` → (El strategist define dinámicamente los agentes necesarios según demanda especificada en el blueprint de `spec.md`) → `qa`

## Paso a paso del flujo
1. Empieza con un rol protagónico decisivo el analista puro `strategist`, evaluando los pro y contra de la solución particular u script solicitado, identificará recursos y delimita ágilmente el blueprint base estableciendo por sí mismo qué agentes transitarán en este workflow (ej. si es un script solitario invocará únicamente `backend`).
2. El engranaje principal del frame dictamina e inyectará las ordenes sucesivas iterando con `orchestrator` la asignación paulatina de cada actor designado. Los actores responden a su estándar operativo general para programar o componer respetando íntegramente `manifest.json`.
3. Sea el actor de programación interviniente que fuere, su ciclo de persistencia es inamovible: (Leer estatus, registrar checkpoint inminente previo trabajo, ejecutar y reportar artefactos codificados con checksum a memoria en base de datos sqlite).
4. Forzosamente como último obstáculo y sin dilación, el encaramado de jerarquía Sonnet del `qa` barre cualquier rastro de la petición comprobando cumplimiento textual y sin fisuras del global rule `rules/global.md`.

## Criterios de completado
Se ejecuta y concreta exitosamente el dictamen particular estipulado inicialmente en spec. Se resguardaron en persistencia base los metadatos y en formato de salida las piezas en su justa y prolija medida y composición. Trazabilidad total del workflow en historial de logs.

## Artefactos esperados en output/
- Un repositorio mínimo alojando lo desarrollado, el respectivo setup particular dentro de `output/[proyecto]/src/`.
- Un imperativo bloque mínimo documental conformado por lo general en el `README.md` resumiendo cómo integrar a la máquina destino el requerimiento custom desarrollado además del QA report tradicional emitido obligatoriamente.

## Condiciones de pausa / HITL
- Se escala de modo vertiginoso si la petición entraña una intrusión fuera de foco al framework e incurre en jurisdicciones restringidas de las esferas del control maestro nativo o demanda accesibilidad directa a credenciales físicas.
