# Workflow: web-design
## Objetivo
Diseñar, estructurar e implementar páginas web y landig pages, centrándose vigorosamente en impacto visual, eficiencia, y conversión; manteniendo fidelidad nativa con layouts limpios. 

## Modelos por fase
- **Análisis inicial:** (Sugerido por Estratega)
- **Desarrollo (HTML/CSS/JS):** (Sugerido por Estratega)
- **Revisión estática y QA final:** (Sugerido por Estratega)

## Agentes y orden de ejecución
`strategist` → `frontend` → `ux` → `docs` → `qa`

## Paso a paso del flujo
1. El strategist perfila en el `spec.md` la visión base e identifica de inmediato la limitante temporal y estética determinando la directiva a usar. Se levanta "blueprint listo".
2. Seguidamente, Orchestrator cede el hilo de desarrollo directamente sobre taskforce `frontend`, el cual procede a articular físicamente los marcos basándose si fue requerido o no en invocaciones concretas a `StitchMCP`.
3. Terminada la labor del HTML/CSS, orchestrator releva el chequeo al taskforce `ux`. UX elabora un checklist crítico y formal. Si levanta issues severos devuelve el ticket, si da `approved_for_next`, pasa etapa.
4. Finalizados los componentes y su aspecto interactivo, `docs` asimila el código frontal originando todos sus comentarios base, manuales orientativos operacionales en `docs/frontend.md`  y su `README.md` estricto en la raíz del proyecto.
5. El flujo fenece irrevocablemente en `qa` donde un Sonnet evalúa las discrepancias y los checksum de validación por directorio garantizando no existir desbalances sintácticos. 

## Criterios de completado
La landig funciona lúdica e íntegramente móvil; sin enlaces huérfanos de marcador visual y carece imperativamente de cualquier tipo de bloque tipo "# TODO". Todos los emuladores estáticos de JS fluyen ininterrumpidamente, y la respuesta auditada en consola lanza limpieza total.

## Artefactos esperados en output/
- `spec.md`, `state.json` del workflow.
- Archivos nucleares front end HTML, directorios /css/ y /js/ limpios en base.
- Archivos documentales: `docs/frontend.md` y un `README.md` inicial.
- Auditorías estáticas finalizadas `ux-review.md` y el infaltable `qa-report.md`.

## Condiciones de pausa / HITL
- El `ux` rechaza obstinadamente un layout estipulando deficiencias de conversión que requieren visión externa. 
- Inoperancia técnica flagrante del CSS no solventada en 3 intentos en taskforce.
