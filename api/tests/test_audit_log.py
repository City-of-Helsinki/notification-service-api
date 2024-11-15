from django.test import Client
from django.urls import reverse

from api.factories import DeliveryLogFactory
from api.models import DeliveryLog
from audit_log.enums import Operation
from audit_log.models import AuditLogEntry


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

    # Assert that an AuditLogEntry was created for each DeliveryLog object
    qs = AuditLogEntry.objects.filter(message__audit_event__target__path=url)
    # There should be just 1 audit log entry
    assert qs.count() == 1
    audit_log_entry = qs.first()
    # The audit log entry should have all the delivery log ids in it
    assert audit_log_entry.message["audit_event"]["target"]["object_ids"] == [
        str(log.pk) for log in delivery_logs
    ]
    assert audit_log_entry.message["audit_event"]["target"]["path"] == url
    assert (
        audit_log_entry.message["audit_event"]["target"]["type"]
        == DeliveryLog._meta.model_name
    )
    assert audit_log_entry.message["audit_event"]["operation"] == Operation.READ.value


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

    # Assert that an AuditLogEntry was created for the creation
    qs = AuditLogEntry.objects.filter(
        message__audit_event__target__path=url,
        message__audit_event__operation=Operation.CREATE.value,
    )
    assert qs.count() == 1
    audit_log_entry = qs.first()

    # Verify the audit log entry details
    assert audit_log_entry.message["audit_event"]["target"]["object_ids"] == [
        str(delivery_log.pk)
    ]
    assert audit_log_entry.message["audit_event"]["target"]["path"] == url
    assert (
        audit_log_entry.message["audit_event"]["target"]["type"]
        == DeliveryLog._meta.model_name
    )
    assert audit_log_entry.message["audit_event"]["operation"] == Operation.CREATE.value


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

    # Assert that an AuditLogEntry was created for the update
    qs = AuditLogEntry.objects.filter(
        message__audit_event__target__path=url,
        message__audit_event__operation=Operation.UPDATE.value,
    )
    assert qs.count() == 1
    audit_log_entry = qs.first()

    # Verify the audit log entry details
    assert audit_log_entry.message["audit_event"]["target"]["object_ids"] == [
        str(delivery_log.pk)
    ]
    assert audit_log_entry.message["audit_event"]["target"]["path"] == url
    assert (
        audit_log_entry.message["audit_event"]["target"]["type"]
        == DeliveryLog._meta.model_name
    )
    assert audit_log_entry.message["audit_event"]["operation"] == Operation.UPDATE.value


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

    # Assert that an AuditLogEntry was created for the deletion
    qs = AuditLogEntry.objects.filter(
        message__audit_event__target__path=url,
        message__audit_event__operation=Operation.DELETE.value,
    )
    assert qs.count() == 1
    audit_log_entry = qs.first()

    # Verify the audit log entry details
    assert audit_log_entry.message["audit_event"]["target"]["object_ids"] == [
        str(delivery_log.pk)
    ]
    assert audit_log_entry.message["audit_event"]["target"]["path"] == url
    assert (
        audit_log_entry.message["audit_event"]["target"]["type"]
        == DeliveryLog._meta.model_name
    )
    assert audit_log_entry.message["audit_event"]["operation"] == Operation.DELETE.value
    assert DeliveryLog.objects.count() == 0


def test_bulk_deleting_delivery_logs_writes_delete_log(admin_user):
    """
    Test that bulk deleting DeliveryLog objects writes a delete log.
    """
    client = Client()
    client.force_login(admin_user)

    COUNT = 3

    delivery_logs = DeliveryLogFactory.create_batch(COUNT)
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

    # Assert that an AuditLogEntry was created for the bulk deletion
    qs = AuditLogEntry.objects.filter(
        message__audit_event__target__path=url,
        message__audit_event__operation=Operation.DELETE.value,
    )
    assert qs.count() == 1
    audit_log_entry = qs.first()

    # Verify the audit log entry details
    assert len(audit_log_entry.message["audit_event"]["target"]["object_ids"]) == COUNT
    assert audit_log_entry.message["audit_event"]["target"]["path"] == url
    assert (
        audit_log_entry.message["audit_event"]["target"]["type"]
        == DeliveryLog._meta.model_name
    )
    assert audit_log_entry.message["audit_event"]["operation"] == Operation.DELETE.value
