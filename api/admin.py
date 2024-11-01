from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from api.models import DeliveryLog


class DeliveryLogAdmin(admin.ModelAdmin):
    search_fields = ["report"]
    list_display = ["id", "user", "get_number", "get_status"]

    def get_number(self, obj):
        try:
            return ", ".join([number for number in obj.report["messages"]])
        except (TypeError, KeyError):
            return ""

    get_number.short_description = _("numbers")

    def get_status(self, obj):
        try:
            return ", ".join(
                [
                    obj.report["messages"][number]["status"]
                    for number in obj.report["messages"]
                ]
            )
        except (TypeError, KeyError):
            return ""

    get_status.short_description = _("status")


admin.site.register(DeliveryLog, DeliveryLogAdmin)
