import json
import logging
import re

from django.db.models import QuerySet
from django.utils import timezone

from audit_log.enums import Operation
from audit_log.exceptions import AuditLoggingDisabledError
from audit_log.models import AuditLogEntry
from audit_log.settings import audit_logging_settings
from audit_log.utils import get_remote_address, get_response_status, get_user_role

_OPERATION_MAPPING = {
    "GET": Operation.READ.value,
    "HEAD": Operation.READ.value,
    "OPTIONS": Operation.READ.value,
    "POST": Operation.CREATE.value,
    "PUT": Operation.UPDATE.value,
    "PATCH": Operation.UPDATE.value,
    "DELETE": Operation.DELETE.value,
}


class AuditLogApiService:
    """
    Service for managing audit logging.

    This class provides methods for:

    - Determining if audit logging is enabled.
    - Checking if a request should be logged.
    - Creating audit log messages.
    - Committing audit logs to a logger and/or database.
    - Managing audit logged object IDs in a request.
    """

    def _get_operation_name(self, request):
        """
        Determine the operation name based on the request method.

        Args:
            request: The Django request object.

        Returns:
            str: The operation name (e.g., "READ", "CREATE", "UPDATE", "DELETE").
        """
        return _OPERATION_MAPPING.get(request.method, f"Unknown: {request.method}")

    def _get_actor_data(self, request):
        """
        Extract actor data from the request.

        Args:
            request: The Django request object.

        Returns:
            dict: A dictionary containing actor information (role, uuid, IP address).
        """
        user = getattr(request, "user", None)
        uuid = getattr(user, "uuid", None)

        return {
            "role": get_user_role(user),
            "uuid": str(uuid) if uuid else None,
            "ip_address": get_remote_address(request),
        }

    def _get_target(self, request):
        """
        Get the target of the operation.

        Args:
            request: The Django request object.

        Returns:
            dict: A dictionary containing the target path and object IDs.
        """
        audit_logged_object_ids = self._get_audit_logged_object_ids(request)
        return {"path": request.path, "object_ids": list(audit_logged_object_ids)}

    def _get_audit_logged_object_ids(self, request):
        """
        Retrieve the audit logged object IDs from the request.

        Args:
            request: The Django request object.

        Returns:
            set: A set of object IDs.
        """
        return getattr(request, audit_logging_settings.REQUEST_AUDIT_LOG_VAR, None)

    def is_audit_logging_enabled(self):
        """
        Check if audit logging is enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        return audit_logging_settings.ENABLED

    def get_response_status(self, response):
        """
        Get the response status.

        Args:
            response: The Django response object.

        Returns:
            str: The response status.
        """
        return get_response_status(response)

    def is_audit_logging_endpoint(self, request):
        """
        Check if the request endpoint should be audit logged.

        Args:
            request: The Django request object.

        Returns:
            bool: True if the endpoint should be logged, False otherwise.
        """
        return re.match(audit_logging_settings.LOGGED_ENDPOINTS_RE, request.path)

    def create_commit_message(self, request, response):
        """
        Create the audit log message.

        Args:
            request: The Django request object.
            response: The Django response object.

        Returns:
            dict: The formatted audit log message.
        """
        current_time = timezone.now()
        iso_8601_datetime = f"{current_time.replace(tzinfo=None).isoformat(sep='T', timespec='milliseconds')}Z"  # noqa: E501
        return {
            "audit_event": {
                "origin": audit_logging_settings.ORIGIN,
                "status": self.get_response_status(response)
                or f"Unknown: {response.status_code}",
                "date_time_epoch": int(current_time.timestamp() * 1000),
                "date_time": iso_8601_datetime,
                "actor": self._get_actor_data(request),
                "operation": self._get_operation_name(request),
                "target": self._get_target(request),
            }
        }

    def commit_to_audit_log(self, request, response):
        """
        Commit the audit log to the logger and/or database.

        Args:
            request: The Django request object.
            response: The Django response object.

        Raises:
            AuditLoggingDisabledError: If audit logging is disabled.
        """
        if not self.is_audit_logging_enabled():
            raise AuditLoggingDisabledError("Audit logging is disabled.")

        if not self._get_audit_logged_object_ids(request):
            return

        message = self.create_commit_message(request, response)

        self.delete_audit_logged_object_ids(request)

        if audit_logging_settings.LOG_TO_LOGGER_ENABLED:
            logger = logging.getLogger("audit")
            logger.info(json.dumps(message))

        if audit_logging_settings.LOG_TO_DB_ENABLED:
            AuditLogEntry.objects.create(message=message)

    def delete_audit_logged_object_ids(self, request):
        """
        Delete the audit logged object IDs from the request.

        Args:
            request: The Django request object.
        """
        delattr(request, audit_logging_settings.REQUEST_AUDIT_LOG_VAR)

    def add_audit_logged_object_ids(self, request, instances):
        """
        Add audit logged object IDs to the request.

        Args:
            request: The Django request object.
            instances: A single instance or a list/queryset of instances.
        """
        request = getattr(request, "_request", request)
        audit_logged_object_ids = set()

        def add_instance(instance):
            if not hasattr(instance, "pk") or not instance.pk:
                return

            audit_logged_object_ids.add(instance.pk)

        if isinstance(instances, QuerySet) or isinstance(instances, list):
            for instance in instances:
                add_instance(instance)
        else:
            add_instance(instances)

        if hasattr(request, audit_logging_settings.REQUEST_AUDIT_LOG_VAR):
            getattr(request, audit_logging_settings.REQUEST_AUDIT_LOG_VAR).update(
                audit_logged_object_ids
            )
        else:
            setattr(
                request,
                audit_logging_settings.REQUEST_AUDIT_LOG_VAR,
                audit_logged_object_ids,
            )


audit_log_service = AuditLogApiService()
