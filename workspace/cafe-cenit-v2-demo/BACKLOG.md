# Backlog — cafe-cenit-v2-demo

> Proyecto de prueba del ecosistema multi-agente. Solo 3 tareas para validar el Round-Robin end-to-end.

| ID | Tarea | Agente | Priority | Dependencies | Status |
|---|---|---|---|---|---|
| T01 | Definir paleta cálida y design tokens | ux-ui_specialist | 10 | - | READY |
| T02 | Implementar landing Astro 1 página | frontend_worker | 8 | T01 | READY |
| T03 | Auditoría QA final + verdict | qa_auditor | 5 | T02 | READY |

---

## T01: Design tokens

**Agente:** ux-ui_specialist
**Descripción:** Crear `src/styles/design-tokens.json` con paleta cálida (marrones, crema, naranja suave) y tipografía (Fraunces + Inter). Publicar ADR-001.

**Criterios de aceptación:**
- [ ] `design-tokens.json` con ≥6 colores y 2 tipografías
- [ ] ADR-001 registrado en la DB vía memory_manager

## T02: Implementación

**Agente:** frontend_worker
**Descripción:** Crear `src/pages/index.astro` con un hero simple que use los tokens de T-01. Solo HTML + estilos inline. Sin JS.

**Criterios de aceptación:**
- [ ] `index.astro` renderiza H1 + párrafo + CTA
- [ ] Estilos usan exclusivamente los tokens de T-01
- [ ] Sin HEX sueltos

## T03: Auditoría

**Agente:** qa_auditor
**Descripción:** Verificar que los tokens se aplican correctamente y que no hay violaciones.

**Criterios de aceptación:**
- [ ] Reporte de QA con verdict PASSED
- [ ] Sin issues CRITICAL
