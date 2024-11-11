import pytest

from api.factories import DeliveryLogFactory
from audit_log.enums import Operation
from audit_log.models import AuditLogEntry


@pytest.mark.django_db
def test_audit_log_for_deliver_log_reading():
    assert AuditLogEntry.objects.count() == 0
    DeliveryLogFactory()
    assert AuditLogEntry.objects.count() == 2
    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__operation=Operation.CREATE.value
        ).count()
        == 1
    )
    assert (
        AuditLogEntry.objects.filter(
            message__audit_event__operation=Operation.READ.value
        ).count()
        == 1
    )
