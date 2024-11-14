from datetime import datetime, timezone
from functools import partial
from urllib.parse import urlparse


def get_origin_from_url(url: str) -> str:
    """Get origin from absolute URL.

    The origin of a URL consists of the scheme (protocol)
    and the domain name (with optional port).
    This function extracts the origin from a given full URL.

    Args:
        url: The absolute URL, including scheme, domain, and optional path,
            query parameters, etc.

    Returns:
        The origin of the URL in the format "scheme://domain:port"
        (port is omitted if it's the default port).

    Raises:
        ValueError: If the provided URL is not a valid absolute URL
                    or if the URL is missing a scheme or network location.

    Example:
        >>> get_origin_from_url("https://www.example.com/path/to/page?query=string")
        'https://www.example.com'

        >>> get_origin_from_url("http://localhost:8080/api/data")
        'http://localhost:8080'
    """
    try:
        parsed_url = urlparse(url)
    except (ValueError, AttributeError) as e:
        raise ValueError("Invalid URL: The provided URL is not a valid URL.") from e

    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(
            "Invalid URL: The URL must include a scheme and network location."
        )

    return f"{parsed_url.scheme}://{parsed_url.netloc}"


# Create datetime with UTC timezone
utc_datetime = partial(datetime, tzinfo=timezone.utc)
