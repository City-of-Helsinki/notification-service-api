from unittest.mock import patch

from django.test import Client
from django.urls import reverse
from health_check.exceptions import ServiceUnavailable


@patch("custom_health_checks.backends.DatabaseHealthCheck.run")
def test_healthz_success(mock_run, client: Client):  # Use the 'client' fixture
    """
    Test /healthz endpoint with successful health checks.
    """
    mock_run.return_value = None  # Simulate successful check
    url = reverse("healthz")
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {"DatabaseHealthCheck()": "OK"}


@patch("custom_health_checks.backends.DatabaseHealthCheck.run")
def test_healthz_database_error(mock_run, client: Client):
    """
    Test /healthz endpoint with a database error.
    """
    mock_run.side_effect = ServiceUnavailable("Database connection failed")
    url = reverse("healthz")
    response = client.get(url)
    assert response.status_code == 500
    assert b"Database connection failed" in response.content
