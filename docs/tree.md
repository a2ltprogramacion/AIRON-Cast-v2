AIRON-Cast/                             # Raíz del ecosistema
│
├── AGENTS.md                           # Constitución global: reglas, ciclo de agentes, STOP_LOSS
├── manifest.json                       # Contratos de 11 agentes con permisos, skills y MCPs
├── requirements.txt                    # Dependencias: pydantic, dotenv, pytest, pyyaml, jsonschema
├── start_airon.bat                     # Script de inicio integral: venv + dependencias + init + dashboard
│
├── .agents/                            # Agentes, skills, workflows
│   ├── profiles/                       # 11 perfiles de agentes (.md)
│   │   ├── orchestrator.md             # Dispatcher central: Round-Robin, contexto, STOP_LOSS, workflows
│   │   ├── pm.md                       # Product Manager: user stories, tickets, backlog priorizado
│   │   ├── requirements_architect.md   # Arquitecto de especificaciones: REQUIREMENTS.md, BACKLOG.md, ADRs
│   │   ├── ux-ui_specialist.md         # Director estético: design tokens, wireframes, checklist UX
│   │   ├── writer.md                   # Copywriter & SEO: copy, meta tags, secuencias de email
│   │   ├── frontend_worker.md          # Implementador UI: componentes Astro, Tailwind, Alpine.js
│   │   ├── backend_specialist.md       # Desarrollador Django/DRF: modelos, serializers, endpoints, tests
│   │   ├── tester.md                   # QA Test Engineer: ejecuta tests, lint, smoke tests, emite veredictos
│   │   ├── qa_auditor.md               # Juez de calidad: revisa artefactos, checksums, checklist UX, veredictos
│   │   ├── docs.md                     # Technical Writer: README, API reference, guías de usuario
│   │   └── meta_factory.md             # Arquitecto del ecosistema: audita, parchea, crea agentes y skills
│   │
│   ├── skills/                         # 25 skills modulares
│   │   ├── a2lt-brand-kit/             # ADN visual A2LT: CSS, navbars, SVGs, efectos Neón/Platinum
│   │   ├── agent-creator-pro/          # Genera nuevos perfiles de agentes con scripts en tools/
│   │   ├── agent-skill-scout/          # Busca skills y agentes en repositorios externos (skills.sh, GitHub)
│   │   ├── api-patterns/               # Patrones REST con DRF: endpoints, serializers, autenticación, JSend
│   │   ├── architecture-documentation/ # Plantillas README, Changelogs, documentación inline
│   │   ├── astro-landing-kit/          # Componentes Astro predefinidos y baseline de proyecto
│   │   ├── audit-code-review/          # Auditoría de código: funcionalidad, seguridad, lint, clean code, tests
│   │   ├── brainstorming/              # Propuestas de diseño con patrones antes de commitear
│   │   ├── context7-resolver/          # Consulta documentación oficial actualizada vía MCP context7
│   │   ├── database-architecture/      # Diseño de schemas, índices, migraciones y optimización SQL
│   │   ├── django-patterns/            # Patrones Django: modelos, QuerySets, services, signals, N+1
│   │   ├── geo-optimization/           # GEO para motores RAG: citaciones, datos originales, entidades
│   │   ├── institutional-memory/       # Memoria institucional interna: ADRs y patrones vía FTS5
│   │   ├── journal-writer/             # Escribe entradas estructuradas en el journal del proyecto
│   │   ├── manifest-updater/           # Gestiona manifest.json: add, update, deprecate, validate
│   │   ├── notebooklm-mcp-integration/ # Conexión con Google NotebookLM vía MCP: consulta, audio, fuentes
│   │   ├── seo-content-strategy/       # Estrategia de contenidos: clusters, LSI, densidad KW, refresh
│   │   ├── seo-onpage-architecture/    # On-page SEO: meta tags, schema, featured snippets, E-E-A-T
│   │   ├── seo-technical-audit/        # Auditoría técnica: indexación, Core Web Vitals, score 0-100
│   │   ├── skill-creator-pro/          # Genera nuevas skills modulares con pipeline de validación
│   │   ├── stitch-designer/            # Prototipado UI vía StitchMCP: diseño y edición de pantallas
│   │   ├── tailwind-architecture/      # Tailwind v4: CSS-first, @theme, Container Queries, tokens
│   │   ├── testing-tdd-architecture/   # TDD con Pytest, Vitest, Playwright; cobertura >80%
│   │   ├── ui-ux-pro-max/              # Base de datos de diseño: paletas, tipografías, arquetipos
│   │   └── yaml-validator/             # Valida frontmatter YAML de skills y agentes contra schema
│   │
│   └── workflows/
│       └── system.md                   # Protocolo de auto-mantenimiento: detección → parche → deploy
│
├── core/                               # Módulos nucleares del motor
│   ├── airon_cast_schema.sql           # Esquema completo: tablas, índices, vistas, triggers, FTS5
│   ├── memory_manager.py               # Único punto de acceso a SQLite: contexto, checkpoints, ADRs
│   ├── trajectory_compressor.py        # Comprime historial de ejecución para ventanas de tokens
│   ├── orchestrator.py                 # Motor de ejecución Round-Robin con cola de tareas
│   ├── api_router.py                   # Caché de respuestas + notificaciones de cambio de modelo
│   ├── checksum_verifier.py            # Verificación de integridad SHA256 de artefactos
│   ├── hitl_gateway.py                 # Escalación y resolución de intervención humana (HITL)
│   └── validator.py                    # Validación de output de agentes contra schemas
│
├── tools/                              # Scripts CLI auxiliares
│   ├── init_ecosystem.py               # Inicializa central_intelligence.db desde schema.sql
│   ├── db_ops.py                       # Operaciones CLI: proyectos, tareas, checkpoints, model-usage
│   ├── dashboard_server.py             # Servidor HTTP en localhost:8765 para el panel de monitoreo
│   ├── generate_agent_profile.py       # Genera perfiles .md de agentes desde argumentos CLI
│   ├── validate_agent_profile.py       # Valida perfiles .md contra el estándar AIRON‑Cast
│   ├── run_project.py                  # ✅ Ejecuta el ciclo Round‑Robin automáticamente
│   └── list_agents.py                  # Lista agentes con upstream, downstream y objetivo
│
├── dashboard/
│   └── index.html                      # Panel de monitoreo con proyectos, tareas y model usage
│
├── docs/
│   ├── ECOSYSTEM_EVOLUTION.md          # Guía de evolución, contratos, versionado y backlog histórico
│   └── tree.md                         # Este archivo: árbol del ecosistema con descripciones
│
├── rules/
│   ├── ceo.md                          # Límites operativos: $0, 16GB RAM, escritura, STOP_LOSS
│   └── jurisdiction.md                 # Matriz RBAC: qué puede leer/escribir/ejecutar cada agente
│
├── workspace/                          # Entornos aislados por proyecto
│   └── .gitkeep                        # Vacío, listo para proyectos piloto
│
└── output/
    └── .gitkeep                        # Vacío, listo para salidas finales