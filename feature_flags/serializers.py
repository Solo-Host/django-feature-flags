from __future__ import annotations

from rest_framework import serializers

from feature_flags.models import FeatureFlag


class FeatureFlagSerializer(serializers.ModelSerializer):
    enabled = serializers.SerializerMethodField()
    has_user_restrictions = serializers.SerializerMethodField()
    has_context_restrictions = serializers.SerializerMethodField()

    class Meta:
        model = FeatureFlag
        fields = (
            "name",
            "description",
            "is_enabled",
            "is_public",
            "enabled",
            "has_user_restrictions",
            "has_context_restrictions",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_enabled(self, obj: FeatureFlag) -> bool:
        request = self.context.get("request")
        context = self.context.get("feature_flag_context")
        user = getattr(request, "user", None)
        return obj.is_enabled_for_user(user=user, context=context)

    def get_has_user_restrictions(self, obj: FeatureFlag) -> bool:
        return obj.has_user_restrictions()

    def get_has_context_restrictions(self, obj: FeatureFlag) -> bool:
        return obj.has_context_restrictions()
