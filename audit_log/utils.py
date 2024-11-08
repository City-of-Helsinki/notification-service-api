from dataclasses import asdict
from typing import Optional, Union

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status

from audit_log.enums import Operation, Role, Status
from audit_log.settings import audit_logging_settings
from audit_log.types import AuditActorData, AuditTarget


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
    if not (x_forwarded_for := request.headers.get("x-forwarded-for")):
        return request.META.get("REMOTE_ADDR")

    remote_addr = x_forwarded_for.split(",")[0]

    # Remove port number from remote_addr
    if "." in remote_addr and ":" in remote_addr:
        # IPv4 with port (`x.x.x.x:x`)
        remote_addr = remote_addr.split(":")[0]
    elif "[" in remote_addr:
        # IPv6 with port (`[:::]:x`)
        remote_addr = remote_addr[1:].split("]")[0]

    return remote_addr


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
