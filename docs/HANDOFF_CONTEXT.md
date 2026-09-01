# AIRON-Cast — Documento de Traspaso de Sesión
> **Estado:** Activo | **Versión:** 2.0.0 (Consolidada) | **Operador:** Argenis @ A2LT Soluciones

---

## ¿Qué es AIRON-Cast?

**AIRON-Cast: Blacksmithing Development Framework**  
A.I.R.O.N. = Artificial Intelligence Reinforced Orchestration Network

Framework de orquestación de desarrollo profesional construido sobre Antigravity (entorno local del operador). El operador es **Argenis** — desarrollador y consultor (A2LT Soluciones).

Cubre: diseño web (Astro + Tailwind v4), apps web/escritorio, integración y administración GoHighLevel, arquitectura backend (Django + DRF), y soluciones personalizadas con presupuesto $0.

---

## Stack Técnico y Entorno

- **Entorno:** Antigravity (VSCode fork, local)
- **Modelos disponibles:** Gemini Flash / Pro, Claude Sonnet / Opus Thinking, modelos gratuitos vía OpenRouter/Groq y Ollama local.
- **MCPs activos:** StitchMCP, context7, notebooklm, cloudflare, filesystem, github
- **Persistencia:** SQLite (`central_intelligence.db`) con soporte FTS5
- **Lenguaje core:** Python 3.x (FastAPI/Django/Astro stack)
- **Modo de Operación:** Cero presupuesto obligatorio ($0 Budget Fallback) + Round-Robin determinista.

---

## Estructura Consolidada del Proyecto

```
AIRON-Cast/
├── AGENTS.md                    ✅ Constitución del sistema unificado
├── MANUAL_DE_OPERACION.md       ✅ Guía paso a paso para operar el ecosistema
├── MISSION_CONTROL.md           ✅ Bitácora de hitos y lecciones aprendidas
├── manifest.json                ✅ Contratos de jurisdicción por agente
├── requirements.txt             ✅ Dependencias Python
├── .gitignore                   ✅ Exclusiones configuradas
├── central_intelligence.db      ✅ SQLite + FTS5 memoria central
│
├── .agent/                      ✅ Personalizaciones y skills canónicas
│   ├── agents/                  ✅ 13 perfiles de agentes
│   ├── skills/                  ✅ 60 skills de desarrollo
│   ├── workflows/               ✅ 8 workflows operativos
│   └── scripts/                 ✅ Utilidades de skills
│
├── .agents/                     ✅ Mirror idéntico para Antigravity IDE
│   ├── profiles/                ✅ 13 perfiles de agentes
│   ├── skills/                  ✅ 60 skills de desarrollo
│   └── workflows/               ✅ 8 workflows operativos
│
├── core/                        ✅ Motor de ejecución determinista
│   ├── airon_cast_schema.sql    ✅ DDL + FTS5 + triggers
│   ├── memory_manager.py        ✅ Punto único de lectura/escritura a DB
│   ├── orchestrator.py          ✅ Motor de despacho Round-Robin
│   ├── service_supervisor.py    ✅ Watchdog y health checks vía socket
│   ├── api_router.py            ✅ Fallback chain para modelos $0
│   ├── checksum_verifier.py     ✅ Integridad de artefactos SHA256
│   ├── hitl_gateway.py          ✅ Notificación de escalación operador
│   ├── trajectory_compressor.py ✅ Compresión de trayectoria
│   └── validator.py             ✅ Validación de outputs
│
├── tools/                       ✅ CLIs de operación y dashboards
│   ├── airon_executor.py        ✅ CLI principal de tareas y despacho
│   ├── airon_nl.py              ✅ Interfaz de lenguaje natural
│   ├── airon_supervisor.py      ✅ Servicio supervisor continuo
│   ├── dashboard_server.py      ✅ Servidor web del dashboard local
│   ├── stop_supervisor.py       ✅ Detención limpia de servicios
│   ├── init_ecosystem.py        ✅ Bootstrap de la base de datos
│   └── ...
│
├── dashboard/                   ✅ Frontend Web local (puerto 8765)
│   └── index.html
│
├── rules/                       ✅ Reglas de gobernanza
│   ├── global.md
│   ├── ceo.md
│   └── jurisdiction.md
│
├── test/                        ✅ Suite de pruebas automatizadas
│   ├── test_core_integration.py
│   └── test_memory_manager.py
│
├── docs/                        ✅ Documentación técnica de alto valor
│   ├── ECOSYSTEM_EVOLUTION.md
│   ├── EXECUTOR_MODE.md
│   ├── HANDOFF_CONTEXT.md
│   └── ghl_api_v2_panorama.md
│
└── workspace/                   ✅ Proyectos de desarrollo activos
```

---

## Decisiones de Arquitectura Consolidadas

1. **SQLite (`central_intelligence.db`):** Corre local sin dependencias de servidores.
2. **`memory_manager.py`:** Único punto de escritura a la DB — ningún agente ni script escribe directamente sin pasar por este módulo.
3. **Round-Robin con Pizarra Compartida:** El orquestador mantiene la cola secuencial y el contexto se transfiere en cada turno.
4. **Jurisdicción Estricta (`manifest.json`):** Cada rol tiene permisos explícitos de lectura, escritura y MCPs.
5. **Supervisor Autónomo Portable:** Watchdog sin dependencias del SO que monitoriza y auto-recupera servicios locales.
6. **Integridad de Artefactos:** Checksum SHA256 para prevenir manipulaciones fuera de ciclo.
