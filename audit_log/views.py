from rest_framework.generics import GenericAPIView

from audit_log.services import audit_log_service


class AuditLogApiView(GenericAPIView):
    """
    A base API view class that automatically logs object IDs for audit purposes.

    This class extends Django REST Framework's `GenericAPIView` and adds functionality
    to log the IDs of objects accessed, created, updated, or deleted through the API.

    It integrates with an `audit_log_service` to handle the actual logging process.

    Attributes:
        None

    Methods:
        get_object(self, skip_log_ids=False):
            Retrieves the object for the request, optionally skipping the audit logging.

        paginate_queryset(self, queryset):
            Paginates the queryset and logs the IDs of the objects in the page or
            the entire queryset.

        perform_create(self, serializer):
            Creates an object instance and logs its ID.

        perform_update(self, serializer):
            Updates an object instance and logs its ID.

        perform_destroy(self, instance):
            Logs the object ID and then deletes the object instance.
    """

    def get_object(self, skip_log_ids=False):
        """
        Retrieves the object for the request.

        Args:
            skip_log_ids (bool, optional): Whether to skip logging the object ID.
            Defaults to False.

        Returns:
            The object instance.
        """
        instance = super().get_object()

        if not skip_log_ids:
            audit_log_service.add_audit_logged_object_ids(self.request, instance)

        return instance

    def paginate_queryset(self, queryset):
        """
        Paginates the queryset and logs object IDs.

        Args:
            queryset: The queryset to paginate.

        Returns:
            The paginated queryset or None if no pagination is applied.
        """
        page = super().paginate_queryset(queryset)

        logged_objects = page if page is not None else queryset
        audit_log_service.add_audit_logged_object_ids(self.request, logged_objects)

        return page

    def perform_create(self, serializer):
        """
        Creates an object instance and logs its ID.

        Args:
            serializer: The serializer instance.
        """
        super().perform_create(serializer)

        audit_log_service.add_audit_logged_object_ids(self.request, serializer.instance)

    def perform_update(self, serializer):
        """
        Updates an object instance and logs its ID.

        Args:
            serializer: The serializer instance.
        """
        super().perform_update(serializer)

        audit_log_service.add_audit_logged_object_ids(self.request, serializer.instance)

    def perform_destroy(self, instance):
        """
        Logs the object ID and then deletes the object instance.

        Args:
            instance: The object instance to delete.
        """
        audit_log_service.add_audit_logged_object_ids(self.request, instance)

        super().perform_destroy(instance)
