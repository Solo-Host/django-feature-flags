# Scoping examples

## Public rollout

```python
from feature_flags.models import FeatureFlag

FeatureFlag.objects.create(
    name="new-pricing-model",
    description="Show the new pricing page to everyone.",
    is_enabled=True,
    is_public=True,
)
```

## Authenticated rollout

```python
FeatureFlag.objects.create(
    name="bulk-trip-import",
    description="Enable bulk import for authenticated users only.",
    is_enabled=True,
)
```

With `is_public=False` and no user allowlist, every authenticated user can access the feature.

## User allowlist rollout

```python
flag = FeatureFlag.objects.create(
    name="early-access-reporting",
    is_enabled=True,
)
flag.allowed_users.add(user)
```

## Team, workspace, group, or account rollout

```python
flag = FeatureFlag.objects.create(
    name="workspace-insights",
    is_enabled=True,
)
flag.add_target(workspace)
```

The target can be any Django model instance. The package stores it generically through `ContentType`.

## Hybrid rollout

```python
flag = FeatureFlag.objects.create(
    name="pilot-dashboard",
    is_enabled=True,
)
flag.allowed_users.add(user)
flag.add_target(team)
```

When both a user allowlist and context targets exist, both must match.

## Server-side usage

```python
from feature_flags.utils import is_feature_enabled

if is_feature_enabled("workspace-insights", user=request.user, context=workspace):
    ...
```
