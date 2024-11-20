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
        ip_address="",
        path="",
        _type: Optional[str] = None,
        force_disable_object_states=False,
    ):
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
        force_disable_object_states=False,
    ):
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
