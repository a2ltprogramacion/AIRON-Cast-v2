# Response Format Structure

A2LT APIs follow a strict, unified envelope structure inspired by [JSend](https://github.com/omniti-labs/jsend). This guarantees that frontend applications (Astro, Vanilla JS) can parse responses predictably without guessing the schema per endpoint.

## The Universal Envelope

Every response from the API MUST conform to this root structure:

```json
{
    "status": "success | fail | error",
    "message": "Human‑readable string (optional for success, mandatory for fail/error)",
    "data": { ... } | null
}
```

- **`status`** – Indicates the outcome category.
- **`message`** – Provides a human‑readable summary, especially for errors.
- **`data`** – Contains the response payload. For `fail`, it holds validation errors. For `error`, it may contain additional debug information (but never stack traces).

## 1. Success Responses (`status: "success"`)

Used when the API call completes successfully (2xx status codes). The `data` key contains the requested resource or operation result.

### Examples

**GET /api/v1/users/123**

```json
HTTP/1.1 200 OK
Content-Type: application/json

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

For `204`, the envelope is omitted because there is no body.

### Paginated List Response

**GET /api/v1/articles/?page=2**

```json
HTTP/1.1 200 OK

{
    "status": "success",
    "data": {
        "count": 145,
        "next": "https://api.a2lt.com/v1/articles/?page=3",
        "previous": "https://api.a2lt.com/v1/articles/?page=1",
        "results": [
            { "id": 1, "title": "First Article" },
            { "id": 2, "title": "Second Article" }
        ]
    }
}
```

## 2. Fail Responses (`status: "fail"`)

Used for 4xx errors where the client’s request is invalid – typically validation failures (400 Bad Request). The `data` object contains field‑level error messages, exactly as produced by DRF serializers.

### Examples

**POST /api/v1/articles/** with missing fields

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

**Authentication failure** (401 Unauthorized)

```json
HTTP/1.1 401 Unauthorized

{
    "status": "fail",
    "message": "Authentication credentials were not provided.",
    "data": null
}
```

**Permission denied** (403 Forbidden)

```json
HTTP/1.1 403 Forbidden

{
    "status": "fail",
    "message": "You do not have permission to perform this action.",
    "data": null
}
```

**Resource not found** (404 Not Found)

```json
HTTP/1.1 404 Not Found

{
    "status": "fail",
    "message": "No Article matches the given query.",
    "data": null
}
```

## 3. Error Responses (`status: "error"`)

Used for 5xx server errors or unexpected conditions that the client cannot fix. The `message` should be a generic, user‑safe description. An optional `code` field can provide a machine‑readable error type for debugging.

### Examples

**Unhandled exception** (500 Internal Server Error)

```json
HTTP/1.1 500 Internal Server Error

{
    "status": "error",
    "message": "Internal server error. Our team has been notified.",
    "code": "INTERNAL_ERROR"
}
```

**External service failure**

```json
HTTP/1.1 502 Bad Gateway

{
    "status": "error",
    "message": "Unable to connect to the external payment gateway.",
    "code": "GATEWAY_TIMEOUT"
}
```

## 4. Edge Cases and Additional Rules

- **Empty data:** For a `success` response with no content (e.g., after a DELETE), use `204 No Content` and omit the body. For a `success` response that would naturally have an empty result (e.g., GET a list with no items), return `data: []` or `data: {}` as appropriate.
- **Message field:** In `fail` responses, the `message` should briefly summarize the error. In `error` responses, it must be user‑friendly (no stack traces).
- **Error codes:** Define a set of standard codes (e.g., `VALIDATION_ERROR`, `AUTH_FAILED`, `NOT_FOUND`, `RATE_LIMITED`) and use them consistently.
- **Content type:** Always `application/json`.

## 5. Envelope Implementation in DRF

The envelope can be enforced globally via:

- A custom exception handler (as shown in `django_drf_patterns.md`) for errors.
- A custom renderer or a response mixin for success responses.

Example of a simple renderer:

```python
from rest_framework.renderers import JSONRenderer

class A2LTJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context['response']
        if response.exception or response.status_code >= 400:
            # Already formatted by exception handler
            return super().render(data, accepted_media_type, renderer_context)
        # Wrap successful responses
        wrapped_data = {
            'status': 'success',
            'data': data
        }
        return super().render(wrapped_data, accepted_media_type, renderer_context)
```

Then set in settings:

```python
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['path.to.A2LTJSONRenderer']
}
```

---

_This format must be applied to every endpoint. Refer to `rest_best_practices.md` for endpoint design and `django_drf_patterns.md` for implementation details._
