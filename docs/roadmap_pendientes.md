# Roadmap de Pendientes: AIRON-Cast Core

Este documento consolida los puntos ciegos y tareas Técnicas identificadas tras la fusión de agentes y skills.

## 1. Refactorización de Skills & Referencias
Hay un desajuste entre los nombres de carpetas en `.agent/skills/` y las referencias en los perfiles `Assigned Skills`.
- [ ] **Limpieza de Referencias:** Actualizar `Rules` y `Processes` en los agentes para que usen los nombres kebab-case definitivos (ej: cambiar `skill_stitch_design` por `stitch-designer`).
- [ ] **Materialización de Sub-actions:** Crear las skills que son solo referencias lógicas pero no tienen carpeta (ej: `skill_materialize_files`, `skill_manage_devserver`, `skill_forge_health_check`).
- [ ] **Limpieza de Huérfanos:** Asignar o documentar el propósito de skills como `red-team-operations` y `mcp-integrator`.

## 2. Matriz de Jurisdicción (Orquestación)
- [ ] **Sincronización `manifest.json`:** Actualizar el manifiesto global para incluir los 6 nuevos agentes y sus 52 nuevas skills mapeadas.
- [ ] **Integridad en SQLite:** Asegurar que la tabla `agents` y `skills` en `core/airon.sqlite` refleje la realidad del sistema de archivos para que el Orquestador pueda validar la jurisdicción en tiempo real.
- [ ] **Validación de Capacidad:** Implementar un hook en `Orchestrator` que rechace tareas si el agente asignado no tiene la skill en su "toolbox" del manifiesto.

## 3. RAG & Memoria (Core)
- [ ] **Integración ChromaDB:** Implementar el `ChromaClient` dentro de `core/` para permitir la indexación de decisiones arquitectónicas (`project_context`).
- [ ] **Vectores de Memoria:** Completar la lógica de `rag-indexer` y `rag-query` para que los agentes puedan consultar la memoria histórica de otros proyectos (`notebooklm` local).
- [ ] **Sincronización SQLite + Chroma:** Mantener el link entre el ID de tarea en SQLite y su embedding en ChromaDB para búsquedas semánticas de errores comunes.

## 4. Infraestructura de Ejecución
- [ ] **Script de Materialización:** Desarrollar el script que toma los artefactos de la base de datos y los escribe físicamente en el directorio `output/[proyecto]/` con verificación de checksum.
- [ ] **Gestión de DevServer:** Implementar el control robusto de procesos para iniciar/detener el servidor de desarrollo Django durante los tests.

## 5. Auditoría & Calidad
- [ ] **Refactorización de Verificador de Checksums:** Asegurar que el `ChecksumVerifier` se ejecute automáticamente antes de cada materialización (`infra`).
- [ ] **Esquema de Output Estricto:** Finalizar los schemas JSON en `manifest.json` para cada skill nueva para permitir validación automática de outputs.
