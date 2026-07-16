# Copilot Instructions for django-feature-flags

## Build, Test, and Lint Commands

### Running Tests
```bash
# Run all tests with coverage
pytest

# Run specific test module
pytest tests/test_models.py

# Run specific test function
pytest tests/test_models.py::test_function_name -v

# Run with coverage report
pytest --cov=feature_flags --cov-report=term-missing
```

### Linting and Type Checking
```bash
# Run all checks (linting and type checking)
tox -e py311,lint,mypy

# Lint only (ruff check and format validation)
ruff check .
ruff format --check feature_flags tests

# Fix formatting automatically
ruff format feature_flags tests

# Type check only
mypy feature_flags
```

### Full Local Validation
```bash
# Replicate all CI checks
pytest
ruff check .
ruff format --check feature_flags tests
mypy feature_flags
```

**Note:** Tests require `DJANGO_SETTINGS_MODULE=tests.settings` (configured in `pyproject.toml`). Django ORM operations use SQLite in-memory cache for testing.

## High-Level Architecture

### Core Concept
`django-feature-flags` provides a reusable Django app for managing feature flags at three scopes:
1. **Public**: Anonymous (no authentication required)
2. **User-based**: Authenticated users with optional allowlisting
3. **Context-based**: Generic scoping to any Django model (workspace, team, group, account, etc.)

### Key Models
- **FeatureFlag**: Core model with `is_enabled`, `is_public`, `allowed_users`, and `name` (slug) fields
- **FeatureFlagTarget**: Generic FK to any model via ContentType, enabling organization-level scoping

### Evaluation Logic (`FeatureFlag.is_enabled_for_user()`)
1. If flag is not enabled globally → return False
2. If flag has context restrictions and context provided doesn't match → return False
3. If flag is public → return True
4. If no authenticated user → return False
5. If flag has user restrictions → check if user is in allowlist
6. If no user restrictions → return True (all authenticated users allowed)

### Request Paths

#### Admin Interface
- Django admin for CRUD of flags, user allowlists, and targets
- Integrated with Django's standard admin permissions

#### REST API
- **`GET /api/feature-flags/public/`** (AllowAny): Public flags only, supports `context_*` query params
- **`GET /api/feature-flags/all-enabled/`** (IsAuthenticated): All enabled flags for current user/context
- **`GET /api/feature-flags/{name}/is-enabled/`** (IsAuthenticated): Check single flag for current user/context
- **`GET /api/feature-flags/{name}/`** (IsAuthenticated): Retrieve single flag details

Context parameters (query string):
- `context_app_label`: App label of the context model (e.g., `myapp`)
- `context_model`: Model name of the context (e.g., `workspace`)
- `context_id`: PK of the context instance
- All three must be provided together or omitted entirely

#### Programmatic API
```python
from feature_flags.utils import is_feature_enabled, get_feature_flag_states

# Check single flag
is_feature_enabled('feature-name', user=request.user, context=workspace)

# Batch check all flags
flags_dict = get_feature_flag_states(user=request.user, context=workspace)
```

### Caching Strategy
- All flag evaluations are cached with a version-based invalidation system
- Cache key structure: `{prefix}:{version}:{feature_name}:{user_fragment}:{context_fragment}`
- Cache invalidation triggered by signals on model save/delete (bumps cache version)
- Configuration via `FEATURE_FLAGS_CACHE_TTL` (default 300 seconds)

### Management Command
```bash
python manage.py feature_flags list
python manage.py feature_flags create <name> [--public] [--description TEXT]
python manage.py feature_flags toggle <name>
python manage.py feature_flags set <name> [--enabled|--disabled] [--public|--private]
```

## Key Conventions

### Code Style
- **Type hints**: Mandatory on all public APIs and model methods (enforced by mypy with `disallow_untyped_defs`)
- **Imports**: Organized by `isort` rules; use `from __future__ import annotations` at top of modules for forward references
- **Line length**: 100 characters (configured in ruff)
- **Linting rules**: `B` (flake8-bugbear), `DJ` (django), `E` (pycodestyle errors), `F` (pyflakes), `I` (isort), `UP` (pyupgrade)

### Django Patterns
- **Foreign keys**: Use `on_delete=models.CASCADE` with explicit `related_name` for reverse access
- **Generic relations**: Leverage Django's `ContentType` and `GenericForeignKey` for model-agnostic relationships
- **Prefetching**: Always use `prefetch_related("allowed_users", "targets")` when loading flags to avoid N+1 queries
- **Model methods**: Use private helper methods (leading `_`) for internal logic; public methods handle the public interface
- **Signals**: Connected in `signals.py` and imported in `apps.py.ready()` to invalidate cache on model changes

### Testing Patterns
- **Settings module**: Use `tests.settings` which configures SQLite, in-memory cache, and test-specific Auth settings
- **Fixtures**: Use `conftest.py` for reusable test data and Django fixtures
- **Assertions**: Pytest asserts (not unittest); use descriptive assertion messages
- **Coverage**: Minimum 90% branch coverage required (enforced by pytest config)

### Django ORM Specifics
- Use `_default_manager` to access objects when working with dynamic models (allows manager overrides)
- Cast dynamic models to type hints: `cast(type[models.Model], apps.get_model(app, model))`
- Store object IDs as strings in generic relations (ContentType's `object_id` is `CharField`)

### API Design
- **Viewsets**: Use `ReadOnlyModelViewSet` for read-only REST APIs; custom actions with `@action`
- **Permissions**: Mix `AllowAny` and `IsAuthenticated` based on flag properties (public vs. user-restricted)
- **Serializers**: Include `is_enabled_for_user` evaluation in the serializer context if flag state depends on request user
- **Query params**: Use `request.query_params` (DRF standard) not `request.GET`

### Migrations
- All migrations are in `feature_flags/migrations/`
- Run migrations in test environment to ensure they apply cleanly
- Use data migrations sparingly; prefer schema migrations + app-level data handling

## Git Workflow

### Using Worktrees
- **Create worktrees for new work**: Use `git worktree add /path/to/worktree -b feature-branch-name origin/main` to create an isolated workspace for features, bug fixes, or non-trivial changes
- **Don't work directly on main**: Always create a feature branch within the worktree; never commit directly to `main`
- **Commit regularly**: Make commits to the worktree branch as work progresses or when tasks are complete, rather than leaving changes uncommitted until PR preparation
- **Example workflow**:
  ```bash
  # Create a worktree with a new feature branch
  git worktree add ../django-feature-flags-new-feature -b add-caching-improvements origin/main
  cd ../django-feature-flags-new-feature
  # Make changes and commit
  git add .
  git commit -m "Improve caching invalidation logic"
  # Push the feature branch and create a PR
  git push -u origin add-caching-improvements
  ```
