---
name: api-patterns
version: 1.0.0
type: backend
subtype: skill
tier: all
description: |
  Patrones de diseño de APIs REST con Django REST Framework para AIRON‑Cast.
  Cubre estructura de endpoints, métodos HTTP, códigos de estado, envelope JSend,
  autenticación JWT, paginación, versionado y pruebas.
  Activar cuando `backend_specialist` necesite diseñar o implementar endpoints.
  Trigger phrases: "construir API", "diseño de API", "endpoint REST",
  "seguridad API", "DRF", "Django REST", "response format", "JSend".
  No activar para lógica de negocio o diseño de modelos (usar `django-patterns`).
triggers:
  primary: ["construir API", "diseñar API", "endpoint REST", "DRF"]
  secondary: ["response format", "JSend", "autenticación JWT", "versionado API"]
  context: ["backend development", "API design"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - backend_specialist
last_used: 2026-06-05
scope: restricted
---

# API Patterns — AIRON‑Cast

Production-grade REST API design patterns using Django REST Framework.
All AIRON‑Cast backends must follow these standards for consistency.

**CRITICAL DIRECTIVE:** AIRON‑Cast strictly relies on **REST over HTTP** using
**Python & Django REST Framework**. Do not suggest GraphQL, tRPC, or Next.js
API routes. All frontend applications consume these standardized REST endpoints.

---

## 1. Core Principles

- **Resource-Oriented:** APIs structure data as resources (nouns), not actions.
  Endpoints represent collections or individual resources.
- **Statelessness:** Every request contains all information necessary to execute
  it. Session state is stored client-side (JWT) or via session tokens.
- **Predictability:** Endpoints, JSON payloads, and HTTP status codes follow
  strict conventions across all projects.
- **Security by Design:** All endpoints enforce authentication and authorization
  unless explicitly marked public.
- **Consistent Envelope:** Every response uses the JSend-inspired format defined
  in `references/response_format.md`.
- **Layered Architecture:** Views delegate to services; serializers handle
  validation; business logic lives in services.

---

## 2. Progressive Disclosure

When this skill activates, load reference files only when the workflow
requires them. `SKILL.md` never exceeds 500 lines.

| Scenario | Reference File |
|----------|----------------|
| Designing endpoints, resource naming, HTTP methods | `references/rest_best_practices.md` |
| Structuring JSON responses, error handling, pagination | `references/response_format.md` |
| Implementing DRF views, serializers, permissions | `references/django_drf_patterns.md` |

---

## 3. Mandatory Pre‑Flight Checklist

Before writing any API code:

- [ ] Endpoints use **plural nouns** (e.g., `/api/v1/users/`).
- [ ] HTTP method matches the intended action.
- [ ] URL includes API version (`/api/v1/...`).
- [ ] Response is wrapped in the **AIRON‑Cast envelope** (`status`, `data`, `message`).
- [ ] Authentication is applied: JWT for stateless frontends.
- [ ] Permissions are explicitly set on every view.
- [ ] All input is validated through a DRF **Serializer**.
- [ ] Error responses use proper HTTP status codes (4xx/5xx).
- [ ] Pagination is applied to list endpoints.
- [ ] CORS headers are configured if consumed by a different origin.
- [ ] Sensitive data (passwords, tokens) are never exposed.

---

## 4. Anti‑Patterns

- Returning `200 OK` with an error payload.
- Bypassing serializers and manually validating `request.data`.
- Using `POST` for read operations.
- Leaking stack traces to the client.
- Hardcoding URLs or credentials.
- Nesting resources beyond three levels.
- Returning raw ORM objects without serialization.

---

## 5. Versioning

APIs are versioned via the URL path (`/api/v1/`, `/api/v2/`). Never break
backward compatibility without a version bump.

---

## 6. Testing

Every endpoint must have tests. At minimum:
- Successful requests (200, 201, 204)
- Validation failures (400)
- Authentication/authorization failures (401, 403)
- Not found (404)
- Edge cases and pagination

Refer to `references/django_drf_patterns.md` for examples.

---

## 7. Documentation

All APIs must be documented using OpenAPI via `drf-spectacular`. The schema
should be exposed at `/api/schema/`.