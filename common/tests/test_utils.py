from datetime import datetime

import pytest

from common.utils import get_origin_from_url


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
