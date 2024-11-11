from django.conf import settings
from django.db.models.signals import post_delete, post_init, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from api.models import DeliveryLog
from audit_log.enums import Operation, Status
from audit_log.services import audit_log_service
from audit_log.types import AuditCommitMessage
from audit_log.utils import create_commit_message


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=DeliveryLog)
def audit_log_delivery_log_create_update(
    sender, instance, created, path="", ip_address="", **kwargs
):
    message = create_commit_message(
        status=Status.SUCCESS.value,
        operation=Operation.CREATE.value if created else Operation.UPDATE.value,
        actor=audit_log_service._get_actor_data(
            user=instance.user, ip_address=ip_address
        ),
        target=audit_log_service._get_target(path=path, object_ids=[str(instance.id)]),
    )
    audit_log_service._commit_to_audit_log(message=AuditCommitMessage(**message))


@receiver(post_delete, sender=DeliveryLog)
def audit_log_delivery_log_delete(sender, instance, path="", ip_address="", **kwargs):
    message = create_commit_message(
        status=Status.SUCCESS.value,
        operation=Operation.DELETE.value,
        actor=audit_log_service._get_actor_data(
            user=instance.user, ip_address=ip_address
        ),
        target=audit_log_service._get_target(path=path, object_ids=[str(instance.id)]),
    )
    audit_log_service._commit_to_audit_log(message=AuditCommitMessage(**message))


@receiver(post_init, sender=DeliveryLog)
def audit_log_delivery_log_read(sender, instance, path="", ip_address="", **kwargs):
    message = create_commit_message(
        status=Status.SUCCESS.value,
        operation=Operation.READ.value,
        actor=audit_log_service._get_actor_data(
            user=instance.user, ip_address=ip_address
        ),
        target=audit_log_service._get_target(path=path, object_ids=[str(instance.id)]),
    )
    audit_log_service._commit_to_audit_log(message=AuditCommitMessage(**message))
