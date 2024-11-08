from rest_framework.generics import GenericAPIView

from audit_log.services import audit_log_service


class AuditLogApiView(GenericAPIView):
    def get_object(self, skip_log_ids=False):
        # Generic
        instance = super().get_object()

        if not skip_log_ids:
            audit_log_service.add_audit_logged_object_ids(self.request, instance)

        return instance

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)

        logged_objects = page if page is not None else queryset
        audit_log_service.add_audit_logged_object_ids(self.request, logged_objects)

        return page

    def perform_create(self, serializer):
        super().perform_create(serializer)

        audit_log_service.add_audit_logged_object_ids(self.request, serializer.instance)

    def perform_update(self, serializer):
        super().perform_update(serializer)

        audit_log_service.add_audit_logged_object_ids(self.request, serializer.instance)

    def perform_destroy(self, instance):
        audit_log_service.add_audit_logged_object_ids(self.request, instance)

        super().perform_destroy(instance)
