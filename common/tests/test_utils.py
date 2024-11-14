from datetime import datetime, timezone

import pytest

from common.utils import get_origin_from_url, utc_datetime


@pytest.mark.parametrize(
    "url,expected_origin",
    [
        ("https://hel.fi", "https://hel.fi"),
        ("https://hel.fi/", "https://hel.fi"),
        ("https://hel.fi/path/to/somewhere", "https://hel.fi"),
        ("http://hel.fi/http-is-insecure", "http://hel.fi"),
        ("https://hel.fi:80/default-port", "https://hel.fi:80"),
        ("https://hel.fi:8081/with-non-default-port", "https://hel.fi:8081"),
        (
            "https://www.example.com/path/to/page?query=string",
            "https://www.example.com",
        ),
        ("http://localhost:8080/api/data", "http://localhost:8080"),
    ],
)
def test_get_origin_from_url(url, expected_origin):
    assert get_origin_from_url(url) == expected_origin


@pytest.mark.parametrize(
    "url", ["//missing.protocol:0.0.0.1", "not-an-url", "http://", 1, datetime.now()]
)
def test_get_origin_from_url_with_invalid_url(url):
    with pytest.raises(ValueError):
        get_origin_from_url(url)


@pytest.mark.parametrize(
    "args",
    [
        (2021, 10, 22),
        (2022, 2, 8),
        (2021, 10, 22, 12, 30, 10),
        (2022, 2, 8, 19, 55, 59),
        (2021, 10, 22, 12, 30, 10, 9999),
        (2022, 2, 8, 19, 55, 59, 9999),
    ],
)
def test_utc_datetime(args: tuple[int, ...]):
    result = utc_datetime(*args)
    assert result == datetime(*args, tzinfo=timezone.utc)
    assert result.tzinfo == timezone.utc
