from audit_log.settings import audit_logging_settings


def test_defaults_exist_for_settings():
    assert audit_logging_settings.REQUEST_AUDIT_LOG_VAR == "_audit_logged_object_ids"
