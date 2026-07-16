import pytest
from feature_flags.models import FeatureFlag
from feature_flags.utils import is_feature_enabled


@pytest.mark.django_db
def test_missing_flag_defaults_to_disabled(user):
    assert is_feature_enabled("missing-flag", user=user) is False


@pytest.mark.django_db
def test_flag_cache_is_invalidated_when_flag_changes(user):
    flag = FeatureFlag.objects.create(name="dashboard-v2", is_enabled=False)

    assert is_feature_enabled(flag.name, user=user) is False

    flag.is_enabled = True
    flag.save(update_fields=["is_enabled", "updated_at"])

    assert is_feature_enabled(flag.name, user=user) is True


@pytest.mark.django_db
def test_flag_cache_is_invalidated_when_allowed_users_change(user, other_user):
    flag = FeatureFlag.objects.create(name="beta-import", is_enabled=True)

    assert is_feature_enabled(flag.name, user=other_user) is True

    flag.allowed_users.add(user)

    assert is_feature_enabled(flag.name, user=other_user) is False
    assert is_feature_enabled(flag.name, user=user) is True


@pytest.mark.django_db
def test_context_is_part_of_cache_key(user, group, other_group):
    flag = FeatureFlag.objects.create(name="team-rollout", is_enabled=True)
    flag.add_target(group)

    assert is_feature_enabled(flag.name, user=user, context=group) is True
    assert is_feature_enabled(flag.name, user=user, context=other_group) is False
