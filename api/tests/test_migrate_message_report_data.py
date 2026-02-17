"""
Tests for migration 0003_convert_messages_to_list.

These tests verify that the migration correctly converts DeliveryLog report
messages from dict format to list format (and back for reverse migration).
"""

import uuid

import pytest


@pytest.mark.django_db
def test_forward_migration_converts_dict_to_list(migrator):
    """Test that migration 0003 converts messages from dict to list format."""
    # Start at migration 0002 (before the conversion)
    old_state = migrator.apply_initial_migration(
        ("api", "0002_alter_deliverylog_report")
    )

    # Get models from old state
    User = old_state.apps.get_model("users", "User")
    DeliveryLog = old_state.apps.get_model("api", "DeliveryLog")

    # Create test user
    user = User.objects.create(username="test_migration", uuid=uuid.uuid4())

    # Create DeliveryLog with OLD dict format
    log = DeliveryLog.objects.create(
        user=user,
        report={
            "errors": [],
            "warnings": [],
            "messages": {
                "+358401234567": {"converted": "+358401234567", "status": "CREATED"},
                "+358407654321": {"converted": "+358407654321", "status": "DELIVERED"},
            },
        },
    )
    log_id = log.id

    # Verify old format is dict
    assert isinstance(log.report["messages"], dict)
    assert "+358401234567" in log.report["messages"]

    # Apply the migration
    new_state = migrator.apply_tested_migration(
        ("api", "0003_convert_messages_to_list")
    )

    # Get model from new state
    DeliveryLog = new_state.apps.get_model("api", "DeliveryLog")

    # Retrieve the log and verify new format
    log = DeliveryLog.objects.get(id=log_id)

    # Verify new format is list
    assert isinstance(log.report["messages"], list)
    assert len(log.report["messages"]) == 2

    # Verify messages have the expected fields (no redundant 'phone' field)
    converted_numbers = [msg["converted"] for msg in log.report["messages"]]
    assert "+358401234567" in converted_numbers
    assert "+358407654321" in converted_numbers

    # Verify message data is preserved
    for msg in log.report["messages"]:
        assert "converted" in msg
        assert "status" in msg


@pytest.mark.django_db
def test_reverse_migration_converts_list_to_dict(migrator):
    """Test that reverse migration converts messages from list back to dict format."""
    # Start at migration 0003 (after the conversion)
    new_state = migrator.apply_initial_migration(
        ("api", "0003_convert_messages_to_list")
    )

    # Get models from new state
    User = new_state.apps.get_model("users", "User")
    DeliveryLog = new_state.apps.get_model("api", "DeliveryLog")

    # Create test user
    user = User.objects.create(username="test_reverse", uuid=uuid.uuid4())

    # Create DeliveryLog with NEW list format
    log = DeliveryLog.objects.create(
        user=user,
        report={
            "errors": [],
            "warnings": [],
            "messages": [
                {"converted": "+358401234567", "status": "CREATED"},
                {"converted": "+358407654321", "status": "DELIVERED"},
            ],
        },
    )
    log_id = log.id

    # Verify new format is list
    assert isinstance(log.report["messages"], list)
    assert len(log.report["messages"]) == 2

    # Unapply the migration (go back to 0002)
    old_state = migrator.apply_tested_migration(
        ("api", "0002_alter_deliverylog_report")
    )

    # Get model from old state
    DeliveryLog = old_state.apps.get_model("api", "DeliveryLog")

    # Retrieve the log and verify old format
    log = DeliveryLog.objects.get(id=log_id)

    # Verify old format is dict
    assert isinstance(log.report["messages"], dict)
    assert "+358401234567" in log.report["messages"]
    assert "+358407654321" in log.report["messages"]

    # Verify message data is preserved
    for phone, msg in log.report["messages"].items():
        assert "converted" in msg
        assert "status" in msg
        assert msg["converted"] == phone
