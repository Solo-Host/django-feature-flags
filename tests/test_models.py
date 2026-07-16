import pytest
from django.contrib.auth.models import AnonymousUser
from feature_flags.models import FeatureFlag


@pytest.mark.django_db
def test_public_flag_is_enabled_for_anonymous_requests(public_flag):
    assert public_flag.is_enabled_for_user(AnonymousUser()) is True


@pytest.mark.django_db
def test_private_flag_requires_authenticated_user(user):
    flag = FeatureFlag.objects.create(name="private-flag", is_enabled=True)

    assert flag.is_enabled_for_user(AnonymousUser()) is False
    assert flag.is_enabled_for_user(user) is True


@pytest.mark.django_db
def test_user_allowlist_restricts_authenticated_rollout(user, other_user):
    flag = FeatureFlag.objects.create(name="beta-rollout", is_enabled=True)
    flag.allowed_users.add(user)

    assert flag.is_enabled_for_user(user) is True
    assert flag.is_enabled_for_user(other_user) is False


@pytest.mark.django_db
def test_public_flag_ignores_allowed_users(user, other_user):
    flag = FeatureFlag.objects.create(name="public-rollout", is_enabled=True, is_public=True)
    flag.allowed_users.add(user)

    assert flag.is_enabled_for_user(AnonymousUser()) is True
    assert flag.is_enabled_for_user(other_user) is True


@pytest.mark.django_db
def test_context_scoped_flag_requires_matching_context(user, group, other_group):
    flag = FeatureFlag.objects.create(name="group-feature", is_enabled=True)
    flag.add_target(group)

    assert flag.is_enabled_for_user(user, context=group) is True
    assert flag.is_enabled_for_user(user, context=other_group) is False
    assert flag.is_enabled_for_user(user) is False


@pytest.mark.django_db
def test_hybrid_flag_requires_user_and_context(user, other_user, group):
    flag = FeatureFlag.objects.create(name="hybrid-rollout", is_enabled=True)
    flag.allowed_users.add(user)
    flag.add_target(group)

    assert flag.is_enabled_for_user(user, context=group) is True
    assert flag.is_enabled_for_user(other_user, context=group) is False


@pytest.mark.django_db
def test_is_enabled_for_context_uses_same_logic(user, group):
    flag = FeatureFlag.objects.create(name="context-helper", is_enabled=True)
    flag.allowed_users.add(user)
    flag.add_target(group)

    assert flag.is_enabled_for_context(group, user=user) is True
