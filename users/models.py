from django.db import models
from django.utils.translation import ugettext_lazy as _
from helusers.models import AbstractUser


class User(AbstractUser):
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class ApiUser(models.Model):
    api_key = models.CharField(max_length=1000, verbose_name=_("api_key"))
    user = models.OneToOneField(
        User,
        verbose_name=_("user"),
        related_name=("api_user"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("api user")
        verbose_name_plural = _("api users")
