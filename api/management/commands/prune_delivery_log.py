from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from django.utils import timezone

from api.models import DeliveryLog


class Command(BaseCommand):
    help = "Remove old delivery logs (i.e. api.DeliveryLog objects)"

    @property
    def default_months(self):
        return 6

    def add_arguments(self, parser):
        parser.add_argument(
            "--months",
            type=int,
            default=self.default_months,
            help="Number of months to keep logs. Default is %(default)s months",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Dry run mode i.e. don't commit changes, but show what would be done",
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        months = kwargs.get("months")
        if months < 0:
            raise ValueError("Months must be a non-negative integer")
        dry_run = kwargs.get("dry_run")
        if dry_run:
            self.stdout.write("Running in dry-run mode i.e. not committing changes!")

        try:
            logs_to_be_deleted = DeliveryLog.objects.filter(
                created_at__lte=timezone.now() - relativedelta(months=months)
            )
            deleted_count, deleted_objects = logs_to_be_deleted.delete()

            # Check that only DeliveryLog objects were deleted and nothing else.
            #
            # This is defensive programming meant to prevent accidental data loss
            # by rolling back deletions in case something else than DeliveryLog objects
            # were deleted.
            if deleted_objects != (
                {"api.DeliveryLog": deleted_count} if deleted_count else {}
            ):
                transaction.set_rollback(True)
                raise IntegrityError(
                    "Rolling back deletion to prevent accidental data loss. "
                    f"Unexpected objects would've been deleted: {deleted_objects}"
                )

            self.stdout.write(
                f"Deleted {deleted_count} delivery logs "
                f"created at least {months} months ago"
            )
        finally:
            if dry_run:
                transaction.set_rollback(True)
