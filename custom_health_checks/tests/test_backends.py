from unittest.mock import patch

import pytest
from django.db import OperationalError
from health_check.exceptions import ServiceUnavailable

from custom_health_checks.backends import DatabaseHealthCheck


@patch("django.db.connection.cursor")
def test_database_check_status_success(mock_cursor):
    """
    Test that run passes when the database connection is successful.
    """
    mock_cursor.return_value.__enter__.return_value.execute.return_value = True
    health_check = DatabaseHealthCheck()
    health_check.run()  # Should not raise an exception


@patch("django.db.connection.cursor")
def test_database_check_status_failure(mock_cursor):
    """
    Test that run raises ServiceUnavailable when the database connection fails.
    """
    mock_cursor.return_value.__enter__.return_value.execute.side_effect = (
        OperationalError("Database error")
    )
    health_check = DatabaseHealthCheck()
    with pytest.raises(ServiceUnavailable) as exc_info:
        health_check.run()
    assert "Database connection failed" in str(exc_info.value)


def test_database_check_status_with_real_database(db):  # Use the 'db' fixture
    """
    Test run with the actual database connection.
    This assumes your test database is set up correctly.
    """
    try:
        health_check = DatabaseHealthCheck()
        health_check.run()  # Should not raise an exception
    except ServiceUnavailable as e:
        pytest.fail(f"Database health check failed: {e}")
