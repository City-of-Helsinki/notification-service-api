import asyncio

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from health_check.views import HealthCheckView


class HealthCheckJSONView(HealthCheckView):
    """
    Always returns a JSON response, regardless of the Accept header.

    To apply it, in project's `urls.py`, add the custom JSON view in use like this:
    >>> # doctest: +SKIP
    ... import views
    ...
    ... urlpatterns = [
    ...     # ...
    ...     path(
    ...         r"healthz",
    ...         views.HealthCheckJSONView.as_view(),
    ...         name="health_check_custom",
    ...     ),
    ... ]
    """

    checks = ("custom_health_checks.backends.DatabaseHealthCheck",)

    @method_decorator(never_cache)
    async def get(self, request, *args, **kwargs):
        with self.get_executor() as executor:
            self.results = await asyncio.gather(
                *(check.get_result(executor) for check in self.get_checks())
            )
        has_errors = any(result.error for result in self.results)
        status_code = 500 if has_errors else 200
        return self.render_to_response_json(status_code)
