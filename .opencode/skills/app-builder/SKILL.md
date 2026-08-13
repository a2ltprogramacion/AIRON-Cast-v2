---
name: app-builder
description: "Creador de proyectos Full-Stack A2LT. Construye la estructura base, inicializa Astro con Tailwind CSS para el Frontend, y configura Django REST Framework para el Backend. Define la arquitectura de carpetas estándar."
allowed-tools: Read, Write, Edit, Glob, Grep, Run
---

# A2LT Full-Stack App Builder

You are operating under the **app-builder** skill. Your primary directive is to scaffold and structure new A2LT applications from scratch.

A2LT applications strictly use a **decoupled monorepo (or polyrepo) architecture**:

- **Frontend:** Astro (SSG/SSR/PWA) + Vanilla JS + Tailwind CSS.
- **Backend:** Python + Django + Django REST Framework (DRF) + SQLite/PostgreSQL.

You must NEVER generate React (unless as an Astro Island for extreme edge cases), Next.js, Vue, Node.js (Express), or PHP backends.

## 1. Skill Reference Library

To bootstrap a project correctly, read the following reference files depending on the user's request:

| Task / Scenario                       | Required Reference File                      |
| ------------------------------------- | -------------------------------------------- |
| Structuring the root directory layout | `read_file: references/project_structure.md` |
| Bootstrapping the Astro Frontend      | `read_file: references/astro_setup.md`       |
| Bootstrapping the Django Backend      | `read_file: references/django_setup.md`      |

## 2. Bootstrapping Principles

- **Zero Magic, Full Control:** Prefer explicit configurations over boilerplate magic.
- **Strict Separation of Concerns:** Frontend code must never mix with Backend code. The only communication bridge is the REST API.
- **Progressive Enhancement:** Web applications behave as fast statically generated sites, hydrating interactivity only when necessary (Astro Island architecture).
- **Environment Parity:** Both `.env` configurations (Frontend/Backend) must be isolated but clearly documented in a universal `README.md`.

## 3. Mandatory Checklist for New Projects

When asked to "Initialize a new project", verify these steps:

- [ ] Read `project_structure.md` and create the base `frontend/` and `backend/` directories.
- [ ] Initialize the Astro project in `frontend/` with Tailwind CSS integrated.
- [ ] Initialize the Django project in `backend/` with `rest_framework` and `corsheaders` installed.
- [ ] Ensure `backend/.env` and `frontend/.env` templates exist.
- [ ] Write a `README.md` at the root explaining how to run both development servers concurrently.
