# Create your models here.
from common.models import TimestampedModel, UUIDPrimaryKeyModel
from django.db import models
from django.utils.translation import ugettext_lazy as _


class DeliveryLog(UUIDPrimaryKeyModel, TimestampedModel):
    api_user = models.ForeignKey(
        "users.ApiUser",
        related_name="delivery_logs",
        on_delete=models.CASCADE,
        verbose_name=_("api user"),
    )
    payload = models.TextField(verbose_name=_("payload"), blank=True)

    class Meta:
        verbose_name = _("delivery log")
        verbose_name_plural = _("delivery logs")
