from django.contrib import admin

from feature_flags.models import FeatureFlag, FeatureFlagTarget


class FeatureFlagTargetInline(admin.TabularInline):
    model = FeatureFlagTarget
    extra = 0
    verbose_name = "organizational target"
    verbose_name_plural = "organizational targets"


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_enabled",
        "is_public",
        "allowed_user_count",
        "target_count",
        "updated_at",
    )
    list_filter = ("is_enabled", "is_public", "created_at", "updated_at")
    search_fields = ("name", "description")
    filter_horizontal = ("allowed_users",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (FeatureFlagTargetInline,)
    fieldsets = (
        (
            "Flag info",
            {
                "fields": ("name", "description", "is_enabled"),
            },
        ),
        (
            "Access",
            {
                "fields": ("is_public", "allowed_users"),
                "description": (
                    "Public flags are available to anonymous requests. "
                    "Allowed users only apply to non-public flags."
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    @admin.display(description="Allowed users")
    def allowed_user_count(self, obj: FeatureFlag) -> int:
        return obj.allowed_users.count()

    @admin.display(description="Context targets")
    def target_count(self, obj: FeatureFlag) -> int:
        return obj.targets.count()
