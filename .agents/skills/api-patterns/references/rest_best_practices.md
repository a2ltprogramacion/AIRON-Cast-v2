# REST Best Practices — AIRON‑Cast

This reference defines URI design, HTTP method usage, status codes, and other
RESTful conventions for all AIRON‑Cast APIs.

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

- **Nest resources to show relationships, max 3 levels.**
  ✅ `/api/v1/users/123/posts/`
  ✅ `/api/v1/users/123/posts/456/comments/`
  ❌ `/api/v1/users/123/posts/456/comments/789/likes/`

## 2. HTTP Methods

| Method   | CRUD Action           | Safe | Idempotent | Request Body | Response Body     |
|----------|-----------------------|------|------------|--------------|-------------------|
| `GET`    | Read                  | Yes  | Yes        | No           | Resource          |
| `POST`   | Create                | No   | No         | Resource     | Created resource  |
| `PUT`    | Replace (full update) | No   | Yes        | Full resource| Updated resource  |
| `PATCH`  | Partial update        | No   | No         | Partial      | Updated resource  |
| `DELETE` | Delete                | No   | Yes        | No           | Usually empty     |

- `PUT` and `DELETE` are idempotent.
- `POST` is not idempotent — use idempotency keys for payments.
- `GET`, `HEAD`, `OPTIONS` are safe and idempotent.

## 3. HTTP Status Codes

### 2xx Success
- `200 OK` — Standard success for GET, PUT, PATCH.
- `201 Created` — Success after POST. Include `Location` header.
- `204 No Content` — Success after DELETE.

### 4xx Client Errors
- `400 Bad Request` — Validation errors (use `fail` envelope).
- `401 Unauthorized` — Missing or invalid authentication.
- `403 Forbidden` — Authenticated but lacks permission.
- `404 Not Found` — Resource does not exist.
- `409 Conflict` — Conflict with current state.
- `429 Too Many Requests` — Rate limit exceeded.

### 5xx Server Errors
- `500 Internal Server Error` — Unhandled exception (use `error` envelope).
- `502 Bad Gateway` — Invalid response from upstream.
- `503 Service Unavailable` — Temporary overload.

## 4. API Versioning

AIRON‑Cast standard: **URL Path Versioning** (`/api/v1/`, `/api/v2/`).
Never remove a version; deprecate gradually.

## 5. Query Parameters

- **Filtering:** `GET /api/v1/articles/?author=123&published=true`
- **Searching:** `GET /api/v1/articles/?search=django`
- **Sorting:** `GET /api/v1/articles/?ordering=-created_at,title`
- **Field selection:** `GET /api/v1/users/123/?fields=id,username`
- **Pagination:** `GET /api/v1/articles/?page=2&page_size=20`

## 6. HATEOAS (Optional)

Include links for related resources to improve discoverability.

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

## 7. Rate Limiting Headers

- `X-RateLimit-Limit` — Total allowed requests.
- `X-RateLimit-Remaining` — Remaining requests.
- `X-RateLimit-Reset` — Unix timestamp when limit resets.

On limit exceeded: `429 Too Many Requests` with `fail` envelope.

## 8. Security

- **CORS:** Configure `django-cors-headers` with trusted origins only.
- **HTTPS:** Redirect all HTTP to HTTPS; `Secure` and `HttpOnly` cookies.
- **Sensitive data:** Never expose passwords or tokens in responses or logs.

## 9. Example: Blog API Design

| Resource         | Endpoint                               | Methods | Description         |
|------------------|----------------------------------------|---------|---------------------|
| List articles    | `GET /api/v1/articles/`                | GET     | Paginated list      |
| Create article   | `POST /api/v1/articles/`               | POST    | Create new          |
| Article detail   | `GET /api/v1/articles/{id}/`           | GET     | Retrieve one        |
| Update article   | `PUT /api/v1/articles/{id}/`           | PUT     | Full update         |
| Partial update   | `PATCH /api/v1/articles/{id}/`         | PATCH   | Partial update      |
| Delete article   | `DELETE /api/v1/articles/{id}/`        | DELETE  | Remove              |
| List comments    | `GET /api/v1/articles/{id}/comments/`  | GET     | Nested comments     |
| Create comment   | `POST /api/v1/articles/{id}/comments/` | POST    | Add comment         |