---
name: architecture-documentation
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Plantillas y estándares para documentación técnica de proyectos AIRON‑Cast:
  README, Changelogs, documentación inline y guías de arquitectura.
  Activar cuando el agente `docs` necesite generar o estructurar documentación.
  Trigger phrases: "plantilla README", "cómo documentar esto", "architecture
  docs", "changelog format", "documentación de proyecto".
  No activar para copy de marketing o SEO (usar `writer`).
triggers:
  primary: ["plantilla README", "architecture docs", "documentación técnica"]
  secondary: ["changelog format", "guía de arquitectura", "cómo documentar"]
  context: ["project documentation", "technical writing"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - docs
last_used: 2026-06-05
scope: restricted
---

# Architecture Documentation — AIRON‑Cast

Templates and standards for producing consistent, high-quality technical
documentation across all AIRON‑Cast projects.

---

## 1. README Template

Every project must include a `README.md` at its root following this structure:

```markdown
# [Project Name]

## Overview
[One paragraph describing what the project does and who it is for.]

## Tech Stack
- Framework: [Astro | Django | etc.]
- Styling: [Tailwind CSS | etc.]
- Interactivity: [Alpine.js | etc.]

## Project Structure
[Directory tree with brief descriptions of key folders.]

## Setup & Installation
```bash
git clone [repo-url]
cd [project-name]
npm install
cp .env.example .env
# Fill in .env with required values
npm run dev
```

## Available Scripts
| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run test` | Run test suite |

## Deployment
[Instructions specific to the hosting platform.]

## Contributing
[Guidelines for team members contributing to this project.]
```

---

## 2. Changelog Format

Use [Keep a Changelog](https://keepachangelog.com/) format. Every release
must document:

```markdown
## [1.0.0] - YYYY-MM-DD

### Added
- Feature X for Y use case.

### Changed
- Refactored Z module for performance.

### Fixed
- Bug where A caused B under condition C.
```

---

## 3. Inline Code Documentation

- Python: docstrings for all public functions and classes (Google style).
- Astro components: JSDoc comment above each component describing its props
  and behavior.
- Configuration files: inline comments explaining non-obvious settings.

---

## 4. Architecture Decision Records (ADRs)

When documenting architectural decisions in `workspace/<slug>/adrs/`,
follow the standard AIRON‑Cast ADR template used by `journal-writer`.

---

## 5. Quality Standards

- All documentation must be in Spanish (headers and explanations) with
  code blocks in English.
- Avoid documenting implementation details in user-facing guides.
- Review documentation alongside code changes — outdated docs are worse
  than no docs.