import pytest
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from feature_flags.models import FeatureFlag, FeatureFlagTarget


@pytest.mark.django_db
def test_admin_changelist_displays_feature_flags(admin_client):
    flag = FeatureFlag.objects.create(name="beta-dashboard", is_enabled=True)

    response = admin_client.get(reverse("admin:feature_flags_featureflag_changelist"))

    assert response.status_code == 200
    assert flag.name in response.content.decode()


@pytest.mark.django_db
def test_admin_can_create_public_feature_flag(admin_client):
    response = admin_client.post(
        reverse("admin:feature_flags_featureflag_add"),
        {
            "name": "public-flag",
            "description": "A flag for public pages.",
            "is_enabled": "on",
            "is_public": "on",
            "allowed_users": [],
            "targets-TOTAL_FORMS": "0",
            "targets-INITIAL_FORMS": "0",
            "targets-MIN_NUM_FORMS": "0",
            "targets-MAX_NUM_FORMS": "1000",
        },
    )

    assert response.status_code == 302
    created_flag = FeatureFlag.objects.get(name="public-flag")
    assert created_flag.is_public is True
    assert created_flag.is_enabled is True


@pytest.mark.django_db
def test_admin_change_view_displays_context_targets(admin_client, public_flag):
    group = Group.objects.create(name="support")
    public_flag.targets.create(
        content_type=ContentType.objects.get_for_model(group, for_concrete_model=False),
        object_id=str(group.pk),
    )

    response = admin_client.get(
        reverse("admin:feature_flags_featureflag_change", args=[public_flag.pk])
    )

    assert response.status_code == 200
    assert "organizational target" in response.content.decode().lower()
    assert FeatureFlagTarget.objects.filter(feature_flag=public_flag).count() == 1
