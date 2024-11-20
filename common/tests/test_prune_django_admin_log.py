from datetime import datetime
from unittest import mock

import pytest
from dateutil.relativedelta import relativedelta
from django.contrib.admin.models import LogEntry
from django.core.management import call_command
from django.db import IntegrityError
from freezegun import freeze_time

from common.factories import LogEntryFactory
from common.utils import utc_datetime

_TEST_TIME = utc_datetime(2022, 8, 1)


_TEST_LOG_ENTRY_CREATION_TIMES: list[datetime] = [
    _TEST_TIME - relativedelta(years=5, seconds=1),  # Over 5 years ago
    _TEST_TIME - relativedelta(years=5),  # Exactly 5 years ago
    _TEST_TIME - relativedelta(months=7),
    _TEST_TIME - relativedelta(months=6),
    _TEST_TIME - relativedelta(months=5),
    _TEST_TIME - relativedelta(months=4),
    _TEST_TIME - relativedelta(months=3),
    _TEST_TIME - relativedelta(months=2),
    _TEST_TIME - relativedelta(months=1),
    _TEST_TIME,
]


@pytest.fixture(autouse=True)
def _log_entries():
    for created_at in _TEST_LOG_ENTRY_CREATION_TIMES:
        with freeze_time(created_at):
            LogEntryFactory.create()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "months,expected_deletion_count",
    [
        (0, 10),
        (1, 9),
        (2, 8),
        (3, 7),
        (4, 6),
        (5, 5),
        (6, 4),
        (7, 3),
        (8, 2),
        (5 * 12, 2),
        (None, 2),
        (5 * 12 + 1, 0),
    ],
)
@pytest.mark.parametrize("dry_run", [False, True])
def test_valid_months(
    months: None | int, expected_deletion_count: int, dry_run: bool, capsys
):
    """
    Test that the prune_django_admin_log command deletes the expected number of logs
    based on the months and dry_run arguments, and the correct message is printed.
    """
    orig_count = 10
    assert LogEntry.objects.count() == orig_count
    with freeze_time(_TEST_TIME):
        kwargs = {"dry_run": dry_run}
        if months is not None:
            kwargs["months"] = months
        call_command("prune_django_admin_log", **kwargs)
    captured = capsys.readouterr()
    dry_run_msg = "Running in dry-run mode i.e. not committing changes!\n"
    del_msg = (
        f"Deleted {expected_deletion_count} Django admin logs "
        f"created at least {5*12 if months is None else months} months ago"
    )
    assert captured.err == ""
    assert del_msg in captured.out
    assert (dry_run_msg in captured.out) == dry_run
    if dry_run:
        assert LogEntry.objects.count() == orig_count
    else:
        assert LogEntry.objects.count() == orig_count - expected_deletion_count


@pytest.mark.django_db
def test_invalid_months(capsys):
    """
    Test that the prune_django_admin_log command raises a ValueError
    if the months argument is negative, and that no logs are deleted.
    """
    orig_log_entry_count = LogEntry.objects.count()
    assert orig_log_entry_count
    kwargs = {"months": -1}
    with pytest.raises(ValueError) as excinfo:
        call_command("prune_django_admin_log", **kwargs)
    assert "Months must be a non-negative integer" in str(excinfo.value)
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""
    assert LogEntry.objects.count() == orig_log_entry_count


@pytest.mark.django_db
def test_unexpected_data_deletion_leads_to_transaction_rollback(capsys):
    """
    Test that if the delete method unexpectedly deletes something else
    than what was expected, then the transaction is rolled back.
    """
    orig_log_entry_count = LogEntry.objects.count()
    assert orig_log_entry_count
    kwargs = {"months": 0}
    queryset_delete = "django.db.models.query.QuerySet.delete"
    with mock.patch(queryset_delete, return_value=(1, {"User": 1})):
        with pytest.raises(IntegrityError) as excinfo:
            call_command("prune_django_admin_log", **kwargs)
    assert "Rolling back deletion to prevent accidental data loss" in str(excinfo.value)
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""
    assert LogEntry.objects.count() == orig_log_entry_count
