from __future__ import annotations

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.cache import cache
from django.db import models

from feature_flags.conf import get_cache_prefix


def get_cache_version_key() -> str:
    return f"{get_cache_prefix()}:version"


def get_cache_version() -> int:
    version_key = get_cache_version_key()
    version = cache.get(version_key)
    if version is None:
        cache.add(version_key, 1, timeout=None)
        version = cache.get(version_key)
    return int(version or 1)


def bump_cache_version() -> int:
    version_key = get_cache_version_key()
    if cache.add(version_key, 2, timeout=None):
        return 2

    try:
        return int(cache.incr(version_key))
    except (NotImplementedError, ValueError):
        next_version = get_cache_version() + 1
        cache.set(version_key, next_version, timeout=None)
        return next_version


def get_context_cache_fragment(context: models.Model | None) -> str:
    if context is None:
        return "context:none"

    return f"context:{context._meta.app_label}.{context._meta.model_name}:{context.pk}"


def get_user_cache_fragment(user: AbstractBaseUser | None) -> str:
    if user is None:
        return "user:anonymous"

    return f"user:{user.pk}"


def build_flag_cache_key(
    feature_name: str,
    *,
    user: AbstractBaseUser | None,
    context: models.Model | None,
) -> str:
    version = get_cache_version()
    return ":".join(
        [
            get_cache_prefix(),
            str(version),
            feature_name,
            get_user_cache_fragment(user),
            get_context_cache_fragment(context),
        ]
    )
