---
name: architecture-patterns
description: "Patrones de Arquitectura A2LT. Dominio del Service Layer Pattern en Django para aislar lógica de negocio y la Arquitectura de Islas en Astro para el frontend híbrido."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# A2LT Architecture Patterns

You are operating under the **architecture-patterns** skill. This dictates how business logic and UI components are structurally organized within A2LT applications.

**CRITICAL DIRECTIVE:** A2LT relies heavily on Django's ORM. Therefore, strict "Clean Architecture" or "Domain-Driven Design (DDD)" where entities have absolutely no framework dependencies is a **pragmatic anti-pattern**. Instead, we use a **Service Layer Architecture** for the backend, and **Islands Architecture** for the frontend.

## 1. Skill Reference Library

Read the relevant architecture pattern depending on the tier you are working on:

| Architecture Tier                         | Required Reference File                         |
| ----------------------------------------- | ----------------------------------------------- |
| Django Backend (Business Logic Isolation) | `read_file: references/django_service_layer.md` |
| Astro Frontend (Hydration & UI Structure) | `read_file: references/astro_islands.md`        |

## 2. Core Architectural Philosophy

- **Fat Models, Helper Services, Thin Views:** Django Views (or DRF ViewSets) must ONLY handle HTTP request parsing and response formatting. All raw business logic belongs in a `/services.py` layer or on the Model itself.
- **HTML/CSS over Heavy JavaScript:** In the Astro frontend, UI components must be rendered statically on the server by default. Client-side JavaScript (React/Vanilla) is strictly quarantined to interactive "Islands".

## 3. Anti-Patterns to Avoid

- **Fat Controllers:** Writing 100+ lines of business logic inside a Django `APIView` or `ViewSet`.
- **Anemic Models:** Using Django Models just as data bags without any methods.
- **SPA Defaulting:** Building a Single Page Application in React when Astro SSR could have delivered the same page 10x faster.
- **Over-Engineering:** Implementing DDD Repositories and Interfaces just to wrap Django's heavily optimized ORM `QuerySets`.

_(End of instructions. Read the references to proceed)._
