# Walkthrough: Fusión de Agentes y Procesamiento de Skills

## Resumen

Se fusionaron 12 agentes, se materializaron 61 skills, y se actualizaron todos los perfiles de agentes con referencias a skills reales en `.agent/skills/`.

## Fase 1: Agentes (13 total — 13/13 VALID ✅)

### MERGE (7 archivos actualizados)

| Archivo | Fuente |
|---------|--------|
| [strategist.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/strategist.md) | `agent_architect` |
| [orchestrator.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/orchestrator.md) | Template unificado |
| [backend.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/backend.md) | `agent_backend` |
| [frontend.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/frontend.md) | `agent_frontend` |
| [ux.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/ux.md) | `agent_uxui` |
| [docs.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/docs.md) | `agent_docs` |
| [qa.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/qa.md) | `agent_reviewer` |

### NEW (6 archivos creados)

| Archivo | Rol |
|---------|-----|
| [pm.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/pm.md) | Product Manager |
| [forge.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/forge.md) | Forge Engineer |
| [tester.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/tester.md) | QA Test Engineer |
| [ghl.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/ghl.md) | GoHighLevel Specialist |
| [infra.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/infra.md) | Infrastructure & DevOps |
| [writer.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/writer.md) | Copywriter & SEO |

---

## Fase 2: Skills (61 skills en `.agent/skills/`)

192 archivos copiados de `docs/skills/` a `.agent/skills/`. Skills existentes preservadas (9 originales + 52 nuevas).

### Mapeo por Agente

| Agente | # Skills | Principales |
|--------|----------|-------------|
| **Strategist** | 8 | architecture, database-architecture, api-patterns |
| **Backend** | 4 | django-patterns, async-python-patterns, clean-code |
| **Frontend** | 7 | tailwind-architecture, astro-project-standards, stitch-designer |
| **UX** | 4 | ui-ux-pro-max, art-direction, a2lt-brand-kit |
| **QA** | 3 | audit-code-review, audit-lint-validate, debugging-and-profiling |
| **Tester** | 1 | testing-tdd-architecture |
| **Docs** | 2 | architecture-documentation, geo-optimization |
| **Writer** | 3 | seo-content-strategy, seo-onpage-architecture, seo-technical-audit |
| **GHL** | 7 | ghl-master-skill, ghl-list-ai-agents, ghl-workflow-analyzer |
| **Infra** | 5 | deployment-procedures, bash-linux, windows-powershell-architecture |
| **Forge** | 11 | agent-creator-pro, skill-creator-pro, brainstorming, journal-writer |
| **Transversales** | 5 | context7-resolver, mcp-integrator, security-vulnerability-scanner |

Mapa completo: [skill_agent_map.md](file:///C:/Users/Argenito/.gemini/antigravity/brain/39a95e35-ee36-4c8d-8a53-06e9bad91ddb/skill_agent_map.md)

---

## Verificación

```
validate_agent_profile.py → 13/13 VALID, 0 fallidos
Skills en .agent/skills/  → 61 directorios verificados
```
