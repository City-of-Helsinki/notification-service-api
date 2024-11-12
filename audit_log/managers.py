from typing import TYPE_CHECKING, Union

from django.db import models

from audit_log.enums import Operation, Status
from audit_log.services import audit_log_service
from audit_log.types import AuditCommitMessage
from audit_log.utils import create_commit_message

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


class AuditLogQuerySet(models.QuerySet):
    def with_audit_log(
        self,
        user: "AbstractUser",
        operation: Union[Operation, str],
        status: Union[Status, str] = Status.SUCCESS.value,
        ip_address="",
    ):
        # Use the model name as a path
        path = self.model.__name__

        # Get the affected object ids as a list of strings
        object_ids = [str(pk_tuple[0]) for pk_tuple in self.values_list("pk")]

        # Log the queryset retrieval
        message = create_commit_message(
            status=status,
            operation=operation,
            actor=audit_log_service._get_actor_data(user=user, ip_address=ip_address),
            target=audit_log_service._get_target(path=path, object_ids=object_ids),
        )
        audit_log_service._commit_to_audit_log(message=AuditCommitMessage(**message))
        return self


class AuditLogManager(models.Manager):
    def get_queryset(self):
        return AuditLogQuerySet(self.model, using=self._db)
