import json
import logging

from django.contrib import admin
from django.core.paginator import Paginator
from django.db import connection
from django.utils.functional import cached_property
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from audit_log.enums import Operation, Role
from audit_log.models import AuditLogEntry
from audit_log.services import audit_log_service, create_api_commit_message_from_request

logger = logging.getLogger(__name__)


class AuditLogModelAdminMixin:
    def get_queryset(self, request):
        """Write audit logs of the queryset read."""
        return (
            super()
            .get_queryset(request)
            .with_audit_log_and_request(
                request=request,
                operation=Operation.READ.value,
            )
        )

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        # TODO: add a change log to the audit log message
        message = create_api_commit_message_from_request(
            request,
            Operation.UPDATE.value if change else Operation.CREATE.value,
            [str(obj.pk)],
        )
        audit_log_service._commit_to_audit_log(message=message)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        message = create_api_commit_message_from_request(
            request, Operation.DELETE.value, [str(obj.pk)]
        )
        audit_log_service._commit_to_audit_log(message=message)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        super().delete_queryset(
            request,
            queryset.with_audit_log_and_request(
                request=request, operation=Operation.DELETE.value
            ),
        )


class AuditLogMessageOperationListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("operation")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "operation"

    options = [operation.value for operation in Operation]

    def lookups(self, request, model_admin):
        return map(lambda o: (o, o.upper()), self.options)

    def queryset(self, request, queryset):
        if self.value() in self.options:
            return queryset.filter(message__icontains=self.value())
        return queryset


class AuditLogMessageRoleListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("role")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "role"

    options = [role.value for role in Role]

    def lookups(self, request, model_admin):
        return map(lambda o: (o, o.upper()), self.options)

    def queryset(self, request, queryset):
        if self.value() in self.options:
            return queryset.filter(message__icontains=self.value())
        return queryset


class LargeTablePaginator(Paginator):
    """
    Paginator that uses PostgreSQL `reltuples` for queryset size.

    The reltuples values is just an estimate, but it's much faster than
    the COUNT(*) which is used by the default paginator. Therefore, this
    should work better for tables containing millions of rows.

    See https://wiki.postgresql.org/wiki/Count_estimate for details.
    """

    @cached_property
    def count(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT reltuples::bigint FROM pg_class WHERE relname = %s",
                [self.object_list.query.model._meta.db_table],
            )
            estimate = cursor.fetchone()[0]
            if estimate == -1:
                # If the table has not yet been analyzed/vacuumed,
                # reltuples will return -1.  In this case we fall back to
                # the default paginator.
                logger.warning(
                    "Can't estimate count of table %s, using COUNT(*) instead",
                    self.object_list.query.model._meta.db_table,
                )
                return super().count
            return estimate


@admin.register(AuditLogEntry)
class AuditLogEntryAdmin(admin.ModelAdmin):
    exclude = ("message",)
    readonly_fields = ("id", "created_at", "is_sent", "message_prettified")
    list_display = (
        "id",
        "get_audit_event_actor_role",
        "get_audit_event_operation",
        "get_audit_event_target_path",
        "get_audit_event_target_objects_count",
        "get_audit_event_status",
        "created_at",
        "is_sent",
    )
    list_filter = (
        AuditLogMessageOperationListFilter,
        AuditLogMessageRoleListFilter,
        "created_at",
        "is_sent",
    )

    # For increasing listing performance
    show_full_result_count = False
    paginator = LargeTablePaginator

    ordering = ["-created_at"]

    def get_audit_event_actor_role(self, obj):
        try:
            return obj.message["audit_event"]["actor"]["role"]
        except (TypeError, KeyError):
            return ""

    get_audit_event_actor_role.short_description = _("role")

    def get_audit_event_operation(self, obj):
        try:
            return obj.message["audit_event"]["operation"]
        except (TypeError, KeyError):
            return ""

    get_audit_event_operation.short_description = _("operation")

    def get_audit_event_status(self, obj):
        try:
            return obj.message["audit_event"]["status"]
        except (TypeError, KeyError):
            return ""

    get_audit_event_status.short_description = _("status")

    def get_audit_event_target_path(self, obj):
        try:
            return obj.message["audit_event"]["target"]["path"]
        except (TypeError, KeyError):
            return ""

    get_audit_event_target_path.short_description = _("target path")

    def get_audit_event_target_objects_count(self, obj):
        try:
            return len(obj.message["audit_event"]["target"]["object_ids"])
        except (TypeError, KeyError):
            return ""

    get_audit_event_target_objects_count.short_description = _("targets")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="message")
    def message_prettified(self, instance):
        """Format the message to be a bit a more user-friendly."""
        message = json.dumps(instance.message, indent=2, sort_keys=True)
        content = f"<pre>{escape(message)}</pre>"
        return mark_safe(content)
