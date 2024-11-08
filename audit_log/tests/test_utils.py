from unittest.mock import Mock

import pytest
from rest_framework import status

from audit_log.enums import Status
from audit_log.utils import (
    get_remote_address,
    get_response_status,
)


@pytest.mark.parametrize(
    "remote_address,expected,x_forwarded_for",
    [
        ("1.2.3.4:443", "1.2.3.4", True),
        ("1.2.3.4", "1.2.3.4", True),
        (
            "[2001:0db8:85a3:0000:0000:8a2e:0370:7334]:443",
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            True,
        ),
        (
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            True,
        ),
        ("1.2.3.4", "1.2.3.4", False),
        (
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            False,
        ),
    ],
)
def test_get_remote_address(remote_address, expected, x_forwarded_for):
    req_mock = Mock(
        headers={"x-forwarded-for": remote_address} if x_forwarded_for else {},
        META={"REMOTE_ADDR": remote_address} if not x_forwarded_for else {},
    )
    assert get_remote_address(req_mock) == expected


@pytest.mark.parametrize(
    "status_code,audit_status",
    [
        (status.HTTP_200_OK, Status.SUCCESS.value),
        (status.HTTP_201_CREATED, Status.SUCCESS.value),
        (status.HTTP_204_NO_CONTENT, Status.SUCCESS.value),
        (status.HTTP_401_UNAUTHORIZED, Status.FORBIDDEN.value),
        (status.HTTP_403_FORBIDDEN, Status.FORBIDDEN.value),
        (status.HTTP_302_FOUND, None),
        (status.HTTP_404_NOT_FOUND, None),
        (status.HTTP_502_BAD_GATEWAY, None),
    ],
)
def test_get_response_status(status_code, audit_status):
    res_mock = Mock(status_code=status_code)

    assert get_response_status(res_mock) == audit_status
