import re

from django.conf import settings
from django.core.signals import setting_changed
from django.dispatch import receiver

from audit_log.enums import StoreObjectState

_defaults = dict(
    ENABLED=True,
    ORIGIN="service",
    LOGGED_ENDPOINTS_RE=re.compile(r"^/(v1|gdpr-api)/"),
    REQUEST_AUDIT_LOG_VAR="_audit_logged_object_ids",
    LOG_TO_DB_ENABLED=True,
    LOG_TO_LOGGER_ENABLED=False,
    STORE_OBJECT_STATE=StoreObjectState.NONE,
)

_import_strings = []


def _compile_settings():
    """
    Compile audit log settings.

    This function creates a settings object that inherits from the default settings
    and overrides them with any user-defined settings.

    Returns:
        Settings: An object containing the compiled audit log settings.
    """

    class Settings:
        """
        A class to hold audit log settings.

        This class dynamically loads settings from the Django settings module
        and provides access to them through attributes.
        """

        def __init__(self):
            """
            Initialize the settings object.

            Loads the default settings and any user-defined settings.
            """
            self._load()

        def __getattr__(self, name):
            """
            Get an attribute from the settings.

            If the attribute is a string and is listed in `_import_strings`,
            it will be imported as a module.

            Args:
                name (str): The name of the attribute.

            Returns:
                Any: The value of the attribute.

            Raises:
                AttributeError: If the attribute is not found.
            """
            from django.utils.module_loading import import_string

            try:
                attr = self._settings[name]

                if name in _import_strings and isinstance(attr, str):
                    attr = import_string(attr)
                    self._settings[name] = attr

                return attr
            except KeyError:
                raise AttributeError("Setting '{}' not found".format(name))

        def _load(self):
            """
            Load the settings.

            Loads the default settings and overrides them with any user-defined settings
            from the Django settings module.
            """
            self._settings = _defaults.copy()

            user_settings = getattr(settings, "AUDIT_LOG", None)
            self._settings.update(user_settings)

    return Settings()


audit_logging_settings = _compile_settings()


@receiver(setting_changed)
def _reload_settings(setting, **kwargs):
    """
    Reload the audit log settings when the Django settings are changed.

    This function is called when the `setting_changed` signal is sent.
    It checks if the changed setting is `AUDIT_LOG` and reloads the settings if it is.

    Args:
        setting (str): The name of the setting that was changed.
        **kwargs: Additional keyword arguments.
    """
    if setting == "AUDIT_LOG":
        audit_logging_settings._load()
