# API reference

## Models

### `FeatureFlag`

| Field | Type | Description |
| --- | --- | --- |
| `name` | `SlugField` | Unique machine-readable flag name |
| `description` | `TextField` | Optional operator-facing description |
| `is_enabled` | `BooleanField` | Master on/off switch |
| `is_public` | `BooleanField` | Allows evaluation for anonymous requests |
| `allowed_users` | `ManyToManyField` | Optional allowlist for authenticated rollouts |
| `created_at` | `DateTimeField` | Creation timestamp |
| `updated_at` | `DateTimeField` | Last modification timestamp |

#### Methods

- `is_enabled_for_user(user=None, context=None) -> bool`
- `is_enabled_for_context(context, user=None) -> bool`
- `add_target(context) -> tuple[FeatureFlagTarget, bool]`
- `has_user_restrictions() -> bool`
- `has_context_restrictions() -> bool`

### `FeatureFlagTarget`

Represents a scoped organizational target attached to a feature flag through Django's content types framework.

| Field | Type | Description |
| --- | --- | --- |
| `feature_flag` | `ForeignKey` | Parent feature flag |
| `content_type` | `ForeignKey` | Model type for the scoped object |
| `object_id` | `CharField` | Primary key of the scoped object |
| `target` | `GenericForeignKey` | Resolved model instance |

## Utilities

### `is_feature_enabled(feature_name, user=None, context=None)`

Evaluates a single feature flag and caches the result using the configured cache backend.

### `get_feature_flag_states(queryset=None, user=None, context=None)`

Returns a dictionary of `{flag_name: bool}` for a queryset or iterable of feature flags.

## Cache settings

| Setting | Default | Notes |
| --- | --- | --- |
| `FEATURE_FLAGS_CACHE_TTL` | `300` | Per-flag evaluation cache TTL |
| `FEATURE_FLAGS_CACHE_PREFIX` | `"feature_flags"` | Prefix used for the versioned cache namespace |

Cache invalidation is automatic on:

- `FeatureFlag` save/delete
- `FeatureFlagTarget` save/delete
- changes to `allowed_users`

## Management command

```bash
python manage.py feature_flags list
python manage.py feature_flags create my-flag --public
python manage.py feature_flags toggle my-flag
python manage.py feature_flags set my-flag --enabled --private
```
