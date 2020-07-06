from notification_service import __version__
from notification_service.settings import REVISION


def get_api_version():
    return " | ".join((__version__, REVISION.decode("utf-8")))
