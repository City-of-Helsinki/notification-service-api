from django.db import models
from django.utils.translation import gettext as _


class AuditLogEntry(models.Model):
    is_sent = models.BooleanField(default=False, verbose_name=_("is sent"))
    message = models.JSONField(verbose_name=_("message"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        verbose_name_plural = "audit log entries"

        # NOTE: GinIndex could improve the search performance
        # https://docs.djangoproject.com/en/5.1/ref/contrib/postgres/indexes/.
        # indexes = [
        #       GinIndex(fields=["message"], name="message_gin_idx"),
        #       # Example partial GinIndex:
        #       # GinIndex(
        #       #   fields=["message__audit_event__actor"],
        #       #   name="message_audit_event_actor_gin_idx"),
        # ]
