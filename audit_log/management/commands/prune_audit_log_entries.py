from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
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
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Dry run mode i.e. don't commit changes, but show what would be done",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options.get("dry_run")
        if dry_run:
            self.stdout.write(
                self.style.NOTICE(
                    "Running in dry-run mode i.e. not committing changes!"
                )
            )

        try:
            queryset = self.get_queryset(options)
            deleted_count, _ = queryset.delete()
            self.print_success_message(deleted_count, options)
        finally:
            if dry_run:
                transaction.set_rollback(True)

    def get_queryset(self, options):
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
            return queryset  # Return all entries for --all

        if days:
            try:
                days = int(days)
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

        if not (days or is_sent):
            self.stdout.write(
                self.style.ERROR(
                    "Please specify at least one of --days, --is_sent, or --all."
                )
            )
            raise SystemExit(1)

        return queryset

    def print_success_message(self, deleted_count, options):
        days = options.get("days")
        is_sent = options.get("is_sent")

        if days and is_sent:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {deleted_count} sent AuditLog entries older than {days} days."  # noqa: E501
                )
            )
        elif days:
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
        else:  # This is for the --all case
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted all {deleted_count} AuditLog entries."
                )
            )
