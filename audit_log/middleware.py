from audit_log.services import audit_log_service


class AuditLogMiddleware:
    """
    Middleware to handle audit logging.

    This middleware checks if audit logging is enabled and if the current request
    should be logged. If so, it commits the audit log entry after the response is
    generated.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if self._should_commit_to_audit_log(request, response):
            audit_log_service.commit_to_audit_log(request, response)

        return response

    @staticmethod
    def _should_commit_to_audit_log(request, response):
        return (
            audit_log_service.is_audit_logging_enabled()
            and audit_log_service.is_audit_logging_endpoint(request)
            and audit_log_service.get_response_status(response)
        )
