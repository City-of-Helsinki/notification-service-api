import json
from typing import Any, Dict, List, Optional, Union

from django.core import serializers
from django.db.models.query import QuerySet


class ObjectStateSerializer:
    """
    Serializes and deserializes Django model instances, with options
    for filtering fields.

    ObjectStateSerializer is implemented to be a helper utility to
    create the content for audit logging target, when object states
    of the audit log events are wanted to be stored in the audit logs.
    """

    @classmethod
    def _normalize_delivery_log_messages(cls, report: Dict[str, Any]) -> None:
        """
        Convert DeliveryLog report messages from dict to list format in-place.

        This prevents Elasticsearch field limit issues when audit logs are indexed.
        DeliveryLog stores messages as dict in the database, but audit logs need
        list format to avoid creating unlimited dynamic fields in Elasticsearch.

        Converts:
            {"messages": {"+358...": {"converted": "+358...", "status": "..."}}}
        To:
            {"messages": [{"converted": "+358...", "status": "..."}]}

        Args:
            report: The report dict that may contain a 'messages' field
        """
        if not report or "messages" not in report:
            return

        messages = report["messages"]

        # Only convert if it's a dict (not already a list)
        if isinstance(messages, dict):
            # Convert dict values to list, preserving message data
            report["messages"] = list(messages.values())

    @classmethod
    def serialize(cls, obj: Union[QuerySet, List]) -> str:
        """
        Serializes a QuerySet or list of model instances to a JSON string.

        Args:
            obj: The QuerySet or list of model instances to serialize.

        Returns:
            A JSON string representing the serialized objects.
        """
        return serializers.serialize("json", obj)

    @classmethod
    def to_python(cls, json_str: str) -> List[Dict[str, Any]]:
        """
        Deserializes a JSON string to a list of Python dictionaries.

        Args:
            json_str: The JSON string to deserialize.

        Returns:
            A list of Python dictionaries representing the deserialized objects.
        """
        return json.loads(json_str)

    @classmethod
    def get_fields_states(
        cls, obj: Union[QuerySet, List], fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Serializes a QuerySet or list of model instances to a JSON string,
        optionally filtering the fields.

        Args:
            obj: The QuerySet or list of model instances to serialize.
            fields: An optional list of field names to include in the output.
                If None, all fields are included.

        Returns:
            A list of dictionaries, where each dictionary represents a
            serialized object, optionally with only the specified fields.
        """
        json_str = cls.serialize(obj)
        serialized_objects = cls.to_python(json_str)
        fields_dicts = [entry["fields"] for entry in serialized_objects]

        # Normalize DeliveryLog messages for Elasticsearch compatibility
        for field_dict in fields_dicts:
            if "report" in field_dict:
                cls._normalize_delivery_log_messages(field_dict["report"])

        if fields:
            return cls.filter_dicts(fields_dicts, desired_keys=fields)
        return fields_dicts

    @classmethod
    def filter_dicts(
        cls, dicts: List[Dict[str, Any]], desired_keys: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filters a list of dictionaries to include only the desired keys.

        Args:
            dicts: A list of dictionaries.
            desired_keys: A list of keys to include in the output dictionaries.

        Returns:
            A list of dictionaries, where each dictionary contains only the
            desired keys.

        Example:
            >>> dicts = [
            ...     {"a": 1, "b": 2, "c": 3},
            ...     {"b": 4, "c": 5, "d": 6},
            ...     {"a": 7, "c": 8, "e": 9},
            ... ]
            >>> desired_keys = ["a", "c"]
            >>> ObjectStateSerializer.filter_dicts(dicts, desired_keys)
            [{'a': 1, 'c': 3}, {'c': 5}, {'a': 7, 'c': 8}]
        """
        return [{key: d[key] for key in desired_keys if key in d} for d in dicts]
