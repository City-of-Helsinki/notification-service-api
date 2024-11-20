# Audit Log Service

This module provides a comprehensive audit logging service for Django applications. It allows you to track user actions, data changes, and system events, providing valuable insights into application activity and ensuring accountability.

## Table of Contents
<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [Features](#features)
- [Core Components](#core-components)
   * [Audit Log Model](#audit-log-model)
   * [Audit Log Message Format](#audit-log-message-format)
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

- **`LargeTablePaginator`:**

  - A custom paginator optimized for large tables in Django admin.
  - Uses PostgreSQL's `reltuples` to estimate queryset size for improved performance.
  - Falls back to the default `Paginator` if `reltuples` is unavailable or unreliable.

- **`AuditLogEntryAdmin`:**
  - A Django admin class for managing `AuditLogEntry` objects.
  - Provides a read-only interface for viewing audit log entries.
  - Uses `LargeTablePaginator` for efficient pagination of potentially large datasets.
  - Disables creation, modification, and deletion of audit logs through the admin interface.
  - Displays the audit log message in a user-friendly format.

### Audit Log Model

> A reference to structure requirements is here https://github.com/City-of-Helsinki/structured-log-transfer.

The `AuditLogEntry` [model](./models.py) stores audit log entries in the database. Each entry represents a single audit event and contains the following fields:

- `is_sent`: Indicates whether the audit log entry has been sent to an external system or processed in any way.
- `message`: Stores the audit log message in a JSON format (see the ["Audit Log Message Format"](#audit-log-message-format) section for details). This field contains the core information about the audit event, including the actor, action, target, and timestamp.
- `created_at`: Records the timestamp when the audit log entry was created.

This model provides a structured way to store and retrieve audit log data, allowing for efficient querying and analysis.

### Audit Log Message Format

Audit log messages are stored in a JSON format with the following structure:

```json
{
  "audit_event": {
    "actor": {
      "ip_address": "127.0.0.1",
      "role": "ADMIN",
      "uuid": "7a52666c-9b5b-11ef-91f6-e2cd5b1fb5ac"
    },
    "date_time": "2024-11-13T14:13:57.853Z",
    "date_time_epoch": 1731507237853,
    "operation": "READ",
    "origin": "notification_service",
    "status": "SUCCESS",
    "target": {
      "object_ids": [
        "bd6a5d06-8828-47a7-bb5b-fdf4559da56e",
        "9fb9cfa1-23f4-4401-b66a-8cc9a3277175",
        "ee444103-f145-4282-8768-28cdee52c3a4",
        "f928162d-6d27-4fab-a084-fd83a3dd1c5a",
        "c1bf4a0d-0ae3-4191-8948-94bec1742b41",
        "33935ff8-e8db-43e6-8939-15974dfd6d74",
        "e77c9e36-1f24-49dd-a700-2191caf594a4",
        "77e74bab-91ca-48b3-8245-cfd08196af80"
      ],
      "path": "/admin/api/deliverylog/"
    }
  }
}
```

Fields:

- `audit_event`: Contains the details of the audit event.
  - `actor`: Information about the user who performed the action.
    - `ip_address`: The IP address of the actor.
    - `role`: The role of the actor (e.g., "ADMIN", "USER").
    - `uuid`: The unique identifier of the actor. UUID is provided by the `django-helusers`.
    - `user_id`: The unique database primary key identifier of the actor.
  - `date_time`: The date and time of the event in ISO 8601 format.
  - `date_time_epoch`: The date and time of the event in Unix epoch milliseconds.
  - `operation`: The type of operation performed (e.g., "READ", "CREATE", "UPDATE", "DELETE").
  - `origin`: The origin of the event (e.g., "notification_service").
  - `status`: The status of the operation (e.g., "SUCCESS", "FAILURE").
  - `target`: Information about the object(s) affected by the operation.
    - `object_ids`: A list of unique identifiers of the affected objects.
    - `path`: The request path associated with the operation.
    - `type`: Type of the traced object, e.g. a model name.

This standardized format ensures consistency and facilitates analysis of audit log data.

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
