# REST API

Include the router in your project:

```python
from django.urls import include, path

urlpatterns = [
    path("api/feature-flags/", include("feature_flags.urls")),
]
```

## Authentication model

| Endpoint | Auth | Notes |
| --- | --- | --- |
| `GET /api/feature-flags/public/` | `AllowAny` | Public flags only |
| `GET /api/feature-flags/all-enabled/` | `IsAuthenticated` | Enabled flags for the current user |
| `GET /api/feature-flags/<name>/is-enabled/` | `IsAuthenticated` | Single-flag evaluation |
| `GET /api/feature-flags/` | `IsAuthenticated` | Read-only metadata list |
| `GET /api/feature-flags/<name>/` | `IsAuthenticated` | Read-only metadata detail |

## Context query parameters

All three custom endpoints support optional context scoping:

- `context_app_label`
- `context_model`
- `context_id`

These must be supplied together.

### Example

```text
/api/feature-flags/all-enabled/?context_app_label=auth&context_model=group&context_id=1
```

## Response shapes

### `GET /public/`

```json
{
  "new-pricing-model": true
}
```

### `GET /all-enabled/`

```json
{
  "bulk-trip-import": true,
  "workspace-insights": true
}
```

### `GET /<name>/is-enabled/`

```json
{
  "enabled": true
}
```

## Error handling

- Invalid context model parameters return `400 Bad Request`
- Unknown scoped context instances return `404 Not Found`
