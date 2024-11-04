import logging
from unittest.mock import patch

import pytest
import sentry_sdk
from django.test import Client

from notification_service.cors_utils import check_cors_setting


@pytest.mark.django_db
def test_cors_allowed_origin(settings, live_server, client: Client):
    settings.CORS_ALLOWED_ORIGINS = [
        live_server.url,
    ]
    settings.CORS_ORIGIN_ALLOW_ALL = False
    response = client.get("/admin/login/", HTTP_ORIGIN=live_server.url)
    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == live_server.url


@pytest.mark.django_db
def test_cors_disallowed_origin(settings, live_server, client: Client):
    settings.CORS_ALLOWED_ORIGINS = [live_server.url]
    settings.CORS_ORIGIN_ALLOW_ALL = False
    response = client.get("/admin/login/", HTTP_ORIGIN="http://malicious.com")
    assert response.status_code == 200  # The request still succeeds...
    assert (
        "Access-Control-Allow-Origin" not in response
    )  # ...but CORS headers are not present


@pytest.fixture
def disable_sentry():
    sentry_sdk.init(dsn=None)
    yield


@pytest.fixture
def caplog(caplog):
    """Customize caplog fixture to only capture WARNING level logs."""
    caplog.clear()  # Clear any existing log records
    caplog.set_level(logging.WARNING)
    return caplog


@pytest.mark.parametrize(
    "cors_settings, auth_service_url, expected_warning",
    [
        # Warning cases
        (
            {"CORS_ALLOWED_ORIGINS": ["https://other.api.com"]},
            "https://tunnistus.hel.fi/auth/realms/helsinki-tunnistus",
            "Auth service URL (https://tunnistus.hel.fi) "
            "is not included in CORS_ALLOWED_ORIGINS.",
        ),
        (
            {"CORS_ALLOWED_ORIGINS": ["https://tunnistus.hel.fi"]},
            None,  # Missing OIDC_API_TOKEN_AUTH[\"ISSUER\"]
            "Please ensure 'OIDC_API_TOKEN_AUTH[\"ISSUER\"]' and 'CORS_ALLOWED_ORIGINS' are configured correctly.",  # noqa: E501
        ),
        (
            {"CORS_ALLOWED_ORIGINS": ["https://tunnistus.hel.fi"]},
            "invalid-url",  # Invalid OIDC_API_TOKEN_AUTH[\"ISSUER\"]
            "Please ensure 'OIDC_API_TOKEN_AUTH[\"ISSUER\"]' and 'CORS_ALLOWED_ORIGINS' are configured correctly.",  # noqa: E501
        ),
        # No warning cases
        (
            {"CORS_ALLOWED_ORIGINS": ["https://tunnistus.hel.fi"]},
            "https://tunnistus.hel.fi/auth/realms/helsinki-tunnistus",
            None,
        ),
        (
            {"CORS_ALLOW_ALL_ORIGINS": True},
            "https://tunnistus.hel.fi/auth/realms/helsinki-tunnistus",
            None,
        ),
    ],
)
def test_check_cors_setting(
    cors_settings, auth_service_url, expected_warning, caplog, settings, disable_sentry
):
    """Test the check_cors_setting function."""
    settings.CORS_ALLOW_ALL_ORIGINS = False
    settings.CORS_ALLOWED_ORIGINS = []
    with patch.multiple(settings, **cors_settings):
        if auth_service_url is None:
            del settings.OIDC_API_TOKEN_AUTH["ISSUER"]
        else:
            settings.OIDC_API_TOKEN_AUTH["ISSUER"] = auth_service_url
        check_cors_setting()

    if expected_warning:
        assert len(caplog.records) == 1
        assert expected_warning in caplog.text
    else:
        assert len(caplog.records) == 0
