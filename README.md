# django-feature-flags

[![PyPI version](https://img.shields.io/pypi/v/django-feature-flags.svg)](https://pypi.org/project/django-feature-flags/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-feature-flags.svg)](https://pypi.org/project/django-feature-flags/)
[![Django 5.0+](https://img.shields.io/badge/Django-5.0%2B-0C4B33.svg)](https://www.djangoproject.com/)

Reusable Django feature flags with:

- Django admin management
- Built-in caching with automatic invalidation
- Mixed-auth REST API endpoints
- Generic organizational scoping for workspaces, teams, groups, accounts, and similar models

## Why this package exists

`django-feature-flags` gives you a single package you can reuse across internal projects and public apps without hard-coding release toggles into business logic. It supports:

- **Public flags** for anonymous pages such as marketing or pricing pages
- **Authenticated flags** for logged-in experiences
- **User allowlists** for beta rollouts
- **Generic context scoping** for any Django model, such as a workspace, team, group, or account

## Installation

```bash
pip install django-feature-flags
```

Add the app and Django REST Framework to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "feature_flags",
]
```

Run migrations:

```bash
python manage.py migrate
```

## Quick start

Create a flag:

```python
from feature_flags.models import FeatureFlag

flag = FeatureFlag.objects.create(
    name="new-pricing-model",
    description="Roll out the pricing page refresh.",
    is_enabled=True,
    is_public=True,
)
```

Evaluate a flag in Python:

```python
from feature_flags.utils import is_feature_enabled

enabled = is_feature_enabled("new-pricing-model", user=request.user)
```

Scope a flag to an organizational object:

```python
workspace_flag = FeatureFlag.objects.create(
    name="workspace-insights",
    description="Expose the new insights dashboard to a limited set of workspaces.",
    is_enabled=True,
)
workspace_flag.add_target(workspace)
```

## REST API

Mount the built-in router wherever your project expects it:

```python
from django.urls import include, path

urlpatterns = [
    path("api/feature-flags/", include("feature_flags.urls")),
]
```

Endpoints:

| Endpoint | Authentication | Purpose |
| --- | --- | --- |
| `GET /api/feature-flags/public/` | none | Returns public, enabled flags |
| `GET /api/feature-flags/all-enabled/` | required | Returns enabled flags for the current user |
| `GET /api/feature-flags/<name>/is-enabled/` | required | Returns a single feature state |

Optional context query parameters let frontends evaluate flags within a specific team, workspace, group, or account:

- `context_app_label`
- `context_model`
- `context_id`

Example:

```text
/api/feature-flags/all-enabled/?context_app_label=auth&context_model=group&context_id=1
```

## Django admin

Feature flags are manageable from Django admin with:

- enable/disable toggles
- public/private configuration
- user allowlists
- inline context targets

That keeps rollout control available to non-technical teammates without a deploy.

## Settings

| Setting | Default | Description |
| --- | --- | --- |
| `FEATURE_FLAGS_CACHE_TTL` | `300` | Cache duration in seconds for feature evaluations |
| `FEATURE_FLAGS_CACHE_PREFIX` | `"feature_flags"` | Prefix used for cache keys and cache versioning |

## Management command

```bash
python manage.py feature_flags list
python manage.py feature_flags create new-pricing-model --public
python manage.py feature_flags toggle new-pricing-model
python manage.py feature_flags set new-pricing-model --enabled --private
```

## Documentation

- [`docs/api.md`](docs/api.md)
- [`docs/rest-api.md`](docs/rest-api.md)
- [`docs/examples.md`](docs/examples.md)
- [`docs/frontend-typescript.md`](docs/frontend-typescript.md)
- [`docs/frontend-vue.md`](docs/frontend-vue.md)

## Development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
pytest
ruff check .
ruff format --check feature_flags tests
mypy feature_flags
```

## License

MIT. See [`LICENSE`](LICENSE).
