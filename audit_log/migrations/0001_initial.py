# Generated by Django 4.2.13 on 2024-05-29 13:07

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AuditLogEntry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_sent", models.BooleanField(default=False, verbose_name="is sent")),
                ("message", models.JSONField(verbose_name="message")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
            ],
            options={
                "verbose_name_plural": "audit log entries",
            },
        ),
    ]
