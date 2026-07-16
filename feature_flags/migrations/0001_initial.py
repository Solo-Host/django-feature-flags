from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeatureFlag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.SlugField(
                        help_text="Machine-readable feature flag name.", max_length=100, unique=True
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("is_enabled", models.BooleanField(default=False)),
                (
                    "is_public",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "If enabled, the flag can be evaluated for anonymous requests. "
                            "Allowed users are ignored while the flag is public."
                        ),
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "allowed_users",
                    models.ManyToManyField(
                        blank=True,
                        help_text=(
                            "Optional allowlist for authenticated rollouts. "
                            "Leave empty to allow every authenticated user."
                        ),
                        related_name="feature_flags",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "feature flag",
                "verbose_name_plural": "feature flags",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="FeatureFlagTarget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("object_id", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="contenttypes.contenttype"
                    ),
                ),
                (
                    "feature_flag",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="targets",
                        to="feature_flags.featureflag",
                    ),
                ),
            ],
            options={
                "verbose_name": "feature flag target",
                "verbose_name_plural": "feature flag targets",
            },
        ),
        migrations.AddConstraint(
            model_name="featureflagtarget",
            constraint=models.UniqueConstraint(
                fields=("feature_flag", "content_type", "object_id"),
                name="feature_flags_unique_target",
            ),
        ),
        migrations.AddIndex(
            model_name="featureflagtarget",
            index=models.Index(
                fields=["content_type", "object_id"], name="feature_flags_target_lookup"
            ),
        ),
    ]
