# Create your models here.
from copy import deepcopy

from django.db import models
from django.utils.translation import gettext_lazy as _

from audit_log.managers import AuditLogManager
from common.models import TimestampedModel, UUIDPrimaryKeyModel


class DeliveryLog(UUIDPrimaryKeyModel, TimestampedModel):
    user = models.ForeignKey(
        "users.User",
        related_name="delivery_logs",
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    report = models.JSONField(verbose_name=_("report"), blank=True, null=True)

    objects = AuditLogManager()

    class Meta:
        verbose_name = _("delivery log")
        verbose_name_plural = _("delivery logs")
        ordering = ["-updated_at"]

    def update_report(self, report_data):
        """
        Update delivery of single message base on json data sent from Quriiri to
        our service
        :param report_data: JSON
        :return:
        """
        report = self.report
        updated_messages = deepcopy(report["messages"])
        destination = report_data["destination"]
        for i, message in enumerate(report["messages"]):
            if message.get("converted") == destination:
                updated_messages[i] = report_data
        report["messages"] = updated_messages
        self.report = report
        self.save()
