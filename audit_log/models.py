from django.db import models
from django.utils.translation import gettext as _


class AuditLogEntry(models.Model):
    is_sent = models.BooleanField(default=False, verbose_name=_("is sent"))
    message = models.JSONField(verbose_name=_("message"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        verbose_name_plural = "audit log entries"


class DummyTestModel(models.Model):
    """
    A dummy model used for testing purposes.

    This model is not managed by Django's ORM (managed = False),
    meaning it does not have a corresponding table in the database.
    It is used solely for defining data structures in tests.

    Attributes:
        text_field (CharField): A text field with a maximum length of 50 characters.
        number_field (IntegerField): An integer field.
        boolean_field (BooleanField): A boolean field with a default value of False.
    """

    text_field = models.CharField(max_length=50)
    number_field = models.IntegerField()
    boolean_field = models.BooleanField(default=False)

    class Meta:
        managed = False
