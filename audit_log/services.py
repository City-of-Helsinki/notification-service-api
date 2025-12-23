import logging
import re
from dataclasses import asdict
from typing import List, Optional, Union

from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from resilient_logger.sources import ResilientLogSource

from audit_log.enums import Operation, Status, StoreObjectState
from audit_log.exceptions import AuditLoggingDisabledError
from audit_log.settings import audit_logging_settings
from audit_log.types import (
    AuditActorData,
    AuditCommitMessage,
    AuditTarget,
    ObjectState,
    ObjectStateDiff,
    ObjectStateWithDiff,
)
from audit_log.utils import (
    create_commit_message,
    create_object_states,
    get_remote_address,
    get_response_status,
    get_user_role,
)
from users.models import User

_OPERATION_MAPPING = {
    "GET": Operation.READ.value,
    "HEAD": Operation.READ.value,
    "OPTIONS": Operation.READ.value,
    "POST": Operation.CREATE.value,
    "PUT": Operation.UPDATE.value,
    "PATCH": Operation.UPDATE.value,
    "DELETE": Operation.DELETE.value,
}


class AuditLogServiceBase:
    """
    Base class for audit log services.

    Provides common functionality for creating audit log messages and committing
    them to a logger and/or database.

    NOTE: The AuditLogServiceBase should not be coupled with the Django
    request and response objects. That should be done in the extending audit log
    service class.
    """

    def _get_operation_name(self, method: str) -> str:
        """
        Determine the operation name based on the request method.

        Args:
            method: The HTTP request method (e.g., "GET", "POST", "PUT").

        Returns:
            str: The operation name (e.g., "READ", "CREATE", "UPDATE", "DELETE").
        """
        try:
            return _OPERATION_MAPPING[method]
        except KeyError:
            return f"Unknown: {method}"

    def _get_actor_data(self, user: User, ip_address: str) -> AuditActorData:
        """
        Create an AuditActorData object from user and IP address information.

        Args:
            user: The User object.
            ip_address: The IP address of the actor.

        Returns:
            AuditActorData: An AuditActorData object.
        """
        return AuditActorData(
            role=get_user_role(user),
            user_id=str(user.pk),
            # `django-helusers` provides an uuid field for the User.
            uuid=str(user.uuid) if hasattr(user, "uuid") else None,
            ip_address=ip_address,
        )

    def _get_target(
        self,
        path: str,
        object_ids: List[str],
        _type: Optional[str] = None,
        object_states: Optional[
            List[ObjectState | ObjectStateDiff | ObjectStateWithDiff]
        ] = None,
    ) -> AuditTarget:
        """
        Create an AuditTarget object from path and object IDs.

        Args:
            path: The request path.
            object_ids: A list of object IDs involved in the operation.
            _type: Actor type, e.g. the name of the model involved
                            in the operation (optional).

        Returns:
            AuditTarget: An AuditTarget object.
        """
        return AuditTarget(
            path=path, type=_type, object_ids=object_ids, object_states=object_states
        )

    def _commit_to_audit_log(self, message: AuditCommitMessage) -> None:
        """
        Commit the audit log message to the logger and/or database.

        Args:
            message: The AuditCommitMessage object.

        Raises:
            AuditLoggingDisabledError: If audit logging is disabled.
        """
        if not self.is_audit_logging_enabled():
            raise AuditLoggingDisabledError("Audit logging is disabled.")

        ResilientLogSource.create_structured(
            level=logging.NOTSET,
            message=message.audit_event.status,
            actor=asdict(message.audit_event.actor),
            operation=message.audit_event.operation,
            target=asdict(message.audit_event.target),
            extra={"status": message.audit_event.status},
        )

    def is_audit_logging_enabled(self) -> bool:
        """
        Check if audit logging is enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        return bool(audit_logging_settings.ENABLED)

    def should_store_object_state(self) -> bool:
        return audit_logging_settings.STORE_OBJECT_STATE != StoreObjectState.NONE


class AuditLogApiService(AuditLogServiceBase):
    """
    Service for managing audit logging in the context of a Django request.

    Inherits from AuditLogServiceBase and provides additional methods for
    extracting information from Django request objects.
    """

    def get_audit_logged_object_ids(self, request: HttpRequest) -> List[str]:
        """
        Retrieve the audit logged object IDs from the request.

        Args:
            request: The Django request object.

        Returns:
            List[str]: A list of object IDs.
        """
        return [
            str(e)
            for e in getattr(request, audit_logging_settings.REQUEST_AUDIT_LOG_VAR, [])
        ]

    def get_operation_name(self, request: HttpRequest) -> str:
        """
        Determine the operation name based on the request method.

        Args:
            request: The Django request object.

        Returns:
            str: The operation name (e.g., "READ", "CREATE", "UPDATE", "DELETE").
        """
        return self._get_operation_name(request.method)

    def get_actor_data(self, request: HttpRequest) -> AuditActorData:
        """
        Extract actor data from the request.

        Args:
            request: The Django request object.

        Returns:
            AuditActorData: An AuditActorData object.
        """
        user = getattr(request, "user", None)
        return self._get_actor_data(user=user, ip_address=get_remote_address(request))

    def get_target(self, request: HttpRequest) -> AuditTarget:
        """
        Get the target of the operation from the request.

        Args:
            request: The Django request object.

        Returns:
            AuditTarget: An AuditTarget object.
        """
        audit_logged_object_ids = list(self.get_audit_logged_object_ids(request))
        return self._get_target(path=request.path, object_ids=audit_logged_object_ids)

    def is_audit_logging_endpoint(self, request: HttpRequest) -> bool:
        """
        Check if the request endpoint should be audit logged.

        Args:
            request: The Django request object.

        Returns:
            bool: True if the endpoint should be logged, False otherwise.
        """
        return bool(re.match(audit_logging_settings.LOGGED_ENDPOINTS_RE, request.path))

    def get_response_status(self, response: HttpResponse) -> Optional[str]:
        """
        Get the response status.

        Args:
            response: The Django response object.

        Returns:
            Optional[str]: The response status or None.
        """
        return get_response_status(response)

    def create_commit_message(
        self, request: HttpRequest, response: HttpResponse
    ) -> AuditCommitMessage:
        """
        Create the audit log message from the request and response.

        Args:
            request: The Django request object.
            response: The Django response object.

        Returns:
            AuditCommitMessage: The formatted audit log message.
        """
        commit_message_base = create_commit_message()
        return AuditCommitMessage(
            audit_event={
                **commit_message_base["audit_event"],
                "status": self.get_response_status(response)
                or f"Unknown: {response.status_code}",
                "operation": self.get_operation_name(request),
                "actor": asdict(self.get_actor_data(request)),
                "target": asdict(self.get_target(request)),
            }
        )

    def commit_to_audit_log(self, request: HttpRequest, response: HttpResponse) -> None:
        """
        Commit the audit log to the logger and/or database.

        Args:
            request: The Django request object.
            response: The Django response object.

        Raises:
            AuditLoggingDisabledError: If audit logging is disabled.
        """
        if not self.get_audit_logged_object_ids(request):
            return

        message = self.create_commit_message(request, response)
        self.delete_audit_logged_object_ids(request)
        self._commit_to_audit_log(message=message)

    def delete_audit_logged_object_ids(self, request: HttpRequest) -> None:
        """
        Delete the audit logged object IDs from the request.

        Args:
            request: The Django request object.
        """
        if hasattr(request, audit_logging_settings.REQUEST_AUDIT_LOG_VAR):
            delattr(request, audit_logging_settings.REQUEST_AUDIT_LOG_VAR)

    def add_audit_logged_object_ids(
        self, request: HttpRequest, instances: QuerySet
    ) -> None:
        """
        Add audit logged object IDs to the request.

        Args:
            request: The Django request object.
            instances: A single instance or a list/queryset of instances
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


def create_api_commit_message_from_request(
    request: HttpRequest,
    operation: Union[Operation, str],
    object_ids: List[str],
    _type: Optional[str] = None,
    new_objects: Optional[Union[QuerySet, List[Model]]] = None,
    old_objects: Optional[Union[QuerySet, List[Model]]] = None,
) -> AuditCommitMessage:
    """Create an audit log message from an API request.

    This function generates an audit log message for actions performed through the API,
    especially when a response object isn't available. It simplifies the logging process
    by assuming a successful operation (Status.SUCCESS) and extracting relevant
    information from the request.

    Args:
        request: The Django HttpRequest object.
        operation: The operation performed (an Operation enum value).
        object_ids: A list of object IDs involved in the operation.
        _type: The type of actor (e.g., the model name) (optional).
        new_objects: A QuerySet or list of new model instances after
            the operation (optional).
        old_objects: A QuerySet or list of old model instances before
            the operation (optional).

    Returns:
        AuditCommitMessage: The formatted audit log message.

    Example:
        >>> # doctest: +SKIP
        ... create_api_commit_message_from_request(
        ...     request=request,
        ...     operation=Operation.UPDATE,
        ...     object_ids=["123"],
        ...     _type="MyModel",
        ... )
    """
    object_states = None

    if old_objects or new_objects:
        if audit_logging_settings.STORE_OBJECT_STATE != StoreObjectState.NONE:
            object_states = create_object_states(
                new_objects=new_objects, old_objects=old_objects
            )

    return AuditCommitMessage(
        **create_commit_message(
            operation=operation,
            status=Status.SUCCESS.value,
            actor=audit_log_service._get_actor_data(
                user=request.user, ip_address=get_remote_address(request)
            ),
            target=audit_log_service._get_target(
                path=request.path,
                _type=_type,
                object_ids=object_ids,
                object_states=object_states,
            ),
        )
    )
