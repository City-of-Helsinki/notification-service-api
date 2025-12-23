from dataclasses import asdict
from itertools import zip_longest
from typing import Any, Dict, List, Optional, Union

from django.db.models import Model, QuerySet
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status

from audit_log.enums import Operation, Role, Status, StoreObjectState
from audit_log.serializers import ObjectStateSerializer
from audit_log.settings import audit_logging_settings
from audit_log.types import (
    AuditActorData,
    AuditTarget,
    ObjectState,
    ObjectStateDiff,
    ObjectStateWithDiff,
)


def is_list_of_strings(value):
    """
    Checks if a value is a list of strings.

    Args:
        value: The value to check.

    Returns:
        True if the value is a list of strings, False otherwise.
    """
    if not isinstance(value, list):
        return False
    for item in value:
        if not isinstance(item, str):
            return False
    return True


def get_remote_address(request):
    """
    Get the client's IP address from the request.

    Handles cases where the request is behind a proxy (using 'x-forwarded-for' header).

    Args:
        request: The Django request object.

    Returns:
        str: The client's IP address.
    """
    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded_for.split(",")[0] or None

    if not client_ip:
        client_ip = request.META.get("REMOTE_ADDR")

    if client_ip:
        # Strip port from ip address if present
        if "[" in client_ip:
            # Bracketed IPv6 like [2001:db8::1]:1234
            client_ip = client_ip.lstrip("[").split("]")[0]
        elif "." in client_ip and client_ip.count(":") == 1:
            # IPv4 with port
            client_ip = client_ip.split(":")[0]
    return client_ip


def get_user_role(user):
    """
    Determine the user's role for audit logging.

    Args:
        user: The Django user object.

    Returns:
        str: The user's role (e.g., "ANONYMOUS", "USER", "ADMIN").
    """
    if user is None or not user.is_authenticated:
        return Role.ANONYMOUS.value
    elif user.is_staff or user.is_superuser:
        return Role.ADMIN.value
    return Role.USER.value


def get_response_status(response: HttpResponse) -> Optional[str]:
    """
    Get the response status for audit logging.

    Args:
        response: The Django response object.

    Returns:
        Optional[str]: The response status (e.g., "SUCCESS", "FORBIDDEN") or None.
    """
    if 200 <= response.status_code < 300:
        return Status.SUCCESS.value
    elif (
        response.status_code == status.HTTP_401_UNAUTHORIZED
        or response.status_code == status.HTTP_403_FORBIDDEN
    ):
        return Status.FORBIDDEN.value

    return None


def diff_dicts(old_dict: Dict[str, Any], new_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates the difference between two dictionaries.

    Returns a new dictionary containing only the changed keys and values.

    NOTE: The deleted keys are not included in the output.
    """
    diff = {}
    for key in new_dict:
        if key not in old_dict or new_dict[key] != old_dict[key]:
            diff[key] = new_dict[key]
    return diff


def create_object_states(
    new_objects: Optional[Union[QuerySet, List[Model]]] = None,
    old_objects: Optional[Union[QuerySet, List[Model]]] = None,
) -> Optional[List[ObjectState | ObjectStateDiff | ObjectStateWithDiff]]:
    if audit_logging_settings.STORE_OBJECT_STATE == StoreObjectState.NONE:
        return None

    if not new_objects and not old_objects:
        return None

    new_object_state = (
        ObjectStateSerializer.get_fields_states(new_objects) if new_objects else []
    )
    old_object_state = (
        ObjectStateSerializer.get_fields_states(old_objects) if old_objects else []
    )

    if audit_logging_settings.STORE_OBJECT_STATE == StoreObjectState.DIFF:
        return [
            ObjectStateDiff(object_state_diff=diff_dicts(old_entry, new_entry))
            for old_entry, new_entry in zip_longest(
                old_object_state, new_object_state, fillvalue={}
            )
            if diff_dicts(old_entry, new_entry)
        ]

    elif audit_logging_settings.STORE_OBJECT_STATE == StoreObjectState.ALL:
        return [
            ObjectStateWithDiff(
                old_object_state=old_entry,
                new_object_state=new_entry,
                object_state_diff=diff_dicts(old_entry, new_entry),
            )
            for old_entry, new_entry in zip_longest(
                old_object_state, new_object_state, fillvalue={}
            )
        ]

    return [
        ObjectState(old_object_state=old_entry, new_object_state=new_entry)
        for old_entry, new_entry in zip_longest(
            old_object_state, new_object_state, fillvalue={}
        )
    ]


def create_commit_message(
    status: Optional[str] = None,
    operation: Optional[Union[Operation, str]] = None,
    actor: Optional[AuditActorData] = None,
    target: Optional[AuditTarget] = None,
):
    current_time = timezone.now()
    iso_8601_datetime = f"{current_time.replace(tzinfo=None).isoformat(sep='T', timespec='milliseconds')}Z"  # noqa: E501
    return {
        "audit_event": {
            "origin": audit_logging_settings.ORIGIN,
            "date_time_epoch": int(current_time.timestamp() * 1000),
            "date_time": iso_8601_datetime,
            "status": status,
            "operation": operation,
            "actor": asdict(actor) if actor else None,
            "target": asdict(target) if target else None,
        }
    }
