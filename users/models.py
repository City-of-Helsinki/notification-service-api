from django.utils.translation import gettext_lazy as _
from helusers.models import AbstractUser


class User(AbstractUser):
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email
