# Generated by Django 4.2.7 on 2023-11-15 12:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deliverylog",
            name="report",
            field=models.JSONField(blank=True, null=True, verbose_name="report"),
        ),
    ]
