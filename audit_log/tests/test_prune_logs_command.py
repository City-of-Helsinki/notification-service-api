from datetime import timedelta

import pytest
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from audit_log.models import AuditLogEntry

EMPTY_MESSAGE = {}


@pytest.mark.django_db
class PruneAuditLogEntriesTests(TestCase):
    def setUp(self):
        # Create some AuditLog entries with different creation timestamps

        self.entry1 = AuditLogEntry.objects.create(message=EMPTY_MESSAGE, is_sent=True)
        self.entry1.created_at = timezone.now() - timedelta(days=5)
        self.entry1.save()

        self.entry2 = AuditLogEntry.objects.create(message=EMPTY_MESSAGE, is_sent=False)
        self.entry2.created_at = timezone.now() - timedelta(days=5)
        self.entry2.save()

        self.entry3 = AuditLogEntry.objects.create(message=EMPTY_MESSAGE, is_sent=True)
        self.entry3.created_at = timezone.now() - timedelta(days=2)
        self.entry3.save()

        self.entry4 = AuditLogEntry.objects.create(message=EMPTY_MESSAGE, is_sent=True)

    def test_prune_audit_log_entries_with_days(self):
        # Call the command with the --days option
        call_command("prune_audit_log_entries", days=3)

        # Check that the old entry is deleted
        self.assertFalse(AuditLogEntry.objects.filter(pk=self.entry1.pk).exists())
        self.assertFalse(AuditLogEntry.objects.filter(pk=self.entry2.pk).exists())
        # Check that the recent entries are not deleted
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry3.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry4.pk).exists())

    def test_prune_audit_log_entries_with_all(self):
        # Call the command with the --all option
        call_command("prune_audit_log_entries", all=True)

        # Check that all entries are deleted
        self.assertListEqual(list(AuditLogEntry.objects.all()), [])

    def test_prune_audit_log_entries_with_no_options(self):
        # Call the command with no options
        with self.assertRaises(SystemExit):  # Expect the command to exit with an error
            call_command("prune_audit_log_entries")

    def test_prune_audit_log_entries_with_invalid_days(self):
        # Call the command with an invalid --days option
        with self.assertRaises(SystemExit):  # Expect the command to exit with an error
            call_command("prune_audit_log_entries", days="abc")

    def test_prune_audit_log_entries_with_is_sent(self):
        call_command("prune_audit_log_entries", is_sent=True)

        # Entry2 should NOT be deleted (is_sent=False)
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry2.pk).exists())

        # Entry1, Entry3 and Entry4 should be deleted (is_sent=True)
        self.assertFalse(AuditLogEntry.objects.filter(pk=self.entry1.pk).exists())
        self.assertFalse(AuditLogEntry.objects.filter(pk=self.entry3.pk).exists())
        self.assertFalse(AuditLogEntry.objects.filter(pk=self.entry4.pk).exists())

    def test_prune_audit_log_entries_with_days_and_is_sent(self):
        call_command("prune_audit_log_entries", days=3, is_sent=True)

        # Entry1 should be deleted (old and is_sent=True)
        self.assertFalse(AuditLogEntry.objects.filter(pk=self.entry1.pk).exists())
        # Entry2 should NOT be deleted (old but is_sent=False)
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry2.pk).exists())
        # Entry3 and Entry4 should NOT be deleted (recent)
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry3.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry4.pk).exists())

    def test_prune_audit_log_entries_with_all_and_is_sent(self):
        with self.assertRaises(SystemExit):
            call_command("prune_audit_log_entries", all=True, is_sent=True)

    def test_dry_run_with_days(self):
        call_command("prune_audit_log_entries", days=3, dry_run=True)

        # Assert that no entries were actually deleted
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry1.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry2.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry3.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry4.pk).exists())

    def test_dry_run_with_all(self):
        call_command("prune_audit_log_entries", all=True, dry_run=True)

        # Assert that no entries were actually deleted
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry1.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry2.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry3.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry4.pk).exists())

    def test_dry_run_with_days_and_is_sent(self):
        call_command("prune_audit_log_entries", days=3, is_sent=True, dry_run=True)

        # Assert that no entries were actually deleted
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry1.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry2.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry3.pk).exists())
        self.assertTrue(AuditLogEntry.objects.filter(pk=self.entry4.pk).exists())
