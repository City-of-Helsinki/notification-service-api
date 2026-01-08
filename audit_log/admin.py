import logging

from audit_log.enums import Operation
from audit_log.services import audit_log_service, create_api_commit_message_from_request

logger = logging.getLogger(__name__)


class AuditLogModelAdminMixin:
    def get_changelist_instance(self, request):
        """
        Override get_changelist_instance of the Django ModelAdmin
        to get all the objects of the paginator page and write
        audit log READ operations for them.
        """
        from django.contrib.admin.views.main import PAGE_VAR

        changelist = super().get_changelist_instance(request)
        paginator = changelist.paginator
        page_number = request.GET.get(PAGE_VAR, 1)
        page = paginator.get_page(page_number)
        current_page_queryset = page.object_list
        current_page_queryset.with_audit_log_and_request(
            request=request,
            operation=Operation.READ.value,
            # Writing object states of all the objects of 1 page is too intensive.
            force_disable_object_states=True,
        )
        return changelist

    def get_object(self, request, object_id, from_field=None):
        """
        Given an object id, read it from the database.
        Write audit log of the action.
        """
        obj = super().get_object(request, object_id, from_field=from_field)
        if obj is not None:
            message = create_api_commit_message_from_request(
                request=request,
                operation=Operation.READ.value,
                object_ids=[str(obj.pk)],
                _type=obj._meta.model_name,
                old_objects=[obj],
            )
            audit_log_service._commit_to_audit_log(message=message)
        return obj

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        Write audit log of the action.
        """
        # TODO: add a change log to the audit log message
        message = create_api_commit_message_from_request(
            request=request,
            operation=Operation.UPDATE.value if change else Operation.CREATE.value,
            object_ids=[str(obj.pk)],
            _type=obj._meta.model_name,
            new_objects=[obj],
        )
        super().save_model(request, obj, form, change)
        audit_log_service._commit_to_audit_log(message=message)

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        Write audit log of the action.
        """
        message = create_api_commit_message_from_request(
            request=request,
            operation=Operation.DELETE.value,
            object_ids=[str(obj.pk)],
            _type=obj._meta.model_name,
            old_objects=[obj],
        )
        super().delete_model(request, obj)
        audit_log_service._commit_to_audit_log(message=message)

    def delete_queryset(self, request, queryset):
        """
        Given a queryset, delete it from the database.
        Write audit log of the action.
        """
        super().delete_queryset(
            request,
            queryset.with_audit_log_and_request(
                request=request, operation=Operation.DELETE.value
            ),
        )
