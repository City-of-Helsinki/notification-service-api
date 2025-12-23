# Audit Log Service

This module provides a comprehensive audit logging service for Django applications. It allows you to track user actions, data changes, and system events, providing valuable insights into application activity and ensuring accountability.
It uses https://github.com/City-of-Helsinki/django-resilient-logger/ for storing, sending and cleaning audit logs.

## Table of Contents

<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [Features](#features)
- [Core Components](#core-components)
  - [Audit Log Model](#audit-log-model)
  - [Audit Log Message Format](#audit-log-message-format)
- [Django Audit Log Settings](#django-audit-log-settings)
- [Usage](#usage)
- [Management Command](#management-command)

<!-- TOC end -->

## Features

| Feature               | Description                                                                                                                                                                         |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Flexible Logging      | Logs audit events to a dedicated logger, a database, or both, allowing you to choose the storage that best suits your needs.                                                        |
| Request-Aware         | Automatically extracts relevant information from Django requests, such as user details, IP addresses, and request paths, to provide context for audit events.                       |
| Configurable          | Offers flexible configuration options to customize logged endpoints, request variables, and logging destinations, allowing you to tailor the service to your specific requirements. |
| Extensible            | Provides a base class for creating custom audit log services, enabling you to extend the functionality and integrate with other systems.                                            |
| Admin Integration     | Seamlessly integrates with Django admin, automatically logging actions performed through the admin interface, simplifying audit trail management.                                   |
| Optimized Performance | Includes a specialized paginator for handling large audit log tables, ensuring efficient querying and retrieval of audit data, even with high volumes of events.                    |

## Core Components

- **`AuditLogServiceBase`:**

  - A base class for audit log services, providing common functionality for creating and committing audit log messages.
  - Decouples audit logging logic from Django's request/response cycle.
  - Defines methods for determining operation names, extracting actor data, defining targets, and committing messages to loggers and/or the database.

- **`AuditLogApiService`:**

  - Extends `AuditLogServiceBase` to handle Django-specific requests.
  - Extracts information from Django request objects (e.g., object IDs, operation names, actor data).
  - Determines if a request endpoint should be audit logged based on configured rules.
  - Manages the lifecycle of audit log messages within a request (creation, deletion, and committing).
  - Provides utilities for adding and removing audit logged object IDs from requests.

- **`AuditLogModelAdminMixin`:**

  - A mixin for Django's `ModelAdmin` class to enable audit logging for model admin views.
  - Automatically logs read, create, update, and delete operations performed through the admin interface.
  - Integrates with `AuditLogApiService` to commit audit log messages.

## Django Audit Log Settings

This module provides a way to configure settings for the Django Audit Log application. It allows you to customize various aspects of the audit logging functionality. The settings are accessed through the `audit_logging_settings` object. This object provides access to the following settings:

- **`ENABLED`:** A boolean indicating whether audit logging is enabled. Defaults to `True`.
- **`LOGGED_ENDPOINTS_RE`:** A compiled regular expression that matches API endpoints to be logged. Defaults to `re.compile(r"^/(v1|gdpr-api)/")`.
- **`REQUEST_AUDIT_LOG_VAR`:** A string representing the name of the request variable used to store logged object IDs. Defaults to `"_audit_logged_object_ids"`.
- **`STORE_OBJECT_STATE`:** An enum value from `audit_log.enums.StoreObjectState` that specifies how object state should be stored. Defaults to `StoreObjectState.NONE`. Other options are `"none", "old-only", "new-only", "old-and-new", "diff", "all"`.

```python
class StoreObjectState(Enum):
    # Do not store object state
    NONE = "none"
    # Store only the old object state
    OLD_ONLY = "old-only"
    # Store only the new object state
    NEW_ONLY = "new-only"
    # Store the old and the new object states
    OLD_AND_NEW_BOTH = "old-and-new"
    # Store only diff
    DIFF = "diff"
    # Store the old and the new object states and also the diff
    ALL = "all"
```

You can override the default settings by defining an `AUDIT_LOG` dictionary in your Django settings module. For example:

```python
AUDIT_LOG = {
    "ENABLED": True,
    "LOGGED_ENDPOINTS_RE": re.compile(r"^/api/"),
    "STORE_OBJECT_STATE": StoreObjectState.ALL,
}
```

## Usage

This module provides an instance of `AuditLogApiService` as `audit_log_service`. This instance can be used to interact with the audit logging functionality.

**Service Usage Example:**

```python
from audit_log.services import audit_log_service

# Add object IDs to be logged
audit_log_service.add_audit_logged_object_ids(request, instance)

# ... later in the request/response cycle ...

# Commit the audit log entry
audit_log_service.commit_to_audit_log(request, response)
```

**Admin View Example (using `AuditLogModelAdminMixin`):**

```python
from audit_log.admin import AuditLogModelAdminMixin
from django.contrib import admin

class DeliveryLogAdmin(AuditLogModelAdminMixin, admin.ModelAdmin):
    search_fields = ["report", "user__email"]
    list_display = ["id", "user", "get_number", "get_status", "created_at"]
    list_filter = [MessageStatusListFilter, "created_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
```

In this example, DeliveryLogAdmin inherits from AuditLogModelAdminMixin to automatically enable audit logging for all operations performed on DeliveryLog objects through the Django admin interface.

**Queryset Logging Example:**

By using a `AudtLogQuerySet` and `AuditLogManager`, the Django Queryset and the objects in it's result set, can also be easily audit logged with some shortcut methods: `with_audit_log` and `with_audit_log_and_request`, which are introduced in the [managers.py](./managers.py).

```python
    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        super().delete_queryset(
            request,
            queryset.with_audit_log_and_request(
                request=request, operation=Operation.DELETE.value
            ),
        )
```

In this example, the request object is available, so queryset can be called with `with_audit_log_and_request`. Like that all the model object instances of the original queryset will be included in the audit log message.

```python
    def with_audit_log_and_request(
        self,
        request: HttpRequest,
        operation: Operation,
        status: Union[Status, str] = Status.SUCCESS.value,
    ):
        return self.with_audit_log(
            user=request.user,
            operation=operation,
            status=status,
            ip_address=get_remote_address(request),
            path=request.path,
        )
```

In this example, we are in a context where there is no request object available. The queryset result can still be audit logged in to database with `with_audit_log`.

## Management Command

This module includes a management command for pruning (deleting) old AuditLogEntry objects from the database.

`prune_audit_logs`: This command allows you to delete audit log entries based on their age or delete all entries.

Usage:

```shell
python manage.py prune_audit_logs --days <number_of_days>
python manage.py prune_audit_logs --all
```

- `--days`: Specifies the age in days of entries to be deleted.
- `--all`: Deletes all audit log entries.

This command is useful for managing the size of the audit log table and removing old entries that are no longer needed.
