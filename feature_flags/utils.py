from __future__ import annotations

from collections.abc import Iterable

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db import models

from feature_flags.cache import build_flag_cache_key
from feature_flags.conf import get_cache_ttl
from feature_flags.models import FeatureFlag

UserLike = AbstractBaseUser | AnonymousUser | None


def normalize_user(user: UserLike) -> AbstractBaseUser | None:
    if user is None or not user.is_authenticated:
        return None
    return user


def is_feature_enabled(
    feature_name: str,
    user: UserLike = None,
    context: models.Model | None = None,
) -> bool:
    normalized_user = normalize_user(user)
    cache_key = build_flag_cache_key(feature_name, user=normalized_user, context=context)
    cached = cache.get(cache_key)
    if cached is not None:
        return bool(cached)

    try:
        flag = FeatureFlag.objects.prefetch_related("allowed_users", "targets").get(
            name=feature_name
        )
    except FeatureFlag.DoesNotExist:
        enabled = False
    else:
        enabled = flag.is_enabled_for_user(user=normalized_user, context=context)

    cache.set(cache_key, enabled, timeout=get_cache_ttl())
    return enabled


def get_feature_flag_states(
    *,
    queryset: Iterable[FeatureFlag] | None = None,
    user: UserLike = None,
    context: models.Model | None = None,
) -> dict[str, bool]:
    flags = (
        queryset
        if queryset is not None
        else FeatureFlag.objects.prefetch_related("allowed_users", "targets")
    )
    normalized_user = normalize_user(user)
    return {
        flag.name: flag.is_enabled_for_user(user=normalized_user, context=context) for flag in flags
    }
