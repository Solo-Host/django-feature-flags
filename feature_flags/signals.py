from __future__ import annotations

from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from feature_flags.cache import bump_cache_version
from feature_flags.models import FeatureFlag, FeatureFlagTarget


@receiver(post_save, sender=FeatureFlag)
@receiver(post_delete, sender=FeatureFlag)
@receiver(post_save, sender=FeatureFlagTarget)
@receiver(post_delete, sender=FeatureFlagTarget)
def invalidate_flag_cache(**_: object) -> None:
    bump_cache_version()


@receiver(m2m_changed, sender=FeatureFlag.allowed_users.through)
def invalidate_flag_cache_on_m2m_change(action: str, **_: object) -> None:
    if action.startswith("post_"):
        bump_cache_version()
