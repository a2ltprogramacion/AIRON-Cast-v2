# Response Format Structure — AIRON‑Cast

AIRON‑Cast APIs follow a strict, unified envelope structure inspired by
[JSend](https://github.com/omniti-labs/jsend). This guarantees that frontend
applications (Astro, Vanilla JS) can parse responses predictably.

## The Universal Envelope

Every response MUST conform to this root structure:

```json
{
    "status": "success | fail | error",
    "message": "Human‑readable string (optional for success, mandatory for fail/error)",
    "data": { ... } | null
}
```

- **`status`** — Indicates the outcome category.
- **`message`** — Human‑readable summary, especially for errors.
- **`data`** — Response payload. For `fail`, holds validation errors. For `error`,
  may contain debug information (never stack traces).

## 1. Success Responses (`status: "success"`)

Used when the API call completes successfully (2xx status codes).

**GET /api/v1/users/123**

```json
HTTP/1.1 200 OK

{
    "status": "success",
    "data": {
        "id": 123,
        "username": "argenito",
        "email": "angel@a2lt.com"
    }
}
```

**POST /api/v1/articles/** (resource created)

```json
HTTP/1.1 201 Created

{
    "status": "success",
    "data": {
        "id": 42,
        "title": "New Article",
        "content": "..."
    }
}
```

**DELETE /api/v1/articles/42** (no content)

```json
HTTP/1.1 204 No Content
// No response body
```

**Paginated List Response**

```json
HTTP/1.1 200 OK

{
    "status": "success",
    "data": {
        "count": 145,
        "next": "https://api.example.com/v1/articles/?page=3",
        "previous": "https://api.example.com/v1/articles/?page=1",
        "results": [
            { "id": 1, "title": "First Article" },
            { "id": 2, "title": "Second Article" }
        ]
    }
}
```

## 2. Fail Responses (`status: "fail"`)

Used for 4xx errors where the client's request is invalid. The `data` object
contains field‑level error messages from DRF serializers.

**Validation failure (400)**

```json
HTTP/1.1 400 Bad Request

{
    "status": "fail",
    "message": "Validation failed",
    "data": {
        "title": ["This field is required."],
        "content": ["This field may not be blank."]
    }
}
```

**Authentication failure (401)**

```json
HTTP/1.1 401 Unauthorized

{
    "status": "fail",
    "message": "Authentication credentials were not provided.",
    "data": null
}
```

**Permission denied (403)**

```json
HTTP/1.1 403 Forbidden

{
    "status": "fail",
    "message": "You do not have permission to perform this action.",
    "data": null
}
```

**Not found (404)**

```json
HTTP/1.1 404 Not Found

{
    "status": "fail",
    "message": "No Article matches the given query.",
    "data": null
}
```

## 3. Error Responses (`status: "error"`)

Used for 5xx server errors. The `message` must be user‑safe (no stack traces).
An optional `code` field provides a machine‑readable error type.

**Internal server error (500)**

```json
HTTP/1.1 500 Internal Server Error

{
    "status": "error",
    "message": "Internal server error. Our team has been notified.",
    "code": "INTERNAL_ERROR"
}
```

**External service failure (502)**

```json
HTTP/1.1 502 Bad Gateway

{
    "status": "error",
    "message": "Unable to connect to the external payment gateway.",
    "code": "GATEWAY_TIMEOUT"
}
```

## 4. Edge Cases and Rules

- **Empty success:** Use `204 No Content` (no body).
- **Empty list:** Return `data: []` with `200 OK`.
- **Error codes:** Use consistent codes: `VALIDATION_ERROR`, `AUTH_FAILED`,
  `NOT_FOUND`, `RATE_LIMITED`, `INTERNAL_ERROR`, `GATEWAY_TIMEOUT`.
- **Content type:** Always `application/json`.

## 5. Envelope Implementation in DRF

Enforce the envelope globally via a custom renderer for success responses
and a custom exception handler for errors.

**Custom renderer:**

```python
from rest_framework.renderers import JSONRenderer

class AIRONJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context['response']
        if response.exception or response.status_code >= 400:
            return super().render(data, accepted_media_type, renderer_context)
        wrapped_data = {
            'status': 'success',
            'data': data
        }
        return super().render(wrapped_data, accepted_media_type, renderer_context)
```

**Settings:**

```python
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['path.to.AIRONJSONRenderer']
}
```

Exception handler: see `references/django_drf_patterns.md` §8.