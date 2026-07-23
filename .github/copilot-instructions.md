# Copilot Instructions for django-feature-flags

## Quick Start

This is a reusable Django package for feature flag management with admin,
programmatic, and REST API access. Use `uv` for dependency management and `tox`
as the canonical local validation entry point. This repository currently
targets Python 3.13 only.

```bash
uv sync --extra dev
```

`uv.lock` is committed. Update it when dependency metadata changes, and keep CI
compatible with `uv sync --frozen --extra dev`.

## Build, Test, and Lint Commands

### Setup and Packaging
```bash
# Install the development toolchain
uv sync --extra dev

# Build wheel and sdist artifacts
uv run python -m build
```

### Tox Entry Points
```bash
# Run the default locally available tox environments
uv run tox

# Run one environment explicitly
uv run tox -e py313
uv run tox -e lint
uv run tox -e mypy
uv run tox -e security

# Run a single test file or test function through tox
uv run tox -e py313 -- tests/test_models.py
uv run tox -e py313 -- tests/test_api.py::test_public_flags_endpoint_filters_for_public_flags
```

### Running Tests
```bash
# Run all tests with coverage
uv run pytest

# Run specific test module
uv run pytest tests/test_models.py

# Run specific test function
uv run pytest tests/test_models.py::test_function_name -v

# Run with coverage report
uv run pytest --cov=feature_flags --cov-report=term-missing
```

### Linting, Type Checking, and Security
```bash
# Run the full local validation matrix
uv run tox

# Lint only (ruff check and format validation)
uv run ruff check .
uv run ruff format --check feature_flags tests

# Type check only
uv run mypy feature_flags

# Security checks only
uv run bandit -q -r feature_flags -x feature_flags/migrations
uv run pip-audit
```

**Note:** Tests require `DJANGO_SETTINGS_MODULE=tests.settings` (configured in
`pyproject.toml`). Django ORM operations use SQLite and in-memory cache
settings tailored for tests.

`tox` is the canonical entry point for local and CI checks. The configured
environments are `py313`, `lint`, `mypy`, and `security`, with optional `ruff`,
`bandit`, and `pip-audit` aliases for focused runs.

## High-Level Architecture

### Core Concept

`django-feature-flags` provides a reusable Django app for managing feature
flags at three scopes:
1. **Public**: Anonymous (no authentication required)
2. **User-based**: Authenticated users with optional allowlisting
3. **Context-based**: Generic scoping to any Django model (workspace, team,
   group, account, and similar models)

### Key Models

- **FeatureFlag**: Core model with `is_enabled`, `is_public`,
  `allowed_users`, and `name` (slug) fields
- **FeatureFlagTarget**: Generic FK to any model via ContentType, enabling
  organization-level scoping

### Evaluation Logic (`FeatureFlag.is_enabled_for_user()`)

1. If the flag is not enabled globally, return `False`
2. If the flag has context restrictions and the provided context does not
   match, return `False`
3. If the flag is public, return `True`
4. If no authenticated user is available, return `False`
5. If the flag has user restrictions, check the allowlist
6. If the flag has no user restrictions, allow all authenticated users

### Request Paths

#### Admin Interface

- Django admin supports CRUD for flags, user allowlists, and targets
- Standard Django admin permissions govern access

#### REST API

- **`GET /api/feature-flags/public/`** (`AllowAny`): public flags only, with
  optional `context_*` query params
- **`GET /api/feature-flags/all-enabled/`** (`IsAuthenticated`): all enabled
  flags for the current user/context
- **`GET /api/feature-flags/{name}/is-enabled/`** (`IsAuthenticated`): check a
  single flag state for the current user/context
- **`GET /api/feature-flags/{name}/`** (`IsAuthenticated`): retrieve a single
  flag record

Context parameters:

- `context_app_label`
- `context_model`
- `context_id`
- All three must be provided together or omitted entirely

#### Programmatic API

```python
from feature_flags.utils import get_feature_flag_states, is_feature_enabled

is_feature_enabled("feature-name", user=request.user, context=workspace)
flags_dict = get_feature_flag_states(user=request.user, context=workspace)
```

### Caching Strategy

- All flag evaluations use a version-based invalidation system
- Cache key structure: `{prefix}:{version}:{feature_name}:{user_fragment}:{context_fragment}`
- Signals imported from `apps.py.ready()` invalidate the cache on model changes
- Cache behavior is configured via `FEATURE_FLAGS_CACHE_TTL`

### Management Command

```bash
python manage.py feature_flags list
python manage.py feature_flags create <name> [--public] [--description TEXT]
python manage.py feature_flags toggle <name>
python manage.py feature_flags set <name> [--enabled|--disabled] [--public|--private]
```

## Key Conventions

### Code Style

- Type hints are mandatory on public APIs and model methods
- Use `from __future__ import annotations` for forward references
- Ruff enforces a 100-character line length plus `B`, `DJ`, `E`, `F`, `I`, and
  `UP` lint rules

### Django Patterns

- Use `prefetch_related("allowed_users", "targets")` when loading flags to
  avoid N+1 query patterns
- Keep internal logic in private helpers and use public methods as the stable
  interface
- Use `request.query_params` for REST API query inputs

### Migrations

- All migrations live under `feature_flags/migrations/`
- Run migrations in the test environment to ensure they apply cleanly
- Prefer schema migrations plus app-level handling over heavy data migrations

### Versioning and Release Flow

- `pyproject.toml` drives release version selection, and
  `feature_flags/__init__.py` and `uv.lock` must stay aligned with that package
  version
- Normal feature work should not bump the version manually
- Releases go through `.github/workflows/release.yml`, which creates a
  `release-bump/vX.Y.Z` branch and PR, updates `pyproject.toml`,
  `feature_flags/__init__.py`, and `uv.lock`; it attempts to enable PR
  auto-merge when the repository supports it and otherwise leaves the release
  PR open for manual merge after checks pass before creating the tag and GitHub
  Release after merge
- The release PR creation path uses `actions/create-github-app-token@v3`; if
  manual releases fail with PR creation permission errors, check
  `RELEASE_APP_ID` and `RELEASE_APP_PRIVATE_KEY` first
- The release flow is GitHub-only for now; do not add PyPI publishing steps

## Git Workflow

### Using Worktrees

- **Create worktrees for new work**: use
  `git worktree add /path/to/worktree -b feature-branch-name main` to create an
  isolated workspace for non-trivial changes
- **Don't work directly on main**: always create a feature branch within the
  worktree; never commit directly to `main`
- **Commit regularly**: make commits to the worktree branch as work progresses
  or when tasks are complete, rather than leaving changes uncommitted
- **Example workflow**:
  ```bash
  git worktree add ../django-feature-flags-new-feature -b add-caching-improvements main
  cd ../django-feature-flags-new-feature
  git add .
  git commit -m "Improve caching invalidation logic"
  git push -u origin add-caching-improvements
  ```
