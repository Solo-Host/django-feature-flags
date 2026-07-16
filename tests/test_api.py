import pytest
from django.urls import reverse
from feature_flags.models import FeatureFlag
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_public_endpoint_allows_anonymous_access(api_client, public_flag):
    FeatureFlag.objects.create(name="private-flag", is_enabled=True)

    response = api_client.get(reverse("feature_flags:feature-flag-public"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {public_flag.name: True}


@pytest.mark.django_db
def test_public_endpoint_respects_context_filters(api_client, group):
    flag = FeatureFlag.objects.create(name="group-rollout", is_enabled=True, is_public=True)
    flag.add_target(group)

    no_context_response = api_client.get(reverse("feature_flags:feature-flag-public"))
    with_context_response = api_client.get(
        reverse("feature_flags:feature-flag-public"),
        {
            "context_app_label": "auth",
            "context_model": "group",
            "context_id": group.pk,
        },
    )

    assert no_context_response.json() == {}
    assert with_context_response.json() == {"group-rollout": True}


@pytest.mark.django_db
def test_all_enabled_requires_authentication(api_client):
    response = api_client.get(reverse("feature_flags:feature-flag-all-enabled"))

    assert response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}


@pytest.mark.django_db
def test_all_enabled_returns_authenticated_flags(api_client, user, other_user):
    FeatureFlag.objects.create(name="auth-flag", is_enabled=True)
    restricted_flag = FeatureFlag.objects.create(name="beta-only", is_enabled=True)
    restricted_flag.allowed_users.add(user)
    FeatureFlag.objects.create(name="marketing-banner", is_enabled=True, is_public=True)

    api_client.force_authenticate(user=user)
    response = api_client.get(reverse("feature_flags:feature-flag-all-enabled"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "auth-flag": True,
        "beta-only": True,
        "marketing-banner": True,
    }

    api_client.force_authenticate(user=other_user)
    response = api_client.get(reverse("feature_flags:feature-flag-all-enabled"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "auth-flag": True,
        "marketing-banner": True,
    }


@pytest.mark.django_db
def test_is_enabled_endpoint_returns_single_flag_state(api_client, user, group):
    flag = FeatureFlag.objects.create(name="group-beta", is_enabled=True)
    flag.allowed_users.add(user)
    flag.add_target(group)

    api_client.force_authenticate(user=user)
    response = api_client.get(
        reverse("feature_flags:feature-flag-is-enabled", kwargs={"name": flag.name}),
        {
            "context_app_label": "auth",
            "context_model": "group",
            "context_id": group.pk,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"enabled": True}


@pytest.mark.django_db
def test_context_query_requires_complete_parameters(api_client):
    response = api_client.get(
        reverse("feature_flags:feature-flag-public"),
        {"context_app_label": "auth"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_list_endpoint_returns_serialized_flag_metadata(api_client, user, group):
    flag = FeatureFlag.objects.create(
        name="workspace-insights",
        description="Roll out the insights dashboard.",
        is_enabled=True,
    )
    flag.allowed_users.add(user)
    flag.add_target(group)

    api_client.force_authenticate(user=user)
    response = api_client.get(reverse("feature_flags:feature-flag-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "name": "workspace-insights",
            "description": "Roll out the insights dashboard.",
            "is_enabled": True,
            "is_public": False,
            "enabled": False,
            "has_user_restrictions": True,
            "has_context_restrictions": True,
            "created_at": response.json()[0]["created_at"],
            "updated_at": response.json()[0]["updated_at"],
        }
    ]


@pytest.mark.django_db
def test_invalid_context_model_returns_bad_request(api_client):
    response = api_client.get(
        reverse("feature_flags:feature-flag-public"),
        {
            "context_app_label": "not-real",
            "context_model": "missing",
            "context_id": "1",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_missing_context_object_returns_not_found(api_client):
    response = api_client.get(
        reverse("feature_flags:feature-flag-public"),
        {
            "context_app_label": "auth",
            "context_model": "group",
            "context_id": "999999",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
