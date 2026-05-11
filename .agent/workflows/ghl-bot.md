# Workflow: ghl-bot
## Objetivo
Establecer la directriz obligatoria para la construcción de Bots Conversation IA y Voz IA embebidos en el entorno GoHighLevel. Integra la generación de prompts infalibles de alto contexto y la estructuración de la Base de Conocimientos que el bot asimilará.

## Modelos por fase
- **Arquitectura de Bot y Contextos:** (Sugerido por Estratega)
- **Redacción de Prompt:** (Sugerido por Estratega)
- **Verificación Sistémica:** (Sugerido por Estratega)

## Agentes y orden de ejecución
`strategist` → `redactor_de_prompts` → `qa`

## Paso a paso del flujo
1. El `strategist` levanta un mapeo integral de las aspiraciones del cliente en el blueprint o `spec.md`, incluyendo limitantes de la empresa objetivo, catálogos bases y personalidades esperadas.
2. Interviene de lleno el agente `redactor_de_prompts` que moldeará minuciosamente un prompt estructurado ateniéndose indefectiblemente a las 9 secciones estándar impuestas por el operador (Contexto, Rol, Objetivos, Técnicas, Cartera, Restricciones, Acciones Obligatorias, Diagrama, Ejemplos).
3. Configurando localmente los manuales FAQs para embutirlos en Base de Conocimiento nativa de la subcuenta (usando `skill/ghl` si lograse conectividad).
4. Actúa como dique final el filtro del estrato terminal `qa`, forzando el repaso de las 9 secciones para dar el `approved_for_delivery`. Produce consecuentemente el respectivo reporte final `docs/qa-report.md`.

## Criterios de completado
Se generó indiscutiblemente un artefacto base prompt de formato plano con las 9 áreas innegociables establecidas cubiertas profundamente, carece de alucinaciones sobre productos o servicios que la empresa local no posee. Creados archivos base Q&A formativos para GoHighLevel Knowledge Base limpiamente indexados.

## Artefactos esperados en output/
- Carpeta `output/[proyecto]/bot/` que contiene un archivo primordial `prompt-master.txt` o markdown, al igual que los `.csv` o `.json` listos para carga FAQs.
- El clásico listado e impreso certificante de calidad `docs/qa-report.md`.

## Condiciones de pausa / HITL
- Si de forma rotunda el `qa` se topa con un prompt irresoluble en el que las 9 secciones básicas coexisten solapadas, redundantes o incompletas de facto, obligando al HITL al operador.
