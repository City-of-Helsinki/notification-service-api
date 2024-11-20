from typing import Optional, TYPE_CHECKING, Union

from django.db import models
from django.http import HttpRequest

from audit_log.enums import Operation, Status
from audit_log.services import audit_log_service
from audit_log.types import AuditCommitMessage
from audit_log.utils import (
    create_commit_message,
    create_object_states,
    get_remote_address,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


class AuditLogQuerySet(models.QuerySet):
    def with_audit_log(
        self,
        user: "AbstractUser",
        operation: Operation,
        status: Union[Status, str] = Status.SUCCESS.value,
        ip_address: str = "",
        path: str = "",
        _type: Optional[str] = None,
        force_disable_object_states: bool = False,
    ) -> "AuditLogQuerySet":
        """
        Logs the retrieval of this queryset.

        Args:
            user: The user who performed the retrieval.
            operation: The operation that was performed (e.g., "read", "update",
                "delete").
            status: The status of the operation (e.g., "success", "failure").
            ip_address: The IP address of the user who performed the retrieval.
            path: The path of the request that triggered the retrieval.
            _type: The type of object being retrieved. If not specified, the model name
                is used.
            force_disable_object_states: Whether to disable the inclusion of object
                states in the log message. Some times it might be unnecessary to write
                object states in the audit event message.

        Returns:
            The queryset itself, to allow for chaining.

        Raises:
            ValueError: If any of the required arguments are missing or invalid.
        """
        if not user:
            raise ValueError("User cannot be set to None.")

        if not operation:
            raise ValueError("Operation cannot be None or an empty string.")

        if not status:
            raise ValueError("Status cannot be None or an empty string.")

        # Use the model name as a path if it is not given
        if not _type:
            _type = self.model._meta.model_name

        # Get the affected object ids as a list of strings
        object_ids = [str(pk) for pk in self.values_list("pk", flat=True)]

        object_states = None
        if (
            audit_log_service.should_store_object_state()
            and not force_disable_object_states
        ):
            object_states = create_object_states(new_objects=self)

        # Log the queryset retrieval
        message = create_commit_message(
            status=status,
            operation=operation,
            actor=audit_log_service._get_actor_data(user=user, ip_address=ip_address),
            target=audit_log_service._get_target(
                path=path,
                _type=_type,
                object_ids=object_ids,
                object_states=object_states,
            ),
        )
        audit_log_service._commit_to_audit_log(message=AuditCommitMessage(**message))
        return self

    def with_audit_log_and_request(
        self,
        request: HttpRequest,
        operation: Operation,
        status: Union[Status, str] = Status.SUCCESS.value,
        force_disable_object_states: bool = False,
    ) -> "AuditLogQuerySet":
        """
        Logs the retrieval of this queryset, extracting information from the given
        request.

        Args:
            request: The HTTP request that triggered the retrieval.
            operation: The operation that was performed (e.g., "read", "update",
                "delete").
            status: The status of the operation (e.g., "success", "failure").
            force_disable_object_states: Whether to disable the inclusion of object
                states in the log message. Some times it might be unnecessary to write
                object states in the audit event message.

        Returns:
            The queryset itself, to allow for chaining.
        """
        return self.with_audit_log(
            user=request.user,
            operation=operation,
            status=status,
            ip_address=get_remote_address(request),
            path=request.path,
            force_disable_object_states=force_disable_object_states,
        )


class AuditLogManager(models.Manager):
    def get_queryset(self):
        return AuditLogQuerySet(self.model, using=self._db)
