import pytest

from api.factories import DeliveryLogFactory
from api.models import DeliveryLog


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


def test_delivery_log_models():
    DeliveryLogFactory()
    assert DeliveryLog.objects.count() == 1
