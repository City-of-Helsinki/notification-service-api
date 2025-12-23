import pytest
from resilient_logger.models import ResilientLogEntry
from resilient_logger.sources import ResilientLogSource

from api.factories import DeliveryLogFactory
from api.models import DeliveryLog
from audit_log.enums import Operation, Status


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


def test_delivery_log_models():
    DeliveryLogFactory()
    assert DeliveryLog.objects.count() == 1


def test_delivery_log_manager_with_audit_log():
    assert ResilientLogEntry.objects.count() == 0
    delivery_log = DeliveryLogFactory()
    user = delivery_log.user
    assert (
        DeliveryLog.objects.all()
        .with_audit_log(user=user, operation=Operation.READ.value)
        .count()
        == 1
    )
    assert ResilientLogEntry.objects.count() == 1
    log_entry = ResilientLogEntry.objects.first()
    document = ResilientLogSource(log_entry).get_document()

    assert document["audit_event"]["origin"] == "notification-service-api"
    assert document["audit_event"]["operation"] == Operation.READ.value
    assert document["audit_event"]["extra"]["status"] == Status.SUCCESS.value
    assert document["audit_event"]["message"] == Status.SUCCESS.value
    assert document["audit_event"]["target"]["path"] == ""
    assert document["audit_event"]["target"]["type"] == DeliveryLog._meta.model_name
    assert document["audit_event"]["target"]["object_ids"] == [str(delivery_log.pk)]
