import pytest
from resilient_logger.utils import get_resilient_logger_config

from common.tests.conftest import *  # noqa


@pytest.fixture(autouse=True)
def setup_resilient_logger(settings):
    settings.RESILIENT_LOGGER = {
        **settings.RESILIENT_LOGGER,
        "environment": "test",
    }
    get_resilient_logger_config.cache_clear()
    yield
    get_resilient_logger_config.cache_clear()
