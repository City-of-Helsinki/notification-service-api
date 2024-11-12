import pytest

from api.factories import DeliveryLogFactory
from api.models import DeliveryLog
from audit_log.enums import Operation, Status
from audit_log.models import AuditLogEntry


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


def test_delivery_log_models():
    DeliveryLogFactory()
    assert DeliveryLog.objects.count() == 1


def test_delivery_log_manager_with_audit_log():
    assert AuditLogEntry.objects.count() == 0
    delivery_log = DeliveryLogFactory()
    user = delivery_log.user
    assert (
        DeliveryLog.objects.all()
        .with_audit_log(user=user, operation=Operation.READ.value)
        .count()
        == 1
    )
    assert AuditLogEntry.objects.count() == 1
    audit_log = AuditLogEntry.objects.first()
    assert audit_log.message["audit_event"]["origin"] == "notification_service"
    assert audit_log.message["audit_event"]["operation"] == Operation.READ.value
    assert audit_log.message["audit_event"]["status"] == Status.SUCCESS.value
    assert audit_log.message["audit_event"]["target"]["path"] == DeliveryLog.__name__
    assert audit_log.message["audit_event"]["target"]["object_ids"] == [
        str(delivery_log.pk)
    ]
