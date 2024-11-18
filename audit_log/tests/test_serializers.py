import json

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
