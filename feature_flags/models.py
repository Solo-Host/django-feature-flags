from __future__ import annotations

from typing import Any, cast

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

UserLike = AbstractBaseUser | AnonymousUser | None


class FeatureFlag(models.Model):
    name = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Machine-readable feature flag name.",
    )
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=False)
    is_public = models.BooleanField(
        default=False,
        help_text=(
            "If enabled, the flag can be evaluated for anonymous requests. "
            "Allowed users are ignored while the flag is public."
        ),
    )
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="feature_flags",
        help_text=(
            "Optional allowlist for authenticated rollouts. "
            "Leave empty to allow every authenticated user."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "feature flag"
        verbose_name_plural = "feature flags"

    def __str__(self) -> str:
        state = "enabled" if self.is_enabled else "disabled"
        return f"{self.name} ({state})"

    def _get_prefetched_relation(self, relation_name: str) -> list[Any] | None:
        prefetched = getattr(self, "_prefetched_objects_cache", {})
        related = prefetched.get(relation_name)
        if related is None:
            return None
        return list(related)

    def _normalize_user(self, user: UserLike) -> AbstractBaseUser | None:
        if user is None or not user.is_authenticated:
            return None
        return user

    def has_user_restrictions(self) -> bool:
        prefetched = self._get_prefetched_relation("allowed_users")
        if prefetched is not None:
            return bool(prefetched)
        return self.allowed_users.exists()

    def has_context_restrictions(self) -> bool:
        prefetched = self._get_prefetched_relation("targets")
        if prefetched is not None:
            return bool(prefetched)
        return self.targets.exists()

    def user_is_allowed(self, user: AbstractBaseUser) -> bool:
        prefetched = self._get_prefetched_relation("allowed_users")
        if prefetched is not None:
            allowed_ids = {str(allowed_user.pk) for allowed_user in prefetched}
            return str(user.pk) in allowed_ids

        return self.allowed_users.filter(pk=user.pk).exists()

    def matches_context(self, context: models.Model) -> bool:
        content_type = ContentType.objects.get_for_model(context, for_concrete_model=False)
        object_id = str(context.pk)

        prefetched = self._get_prefetched_relation("targets")
        if prefetched is not None:
            return any(
                cast(FeatureFlagTarget, target).content_type_id == content_type.pk
                and cast(FeatureFlagTarget, target).object_id == object_id
                for target in prefetched
            )

        return self.targets.filter(content_type=content_type, object_id=object_id).exists()

    def add_target(self, context: models.Model) -> tuple[FeatureFlagTarget, bool]:
        content_type = ContentType.objects.get_for_model(context, for_concrete_model=False)
        return self.targets.get_or_create(content_type=content_type, object_id=str(context.pk))

    def is_enabled_for_context(self, context: models.Model, user: UserLike = None) -> bool:
        return self.is_enabled_for_user(user=user, context=context)

    def is_enabled_for_user(
        self, user: UserLike = None, context: models.Model | None = None
    ) -> bool:
        if not self.is_enabled:
            return False

        if self.has_context_restrictions():
            if context is None or not self.matches_context(context):
                return False

        if self.is_public:
            return True

        normalized_user = self._normalize_user(user)
        if normalized_user is None:
            return False

        if not self.has_user_restrictions():
            return True

        return self.user_is_allowed(normalized_user)


class FeatureFlagTarget(models.Model):
    feature_flag = models.ForeignKey(
        FeatureFlag,
        on_delete=models.CASCADE,
        related_name="targets",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    target = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "feature flag target"
        verbose_name_plural = "feature flag targets"
        constraints = [
            models.UniqueConstraint(
                fields=("feature_flag", "content_type", "object_id"),
                name="feature_flags_unique_target",
            )
        ]
        indexes = [
            models.Index(fields=("content_type", "object_id"), name="feature_flags_target_lookup")
        ]

    def __str__(self) -> str:
        return (
            f"{self.feature_flag.name} -> "
            f"{self.content_type.app_label}.{self.content_type.model}:{self.object_id}"
        )
