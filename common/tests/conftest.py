import factory.random
import pytest
from copy import deepcopy
from django.contrib.auth.models import AnonymousUser
from freezegun import freeze_time
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

import quriiri
from api.factories import DeliveryLogFactory
from common.tests.mock_data import QURIIRI_SMS_RESPONSE
from users.factories import UserFactory


@pytest.fixture(autouse=True)
def setup_test_environment():
    factory.random.reseed_random("777")
    with freeze_time("2020-01-04"):
        yield


@pytest.fixture
def anonymous_api_client():
    return _create_api_client_with_user(AnonymousUser())


@pytest.fixture
def token_api_client():
    return _create_api_client_with_user(UserFactory())


@pytest.fixture
def delivery_log():
    return DeliveryLogFactory()


@pytest.fixture
def mock_send_sms(monkeypatch):
    def mock_send_sms(*args, **kwargs):
        return deepcopy(QURIIRI_SMS_RESPONSE)

    monkeypatch.setattr(
        quriiri.send.Sender,
        "send_sms",
        mock_send_sms,
    )


def _create_api_client_with_user(user=None):
    client = APIClient()
    if user and user.is_authenticated:
        token, _ = Token.objects.get_or_create(user=user)
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return client
