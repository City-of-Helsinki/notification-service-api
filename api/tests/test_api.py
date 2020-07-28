import uuid

import pytest
from api.factories import DeliveryLogFactory
from api.models import DeliveryLog
from common.tests.mock_data import QURIIRI_SMS_RESPONSE
from django.urls import reverse
from rest_framework.authtoken.models import Token


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


SMS_PAYLOAD = {
    "sender": "Hel.fi",
    "to": [{"destination": "+358461231231", "format": "MOBILE"}],
    "text": "SMS message",
}

SMS_WEBHOOK_DATA = {
    "sender": "hel.fi",
    "destination": "+358461231231",
    "status": "DELIVERED",
    "statustime": "2020-07-21T09:18:00Z",
    "smscount": "1",
    "billingref": "Palvelutarjotin",
}


def test_send_sms_unauthentication(anonymous_api_client):
    response = anonymous_api_client.post(
        reverse("send_message"), SMS_PAYLOAD, format="json"
    )
    assert response.status_code == 401


def test_send_sms(token_api_client, snapshot, mock_send_sms):
    response = token_api_client.post(
        reverse("send_message"), SMS_PAYLOAD, format="json"
    )
    assert DeliveryLog.objects.count() == 1
    snapshot.assert_match(response.data["report"])


def test_webhook_delivery_log(
    token_api_client, anonymous_api_client, snapshot, mock_send_sms
):
    response = anonymous_api_client.post(
        reverse("delivery_log_webhook", kwargs={"id": uuid.uuid4()})
    )
    assert response.status_code == 404

    # Send a message to initiate delivery log
    token_api_client.post(reverse("send_message"), SMS_PAYLOAD, format="json")

    assert DeliveryLog.objects.count() == 1
    log = DeliveryLog.objects.first()
    snapshot.assert_match(log.report)

    webhook_data = SMS_WEBHOOK_DATA

    anonymous_api_client.post(
        reverse("delivery_log_webhook", kwargs={"id": str(log.id)}),
        data=webhook_data,
        format="json",
    )
    log.refresh_from_db()
    snapshot.assert_match(log.report)


def test_get_delivery_log_unauthenticated_or_unauthorized(
    anonymous_api_client, token_api_client
):
    log = DeliveryLogFactory()
    response = anonymous_api_client.get(
        reverse("get_message", kwargs={"id": str(log.id)})
    )
    # Unauthenticated
    assert response.status_code == 401

    response = token_api_client.get(reverse("get_message", kwargs={"id": str(log.id)}))
    # Not found
    assert response.status_code == 404


def test_get_delivery_log(token_api_client, snapshot):
    log = DeliveryLogFactory(report=QURIIRI_SMS_RESPONSE)
    token, _ = Token.objects.get_or_create(user=log.user)
    token_api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    response = token_api_client.get(reverse("get_message", kwargs={"id": str(log.id)}))
    snapshot.assert_match(response.data["report"])
