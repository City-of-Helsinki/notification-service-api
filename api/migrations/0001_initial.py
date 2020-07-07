# Generated by Django 2.2.13 on 2020-07-07 12:18

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0002_apiuser"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryLog",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated_at"),
                ),
                ("payload", models.TextField(blank=True, verbose_name="payload")),
                (
                    "api_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="delivery_logs",
                        to="users.ApiUser",
                        verbose_name="api user",
                    ),
                ),
            ],
            options={
                "verbose_name": "delivery log",
                "verbose_name_plural": "delivery logs",
            },
        ),
    ]
