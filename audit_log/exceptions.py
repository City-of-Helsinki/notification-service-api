class AuditLoggingDisabledError(Exception):
    """Raised when audit logging is disabled and an attempt is made to log an event."""
