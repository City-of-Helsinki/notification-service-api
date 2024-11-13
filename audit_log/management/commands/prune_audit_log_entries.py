from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from audit_log.models import AuditLogEntry


class Command(BaseCommand):
    help = "Prunes (deletes) AuditLog entries. Use --days to specify an age or --all to clear all entries."  # noqa: E501

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            help="Number of days old entries should be to be deleted.",
        )
        parser.add_argument("--all", action="store_true", help="Delete all entries.")

    def handle(self, *args, **options):
        if options["all"]:
            deleted_count, _ = AuditLogEntry.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted all {deleted_count} AuditLog entries."
                )
            )
        elif options["days"]:
            try:
                days = int(options["days"])
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(
                        "Invalid value for --days. Please provide an integer."
                    )
                )
                raise SystemExit(1)
            past = timezone.now() - timedelta(days=days)

            deleted_count, _ = AuditLogEntry.objects.filter(
                created_at__lte=past
            ).delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {deleted_count} AuditLog entries older than {days} days."  # noqa: E501
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR("Please specify either --days or --all.")
            )
            raise SystemExit(1)
