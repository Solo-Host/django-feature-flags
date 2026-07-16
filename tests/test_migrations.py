import pytest
from django.core.management import call_command
from django.db import connection


@pytest.mark.django_db(transaction=True)
def test_initial_migration_can_apply_and_reverse():
    feature_flag_tables = {
        "feature_flags_featureflag",
        "feature_flags_featureflag_allowed_users",
        "feature_flags_featureflagtarget",
    }

    call_command("migrate", "feature_flags", "zero", interactive=False, verbosity=0)
    assert feature_flag_tables.isdisjoint(connection.introspection.table_names())

    call_command("migrate", "feature_flags", "0001_initial", interactive=False, verbosity=0)
    assert feature_flag_tables.issubset(set(connection.introspection.table_names()))

    call_command("migrate", "feature_flags", "zero", interactive=False, verbosity=0)
    assert feature_flag_tables.isdisjoint(connection.introspection.table_names())

    call_command("migrate", "feature_flags", "0001_initial", interactive=False, verbosity=0)
