# REST Best Practices

This reference defines the URI design, HTTP method usage, status codes, and other RESTful conventions for all A2LT APIs.

## 1. Resource Naming Conventions

- **Use nouns, not verbs.**
  ✅ `/api/v1/users/`
  ❌ `/api/v1/getUsers/`

- **Use plural resource names consistently.**
  ✅ `/api/v1/users/123`
  ❌ `/api/v1/user/123`

- **Use kebab‑case for multi‑word resources.**
  ✅ `/api/v1/user-profiles/`
  ❌ `/api/v1/user_profiles/` or `/api/v1/userProfiles/`

- **Nest resources to show relationships, but keep it shallow (max 3 levels).**
  ✅ `/api/v1/users/123/posts/`
  ✅ `/api/v1/users/123/posts/456/comments/`
  ❌ `/api/v1/users/123/posts/456/comments/789/likes/`

- **Avoid mixing singular and plural.** If a resource is a collection, always plural. The singleton (detail) is implied by the identifier.

## 2. HTTP Methods and Semantics

| Method     | CRUD Action           | Safe | Idempotent | Request Body          | Response Body           |
| ---------- | --------------------- | ---- | ---------- | --------------------- | ----------------------- |
| **GET**    | Read                  | Yes  | Yes        | No                    | Resource representation |
| **POST**   | Create                | No   | No         | Resource data         | Created resource        |
| **PUT**    | Replace (full update) | No   | Yes        | Full resource data    | Updated resource        |
| **PATCH**  | Partial update        | No   | No         | Partial resource data | Updated resource        |
| **DELETE** | Delete                | No   | Yes        | No                    | Usually empty (204)     |

### Idempotency Notes

- `PUT` and `DELETE` are idempotent: multiple identical requests have the same effect as one.
- `POST` is **not** idempotent; create duplicate resources unless you implement idempotency keys.
- `GET`, `HEAD`, `OPTIONS`, `TRACE` are safe and idempotent.

## 3. HTTP Status Codes

Always use the most specific status code.

### 2xx Success

- `200 OK` – Standard success for GET, PUT, PATCH.
- `201 Created` – Success after POST. Must include `Location` header pointing to new resource.
- `204 No Content` – Success after DELETE (or PUT/PATCH that returns no body).

### 3xx Redirection (rarely used in APIs)

- `301 Moved Permanently`
- `304 Not Modified` (for conditional GET)

### 4xx Client Errors

- `400 Bad Request` – Malformed syntax, validation errors (use with `fail` envelope).
- `401 Unauthorized` – Missing or invalid authentication.
- `403 Forbidden` – Authenticated but lacks permission.
- `404 Not Found` – Resource does not exist.
- `405 Method Not Allowed` – Wrong HTTP method for endpoint.
- `409 Conflict` – Conflict with current state (e.g., duplicate unique field).
- `429 Too Many Requests` – Rate limit exceeded.

### 5xx Server Errors

- `500 Internal Server Error` – Unhandled exception (use `error` envelope).
- `502 Bad Gateway` – Invalid response from upstream.
- `503 Service Unavailable` – Temporary overload/maintenance.
- `504 Gateway Timeout` – Upstream timeout.

## 4. API Versioning

A2LT standard: **URL Path Versioning** (`/api/v1/`, `/api/v2/`).

- Version in the URL is explicit and easy to route.
- Never remove a version; deprecate gradually with sunset headers.
- Example: `GET /api/v1/users/`

Alternative strategies (not used in A2LT unless required):

- **Accept header versioning:** `Accept: application/json; version=1.0`
- **Query parameter versioning:** `/api/users/?v=1`

## 5. Query Parameters for Filtering, Sorting, and Field Selection

- **Filtering:** Use query parameters with field names.
  `GET /api/v1/articles/?author=123&published=true`

- **Searching:** Use a generic `search` parameter.
  `GET /api/v1/articles/?search=django`

- **Sorting:** Use `ordering` (or `sort`) with field names, prefix `-` for descending.
  `GET /api/v1/articles/?ordering=-created_at,title`

- **Field selection:** `fields` parameter to limit returned fields.
  `GET /api/v1/users/123/?fields=id,username`

- **Pagination:** Use `page`, `page_size`, or `limit`/`offset`.
  `GET /api/v1/articles/?page=2&page_size=20`

## 6. HATEOAS (Hypermedia as the Engine of Application State)

While not strictly required, including links in responses can improve discoverability. A2LT encourages simple links for related resources.

Example:

```json
{
  "status": "success",
  "data": {
    "id": 123,
    "title": "My Article",
    "_links": {
      "self": "/api/v1/articles/123",
      "author": "/api/v1/users/456",
      "comments": "/api/v1/articles/123/comments"
    }
  }
}
```

## 7. Idempotency for POST (Preventing Duplicates)

For operations that should not create duplicates (e.g., payments), clients should send an idempotency key header (`Idempotency-Key`). The server caches the response for that key and returns the same result for subsequent identical requests.

**Implementation hint:** Use a Redis cache with the key and expiration.

## 8. Caching

- **ETag / If-None-Match:** Return `ETag` header with a hash of the resource. Clients can send `If-None-Match` for conditional GETs.
- **Last-Modified / If-Modified-Since:** Use for timestamp‑based caching.
- **Cache-Control:** Set appropriate max-age for public resources.

## 9. Rate Limiting

Return standard headers:

- `X-RateLimit-Limit` – total allowed requests in the current period.
- `X-RateLimit-Remaining` – remaining requests.
- `X-RateLimit-Reset` – time when the limit resets (Unix timestamp).

On limit exceeded, respond with `429 Too Many Requests` and a `fail` envelope.

## 10. Security Headers

- **CORS:** Configure `django-cors-headers` to allow only trusted origins.
- **HTTPS:** Redirect all HTTP traffic to HTTPS; use `Secure` and `HttpOnly` cookies.
- **Content Security Policy (CSP):** Not typically needed for APIs, but can be set for documentation endpoints.

## 11. Documentation

Expose an OpenAPI schema using `drf-spectacular` or `drf-yasd`. The schema should be available at a well‑known endpoint (e.g., `/api/schema/`) and in a human‑readable format (Swagger UI at `/api/docs/`).

## 12. Example: Full API Design for a Blog

| Resource       | Endpoint                               | Methods | Description            |
| -------------- | -------------------------------------- | ------- | ---------------------- |
| List articles  | `GET /api/v1/articles/`                | GET     | Paginated list         |
| Create article | `POST /api/v1/articles/`               | POST    | Create new article     |
| Article detail | `GET /api/v1/articles/{id}/`           | GET     | Retrieve one article   |
| Update article | `PUT /api/v1/articles/{id}/`           | PUT     | Full update            |
| Partial update | `PATCH /api/v1/articles/{id}/`         | PATCH   | Partial update         |
| Delete article | `DELETE /api/v1/articles/{id}/`        | DELETE  | Remove article         |
| List comments  | `GET /api/v1/articles/{id}/comments/`  | GET     | Nested comments        |
| Create comment | `POST /api/v1/articles/{id}/comments/` | POST    | Add comment to article |
| User profile   | `GET /api/v1/users/{id}/`              | GET     | User details           |

All endpoints must follow the response format from `response_format.md`.

---

_Combine these practices with the implementation patterns in `django_drf_patterns.md` and the envelope rules in `response_format.md`._
