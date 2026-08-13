---
name: api-patterns
description: "Patrones de diseño de APIs. Reglas para construir APIs RESTful estructuradas usando Django REST Framework y Python, respuestas JSend, seguridad y convenciones web A2LT."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# A2LT Universal API Patterns (Django REST Framework)

You are operating under the **api-patterns** skill. This skill dictates how all APIs within the A2LT ecosystem must be designed, structured, and implemented.

**CRITICAL DIRECTIVE:** The A2LT ecosystem strictly relies on **REST over HTTP** using **Python & Django REST Framework (DRF)**. You must NOT suggest or implement GraphQL, tRPC, or Next.js API routes. All frontend applications (Astro/Vanilla) consume these standardized REST endpoints.

## 1. Core Principles

- **Resource-Oriented:** APIs structure data as resources (nouns), not actions (verbs). Endpoints represent collections or individual resources.
- **Statelessness:** Every request contains all information necessary to execute it. Session state is stored client-side (JWT) or in the database via session tokens, never in-memory.
- **Predictability:** Endpoints, JSON payloads, and HTTP status codes follow strict, predictable conventions across all A2LT projects.
- **Security by Design:** All endpoints enforce authentication and authorization unless explicitly marked public. Sensitive data is never exposed in logs or responses.
- **Consistent Envelope:** Every response uses the JSend-inspired format defined in `response_format.md`.
- **Layered Architecture:** Views delegate to services or models; serializers handle validation; business logic lives in services or models.

## 2. Skill Activation and Progressive Disclosure

The **description** in the frontmatter is the sole trigger for this skill. It contains action verbs (“construir”, “diseño”, “seguridad”) and domain keywords. When this skill is activated, you MUST load the relevant reference files **only** when the workflow explicitly requires them.

**Strict Progressive Disclosure:** `SKILL.md` never exceeds 500 lines. Additional content resides in `references/`. Never consolidate knowledge into a single monolithic file.

## 3. Skill Reference Library

| Scenario / Task                                        | Required Reference File                                                     |
| ------------------------------------------------------ | --------------------------------------------------------------------------- |
| Designing endpoints, resource naming, HTTP methods     | `read_file: references/rest_best_practices.md`                              |
| Structuring JSON responses, error handling, pagination | `read_file: references/response_format.md`                                  |
| Implementing DRF views, serializers, permissions, etc. | `read_file: references/django_drf_patterns.md`                              |
| Configuring authentication (JWT, sessions)             | `read_file: references/django_drf_patterns.md` (see Authentication section) |
| Adding filtering, searching, ordering                  | `read_file: references/django_drf_patterns.md` (see Filtering section)      |
| Testing APIs                                           | `read_file: references/django_drf_patterns.md` (see Testing section)        |

_Note: If additional tactics are needed (e.g., advanced security, caching), supplementary references may be created in `references/` following the same deep‑domain pattern._

## 4. Mandatory Pre‑flight Checklist

Before writing any API code, verify the following:

- [ ] Endpoints use **plural nouns** (e.g., `/api/v1/users/`, not `/api/v1/getUser/`).
- [ ] HTTP method matches the intended action (GET for read, POST for create, etc.).
- [ ] URL includes API version (e.g., `/api/v1/...`).
- [ ] Response is wrapped in the **A2LT envelope** (`status`, `data`, `message`).
- [ ] Authentication is applied: JWT for stateless frontends, session for first‑party apps.
- [ ] Permissions are explicitly set on every view (at least `IsAuthenticated` or `AllowAny`).
- [ ] All input is validated through a DRF **Serializer** – never trust `request.data` directly.
- [ ] Error responses use proper HTTP status codes (4xx/5xx) and the envelope `fail` or `error`.
- [ ] Pagination is applied to list endpoints.
- [ ] CORS headers are configured if the API is consumed by a different origin.
- [ ] Sensitive data (passwords, tokens) are never exposed in logs or responses.

## 5. Anti‑Patterns to Avoid

- Returning `200 OK` with an error payload – always use correct status codes.
- Bypassing serializers and manually validating `request.data`.
- Using `POST` for read operations (exception: complex queries that exceed URL length limits).
- Leaking stack traces or internal server details to the client.
- Hardcoding URLs or credentials.
- Ignoring idempotency for `PUT` and `DELETE`.
- Nesting resources beyond three levels (e.g., `/users/1/posts/2/comments/3/likes/4`).
- Using function‑based views for complex logic – prefer class‑based views for reusability.
- Returning raw ORM objects without serialization.

## 6. Versioning Strategy

APIs are versioned via the URL path (e.g., `/api/v1/`, `/api/v2/`). This is the simplest and most explicit method. Never break backward compatibility without a version bump. Detailed versioning guidelines are in `rest_best_practices.md`.

## 7. Testing Requirements

Every endpoint must have corresponding tests (unit and integration) using Django's test framework or pytest. At minimum:

- Test successful requests (200, 201, 204).
- Test validation failures (400).
- Test authentication/authorization failures (401, 403).
- Test not found (404).
- Test edge cases and pagination.

Refer to `django_drf_patterns.md` for examples.

## 8. Documentation

All APIs must be documented using OpenAPI (via `drf-spectacular` or `drf-yasg`). The schema should be exposed at a standard endpoint (e.g., `/api/schema/`). Documentation must include examples of requests and responses.

## _(End of SKILL.md. Load the appropriate reference file for detailed implementation.)_
