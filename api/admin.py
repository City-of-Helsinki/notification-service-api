from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from api.models import DeliveryLog


class MessageStatusListFilter(admin.SimpleListFilter):
    DELIVERED = "delivered"
    FAILED = "failed"
    UNKNOWN = "unknown"
    CREATED = "created"

    MESSAGE_STATUS_OPTIONS = [DELIVERED, FAILED, UNKNOWN, CREATED]

    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("message status")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return map(lambda o: (o, o.upper()), self.MESSAGE_STATUS_OPTIONS)

    def queryset(self, request, queryset):
        if self.value() in self.MESSAGE_STATUS_OPTIONS:
            return queryset.filter(report__icontains=self.value())
        return queryset


class DeliveryLogAdmin(admin.ModelAdmin):
    search_fields = ["report", "user__email"]
    list_display = ["id", "user", "get_number", "get_status", "created_at"]
    list_filter = [MessageStatusListFilter, "created_at"]
    date_hierarchy = "created_at"

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
