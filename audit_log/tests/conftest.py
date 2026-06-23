import pytest
from django.contrib.auth import get_user_model
from resilient_logger.utils import get_resilient_logger_config


@pytest.fixture(autouse=True)
def setup_audit_logging(settings):
    settings.AUDIT_LOG = {"ENABLED": True}
    settings.RESILIENT_LOGGER = {
        **settings.RESILIENT_LOGGER,
        "environment": "test",
    }
    get_resilient_logger_config.cache_clear()
    yield
    get_resilient_logger_config.cache_clear()


@pytest.fixture
def superuser():
    User = get_user_model()  # noqa: N806
    return User.objects.create_superuser("admin", "admin@example.com", "admin")
