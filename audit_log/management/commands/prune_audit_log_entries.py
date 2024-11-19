from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from audit_log.models import AuditLogEntry


class Command(BaseCommand):
    help = "Prunes (deletes) AuditLog entries. Use --days to specify an age, --is_sent to filter by sent status, or --all to clear all entries."  # noqa: E501

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            help="Number of days old entries should be to be deleted.",
        )
        parser.add_argument("--all", action="store_true", help="Delete all entries.")
        parser.add_argument(
            "--is_sent",
            action="store_true",
            help="Only delete entries where is_sent is True.",
        )

    def handle(self, *args, **options):
        queryset = AuditLogEntry.objects.all()
        days = options.get("days")
        is_sent = options.get("is_sent")

        if options["all"]:
            if days or is_sent:
                self.stdout.write(
                    self.style.ERROR(
                        "The option --all cannot be used with --days or --is_sent."
                    )
                )
                raise SystemExit(1)
            deleted_count, _ = queryset.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted all {deleted_count} AuditLog entries."
                )
            )
            return  # Exit early after handling --all

        if days:
            try:
                days = int(days)  # Ensure days is an integer
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(
                        "Invalid value for --days. Please provide an integer."
                    )
                )
                raise SystemExit(1)
            past = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__lte=past)

        if is_sent:
            queryset = queryset.filter(is_sent=True)

        if not (days or is_sent):  # No filtering options provided
            self.stdout.write(
                self.style.ERROR(
                    "Please specify at least one of --days, --is_sent, or --all."
                )
            )
            raise SystemExit(1)

        deleted_count, _ = queryset.delete()

        if days:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {deleted_count} AuditLog entries older than {days} days."  # noqa: E501
                )
            )
        elif is_sent:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {deleted_count} sent AuditLog entries."
                )
            )
