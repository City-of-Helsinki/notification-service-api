import logging

from django.conf import settings

from common.utils import get_origin_from_url

logger = logging.getLogger(__name__)


def _is_auth_service_included_in_allowed_origins():
    """
    Check if the auth service URL is included in the CORS allowed origins.

    This function retrieves the auth service URL from
    the `OIDC_API_TOKEN_AUTH["ISSUER"]`setting and the CORS allowed origins from the
    `CORS_ALLOWED_ORIGINS` setting. It then checks if the auth service URL is present
    in the list of allowed origins.

    If either of the settings is not configured correctly or if the auth service URL is
    not found in the allowed origins, a warning message is logged.

    Returns:
        None
    """
    try:
        auth_service_url = get_origin_from_url(settings.OIDC_API_TOKEN_AUTH["ISSUER"])
        cors_whitelist = settings.CORS_ALLOWED_ORIGINS
    except (ValueError, AttributeError, KeyError):
        logger.warning(
            "Please ensure 'OIDC_API_TOKEN_AUTH[\"ISSUER\"]' "
            "and 'CORS_ALLOWED_ORIGINS' are configured correctly."
        )
        return

    if auth_service_url not in cors_whitelist:
        logger.warning(
            f"Auth service URL ({auth_service_url}) "
            "is not included in CORS_ALLOWED_ORIGINS. "
            "This might cause issues with requests from auth service."
        )


def check_cors_setting():
    """Checks if the authorization service is in CORS_ALLOWED_ORIGINS.

    Logs a warning if the setting is not configured correctly.
    """
    if getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False):
        return
    _is_auth_service_included_in_allowed_origins()
