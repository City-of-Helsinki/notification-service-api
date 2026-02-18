import json

import pytest

from audit_log.models import DummyTestModel
from audit_log.serializers import ObjectStateSerializer


class TestObjectStateSerializer:
    def test_serialize(self):
        # Create some dummy model instances
        obj1 = DummyTestModel(text_field="value1", number_field=1, boolean_field=True)
        obj2 = DummyTestModel(text_field="value2", number_field=2, boolean_field=False)

        # Serialize a QuerySet
        queryset = [obj1, obj2]
        serialized_queryset = ObjectStateSerializer.serialize(queryset)
        assert isinstance(serialized_queryset, str)
        assert json.loads(serialized_queryset)  # Check if valid JSON

        # Serialize a list of instances
        list_of_instances = [obj1, obj2]
        serialized_list = ObjectStateSerializer.serialize(list_of_instances)
        assert isinstance(serialized_list, str)
        assert json.loads(serialized_list)  # Check if valid JSON

    def test_to_python(self):
        json_str = '[{"model": "audit_log.dummytestmodel", "pk": 1, "fields": {"text_field": "value1", "number_field": 1, "boolean_field": true}}]'  # noqa: E501
        python_objects = ObjectStateSerializer.to_python(json_str)
        assert isinstance(python_objects, list)
        assert isinstance(python_objects[0], dict)
        assert python_objects[0]["model"] == "audit_log.dummytestmodel"

    def test_get_fields_states(self):
        # Create some dummy model instances
        obj1 = DummyTestModel(text_field="value1", number_field=1, boolean_field=True)
        obj2 = DummyTestModel(text_field="value2", number_field=2, boolean_field=False)

        # Test with no fields argument (all fields)
        queryset = [obj1, obj2]
        all_fields = ObjectStateSerializer.get_fields_states(queryset)
        assert len(all_fields) == 2
        assert all_fields[0]["text_field"] == "value1"

        # Test with specific fields
        fields = ["text_field", "boolean_field"]
        filtered_fields = ObjectStateSerializer.get_fields_states(
            queryset, fields=fields
        )
        assert len(filtered_fields) == 2
        assert "text_field" in filtered_fields[0]
        assert "boolean_field" in filtered_fields[0]
        assert "number_field" not in filtered_fields[0]

    def test_filter_dicts(self):
        dicts = [
            {"a": 1, "b": 2, "c": 3},
            {"b": 4, "c": 5, "d": 6},
            {"a": 7, "c": 8, "e": 9},
        ]
        desired_keys = ["a", "c"]
        filtered_dicts = ObjectStateSerializer.filter_dicts(dicts, desired_keys)
        assert filtered_dicts == [
            {"a": 1, "c": 3},
            {"c": 5},
            {"a": 7, "c": 8},
        ]

    def test_normalize_delivery_log_messages_dict_to_list(self):
        """Test that DeliveryLog messages are converted from dict to list format."""
        # Dict format (how DeliveryLog stores it)
        report_dict = {
            "errors": [],
            "warnings": [],
            "messages": {
                "+358401234567": {"converted": "+358401234567", "status": "CREATED"},
                "+358407654321": {"converted": "+358407654321", "status": "DELIVERED"},
            },
        }

        # Convert in place
        ObjectStateSerializer._normalize_delivery_log_messages(report_dict)

        # Verify it was converted to list
        assert isinstance(report_dict["messages"], list)
        assert len(report_dict["messages"]) == 2

        # Verify message data is preserved
        converted_numbers = {msg["converted"] for msg in report_dict["messages"]}
        assert "+358401234567" in converted_numbers
        assert "+358407654321" in converted_numbers

        # Verify status fields are preserved
        for msg in report_dict["messages"]:
            assert "converted" in msg
            assert "status" in msg

    def test_normalize_delivery_log_messages_already_list(self):
        """Test that already-list messages are not modified."""
        # List format (already normalized)
        report_list = {
            "errors": [],
            "warnings": [],
            "messages": [
                {"converted": "+358401234567", "status": "CREATED"},
                {"converted": "+358407654321", "status": "DELIVERED"},
            ],
        }

        original = report_list["messages"].copy()

        # Convert (should be idempotent)
        ObjectStateSerializer._normalize_delivery_log_messages(report_list)

        # Verify it's still a list and unchanged
        assert isinstance(report_list["messages"], list)
        assert report_list["messages"] == original

    def test_normalize_delivery_log_messages_no_messages(self):
        """Test with report that has no messages field."""
        report_empty = {"errors": [], "warnings": []}

        # Should not raise an error
        ObjectStateSerializer._normalize_delivery_log_messages(report_empty)

        # Report should be unchanged
        assert "messages" not in report_empty

    @pytest.mark.django_db
    def test_get_fields_states_converts_delivery_log_messages(self):
        """Integration test: verify get_fields_states converts DeliveryLog messages."""
        from api.models import DeliveryLog
        from users.factories import UserFactory

        # Create DeliveryLog with dict format (normal storage)
        delivery_log = DeliveryLog.objects.create(
            user=UserFactory(),
            report={
                "errors": [],
                "warnings": [],
                "messages": {
                    "+358401234567": {
                        "converted": "+358401234567",
                        "status": "CREATED",
                    },
                },
            },
        )

        # Serialize using ObjectStateSerializer (used by audit log)
        serialized = ObjectStateSerializer.get_fields_states([delivery_log])

        # Verify the serialized version has list format
        assert len(serialized) == 1
        assert "report" in serialized[0]
        assert isinstance(serialized[0]["report"]["messages"], list)
        assert len(serialized[0]["report"]["messages"]) == 1
        assert serialized[0]["report"]["messages"][0]["converted"] == "+358401234567"

        # Verify original DeliveryLog still has dict format in DB
        delivery_log.refresh_from_db()
        assert isinstance(delivery_log.report["messages"], dict)
        assert "+358401234567" in delivery_log.report["messages"]
