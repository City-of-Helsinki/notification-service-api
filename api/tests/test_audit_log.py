from django.test import Client
from django.urls import reverse
from resilient_logger.models import ResilientLogEntry

from api.factories import DeliveryLogFactory
from api.models import DeliveryLog
from audit_log.enums import Operation, StoreObjectState


def test_visiting_delivery_log_admin_view_writes_read_log(admin_user):
    """
    Test that visiting the DeliveryLog admin list view writes a read log for each object
    """
    client = Client()
    client.force_login(admin_user)

    delivery_logs = DeliveryLogFactory.create_batch(3)

    # Visit the admin list page of DeliveryLog (/admin/api/deliverylog/)
    url = reverse("admin:api_deliverylog_changelist")
    response = client.get(url)
    assert response.status_code == 200

    # Assert that a ResilientLogEntry was created for each DeliveryLog object
    qs = ResilientLogEntry.objects.filter(context__target__path=url)
    # There should be just 1 audit log entry
    assert qs.count() == 1
    audit_log_entry = qs.first()
    # The audit log entry should have all the delivery log ids in it
    assert sorted(audit_log_entry.context["target"]["object_ids"]) == sorted(
        [str(log.pk) for log in delivery_logs]
    )
    assert audit_log_entry.context["target"]["path"] == url
    assert audit_log_entry.context["target"]["type"] == DeliveryLog._meta.model_name
    assert audit_log_entry.context["operation"] == Operation.READ.value


def test_creating_delivery_log_writes_create_log(admin_user):
    """
    Test that creating a DeliveryLog object writes a create log.
    """
    client = Client()
    client.force_login(admin_user)

    # Get the URL for creating a new DeliveryLog object
    url = reverse("admin:api_deliverylog_add")

    # Send a POST request with data to create the object
    response = client.post(url, {"user": admin_user.pk, "report": "null"})

    # Assuming successful creation redirects to changelist view
    assert response.status_code == 302

    # Find the newly created DeliveryLog object
    delivery_log = DeliveryLog.objects.latest("pk")

    # Assert that a ResilientLogEntry was created for the creation
    qs = ResilientLogEntry.objects.filter(
        context__target__path=url, context__operation=Operation.CREATE.value
    )
    assert qs.count() == 1
    audit_log_entry = qs.first()

    # Verify the audit log entry details
    assert audit_log_entry.context["target"]["object_ids"] == [str(delivery_log.pk)]
    assert audit_log_entry.context["target"]["path"] == url
    assert audit_log_entry.context["target"]["type"] == DeliveryLog._meta.model_name
    assert audit_log_entry.context["operation"] == Operation.CREATE.value


def test_updating_delivery_log_writes_update_log(admin_user):
    """
    Test that updating a DeliveryLog object writes an update log.
    """
    client = Client()
    client.force_login(admin_user)

    delivery_log = DeliveryLogFactory()

    # Get the URL for updating the DeliveryLog object
    url = reverse("admin:api_deliverylog_change", args=[delivery_log.pk])

    # Send a POST request with updated data
    updated_data = {
        "user": admin_user.pk,
        "report": "null",
    }  # Example updated data
    response = client.post(url, updated_data)
    assert response.status_code == 302  # Redirect after successful update

    # Assert that a ResilientLogEntry was created for the update
    qs = ResilientLogEntry.objects.filter(
        context__target__path=url, context__operation=Operation.UPDATE.value
    )
    assert qs.count() == 1
    audit_log_entry = qs.first()

    # Verify the audit log entry details
    assert audit_log_entry.context["target"]["object_ids"] == [str(delivery_log.pk)]
    assert audit_log_entry.context["target"]["path"] == url
    assert audit_log_entry.context["target"]["type"] == DeliveryLog._meta.model_name
    assert audit_log_entry.context["operation"] == Operation.UPDATE.value


def test_deleting_delivery_log_writes_delete_log(admin_user):
    """
    Test that deleting a DeliveryLog object writes a delete log.
    """
    client = Client()
    client.force_login(admin_user)

    delivery_log = DeliveryLogFactory()

    # Get the URL for deleting the DeliveryLog object
    url = reverse("admin:api_deliverylog_delete", args=[delivery_log.pk])

    # Send a POST request to delete the object
    response = client.post(url, {"post": "yes"})
    assert response.status_code == 302  # Redirect after successful deletion

    # Assert that a ResilientLogEntry was created for the deletion
    qs = ResilientLogEntry.objects.filter(
        context__target__path=url, context__operation=Operation.DELETE.value
    )
    assert qs.count() == 1
    audit_log_entry = qs.first()

    # Verify the audit log entry details
    assert audit_log_entry.context["target"]["object_ids"] == [str(delivery_log.pk)]
    assert audit_log_entry.context["target"]["path"] == url
    assert audit_log_entry.context["target"]["type"] == DeliveryLog._meta.model_name
    assert audit_log_entry.context["operation"] == Operation.DELETE.value
    assert DeliveryLog.objects.count() == 0


def test_bulk_deleting_delivery_logs_writes_delete_log(admin_user):
    """
    Test that bulk deleting DeliveryLog objects writes a delete log.
    """
    client = Client()
    client.force_login(admin_user)

    count = 3

    delivery_logs = DeliveryLogFactory.create_batch(count)
    object_ids = [str(log.pk) for log in delivery_logs]

    # Get the URL for the changelist view
    url = reverse("admin:api_deliverylog_changelist")

    # Send a POST request to bulk delete the objects
    data = {
        "action": "delete_selected",
        "_selected_action": object_ids,
        "post": "yes",
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirect after successful deletion

    # Assert that a ResilientLogEntry was created for the bulk deletion
    qs = ResilientLogEntry.objects.filter(
        context__target__path=url, context__operation=Operation.DELETE.value
    )
    assert qs.count() == 1
    audit_log_entry = qs.first()

    # Verify the audit log entry details
    assert len(audit_log_entry.context["target"]["object_ids"]) == count
    assert sorted(audit_log_entry.context["target"]["object_ids"]) == sorted(object_ids)
    assert audit_log_entry.context["target"]["path"] == url
    assert audit_log_entry.context["target"]["type"] == DeliveryLog._meta.model_name
    assert audit_log_entry.context["operation"] == Operation.DELETE.value


def test_audit_log_converts_delivery_log_messages_to_list(admin_user, settings):
    """
    Test that ResilientLogEntry stores DeliveryLog messages as list format.

    DeliveryLog stores messages as dict in the database, but audit logs
    convert to list format to prevent Elasticsearch field limit issues.
    """
    import json

    # Enable object state storage in audit logs
    settings.AUDIT_LOG = {
        **settings.AUDIT_LOG,
        "STORE_OBJECT_STATE": StoreObjectState.OLD_AND_NEW_BOTH.value,
    }

    client = Client()
    client.force_login(admin_user)

    # Create a DeliveryLog with dict format messages
    delivery_log = DeliveryLogFactory(
        report={
            "errors": [],
            "warnings": [],
            "messages": {
                "+358401234567": {"converted": "+358401234567", "status": "CREATED"},
            },
        }
    )

    # Update it via admin to trigger audit log
    url = reverse("admin:api_deliverylog_change", args=[delivery_log.pk])
    response = client.post(
        url, {"user": admin_user.pk, "report": json.dumps(delivery_log.report)}
    )
    assert response.status_code == 302

    # Get the ResilientLogEntry for this specific update
    qs = ResilientLogEntry.objects.filter(
        context__operation=Operation.UPDATE.value,
        context__target__path=url,
    )
    assert qs.count() == 1
    audit_log = qs.first()

    # Verify the audit log has list format (not dict)
    object_states = audit_log.context["target"]["object_states"]
    new_report = object_states[0]["new_object_state"]["report"]

    assert isinstance(new_report["messages"], list), (
        "Messages should be list in audit log"
    )
    assert len(new_report["messages"]) == 1
    assert new_report["messages"][0]["converted"] == "+358401234567"

    # Verify original DeliveryLog still has dict format
    delivery_log.refresh_from_db()
    assert isinstance(delivery_log.report["messages"], dict), (
        "Messages should stay dict in DB"
    )
