import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from feature_flags.models import FeatureFlag


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(username="user", password="password")


@pytest.fixture
def other_user(db):
    return get_user_model().objects.create_user(username="other-user", password="password")


@pytest.fixture
def group(db):
    return Group.objects.create(name="beta-group")


@pytest.fixture
def other_group(db):
    return Group.objects.create(name="control-group")


@pytest.fixture
def public_flag(db):
    return FeatureFlag.objects.create(
        name="new-pricing-model",
        description="Expose a new public pricing page experience.",
        is_enabled=True,
        is_public=True,
    )
