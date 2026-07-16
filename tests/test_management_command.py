from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from feature_flags.models import FeatureFlag


@pytest.mark.django_db
def test_create_command_creates_flag():
    stdout = StringIO()

    call_command("feature_flags", "create", "new-pricing-model", "--public", stdout=stdout)

    created_flag = FeatureFlag.objects.get(name="new-pricing-model")
    assert created_flag.is_public is True
    assert "Created feature flag" in stdout.getvalue()


@pytest.mark.django_db
def test_toggle_command_flips_flag_state():
    flag = FeatureFlag.objects.create(name="beta-dashboard", is_enabled=False)
    stdout = StringIO()

    call_command("feature_flags", "toggle", flag.name, stdout=stdout)

    flag.refresh_from_db()
    assert flag.is_enabled is True
    assert "is now enabled" in stdout.getvalue()


@pytest.mark.django_db
def test_list_command_outputs_flags():
    FeatureFlag.objects.create(name="public-rollout", is_enabled=True, is_public=True)
    stdout = StringIO()

    call_command("feature_flags", "list", stdout=stdout)

    assert "public-rollout: enabled (public)" in stdout.getvalue()


@pytest.mark.django_db
def test_set_command_updates_state_and_access():
    flag = FeatureFlag.objects.create(name="ops-flag", is_enabled=False)
    stdout = StringIO()

    call_command("feature_flags", "set", flag.name, "--enabled", "--public", stdout=stdout)

    flag.refresh_from_db()
    assert flag.is_enabled is True
    assert flag.is_public is True
    assert "set to enabled (public)" in stdout.getvalue()


@pytest.mark.django_db
def test_duplicate_create_command_raises_error():
    FeatureFlag.objects.create(name="duplicate-flag", is_enabled=True)

    with pytest.raises(CommandError):
        call_command("feature_flags", "create", "duplicate-flag")
