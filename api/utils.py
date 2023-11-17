from django.urls import reverse

from api.const import NOTIFICATION_TYPE_MOBILE
from notification_service.settings import DEBUG, QURIIRI_REPORT_URL


def format_destinations(recipients):
    return [
        r["destination"]
        for r in recipients
        if r["format"].lower() == NOTIFICATION_TYPE_MOBILE
    ]


def get_default_options(request, **kwargs):
    options = {}
    relative_drurl = reverse("delivery_log_webhook", kwargs={"id": kwargs.get("id")})
    if DEBUG:
        # Dev setting to receive delivery log
        options["drurl"] = f"{QURIIRI_REPORT_URL}{relative_drurl}"
    else:
        options["drurl"] = request.build_absolute_uri(relative_drurl)
    return options
