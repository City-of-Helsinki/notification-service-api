from collections import Counter
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from freezegun import freeze_time
from rest_framework import status

from audit_log.enums import Operation, Role, Status
from audit_log.models import AuditLogEntry
from audit_log.services import audit_log_service
from audit_log.settings import audit_logging_settings
from users.factories import UserFactory

User = get_user_model()

TEST_IP_ADDRESS = "1.2.3.4"


def _assert_basic_log_entry_data(log_entry):
    current_time = datetime.now(tz=timezone.utc)
    iso_8601_date = f"{current_time.replace(tzinfo=None).isoformat(sep='T', timespec='milliseconds')}Z"  # noqa

    assert log_entry.message["audit_event"]["origin"] == audit_logging_settings.ORIGIN
    assert log_entry.message["audit_event"]["date_time_epoch"] == int(
        current_time.timestamp() * 1000
    )
    assert log_entry.message["audit_event"]["date_time"] == iso_8601_date


def _create_default_request_mock(user):
    return Mock(
        method="GET",
        user=user,
        path="/v1/endpoint",
        headers={"x-forwarded-for": f"{TEST_IP_ADDRESS}:80"},
    )


def _assert_target_data(target_data, expected_path, expected_object_ids):
    assert target_data.path == expected_path
    assert Counter(target_data.object_ids) == Counter(expected_object_ids)


@freeze_time("2023-10-17 13:30:00+02:00")
@pytest.mark.parametrize(
    "status_code,audit_status",
    [
        (status.HTTP_200_OK, Status.SUCCESS.value),
        (status.HTTP_201_CREATED, Status.SUCCESS.value),
        (status.HTTP_204_NO_CONTENT, Status.SUCCESS.value),
        (status.HTTP_401_UNAUTHORIZED, Status.FORBIDDEN.value),
        (status.HTTP_403_FORBIDDEN, Status.FORBIDDEN.value),
        (status.HTTP_302_FOUND, "Unknown: 302"),
        (status.HTTP_404_NOT_FOUND, "Unknown: 404"),
        (status.HTTP_502_BAD_GATEWAY, "Unknown: 502"),
    ],
)
@pytest.mark.django_db
def test_commit_to_audit_log_response_status(status_code, audit_status):
    user = UserFactory()
    req_mock = _create_default_request_mock(user)
    setattr(req_mock, audit_logging_settings.REQUEST_AUDIT_LOG_VAR, {1})
    res_mock = Mock(status_code=status_code)
    assert AuditLogEntry.objects.count() == 0

    audit_log_service.commit_to_audit_log(req_mock, res_mock)

    assert AuditLogEntry.objects.count() == 1
    log_entry = AuditLogEntry.objects.first()
    assert log_entry.message["audit_event"]["status"] == audit_status
    _assert_basic_log_entry_data(log_entry)


@freeze_time("2023-10-17 13:30:00+02:00")
@pytest.mark.parametrize(
    "http_method,audit_operation",
    [
        ("GET", Operation.READ.value),
        ("HEAD", Operation.READ.value),
        ("OPTIONS", Operation.READ.value),
        ("POST", Operation.CREATE.value),
        ("PUT", Operation.UPDATE.value),
        ("PATCH", Operation.UPDATE.value),
        ("DELETE", Operation.DELETE.value),
    ],
)
@pytest.mark.django_db
def test_commit_to_audit_log_crud_operations(http_method, audit_operation):
    user = UserFactory()
    req_mock = Mock(
        method=http_method,
        user=user,
        path="/v1/endpoint",
        headers={"x-forwarded-for": TEST_IP_ADDRESS},
        **{audit_logging_settings.REQUEST_AUDIT_LOG_VAR: {1}},
    )
    res_mock = Mock(status_code=200)
    assert AuditLogEntry.objects.count() == 0

    audit_log_service.commit_to_audit_log(req_mock, res_mock)

    assert AuditLogEntry.objects.count() == 1
    log_entry = AuditLogEntry.objects.first()
    assert log_entry.message["audit_event"]["operation"] == audit_operation
    assert log_entry.message["audit_event"]["target"]["path"] == "/v1/endpoint"
    assert log_entry.message["audit_event"]["target"]["object_ids"] == ["1"]
    _assert_basic_log_entry_data(log_entry)


@freeze_time("2023-10-17 13:30:00+02:00")
@pytest.mark.parametrize(
    "user_role,audit_role",
    [
        ("staff", Role.ADMIN.value),
        ("superuser", Role.ADMIN.value),
        ("regular_user", Role.USER.value),
        ("anonymous", Role.ANONYMOUS.value),
    ],
)
@pytest.mark.django_db
def test_commit_to_audit_log_actor_data(user_role, audit_role):
    if user_role == "anonymous":
        user = AnonymousUser()
    else:
        user = UserFactory(
            is_staff=user_role == "staff", is_superuser=user_role == "superuser"
        )
    req_mock = _create_default_request_mock(user)
    setattr(req_mock, audit_logging_settings.REQUEST_AUDIT_LOG_VAR, {1})
    res_mock = Mock(status_code=200)
    assert AuditLogEntry.objects.count() == 0

    audit_log_service.commit_to_audit_log(req_mock, res_mock)

    assert AuditLogEntry.objects.count() == 1
    log_entry = AuditLogEntry.objects.first()
    assert log_entry.message["audit_event"]["actor"]["role"] == audit_role
    assert log_entry.message["audit_event"]["actor"]["ip_address"] == TEST_IP_ADDRESS
    if hasattr(user, "uuid"):
        assert log_entry.message["audit_event"]["actor"]["uuid"] == str(user.uuid)
    _assert_basic_log_entry_data(log_entry)


@pytest.mark.django_db
def test_dont_commit_audit_logs_if_no_loggable_ids():
    user = AnonymousUser()
    req_mock = _create_default_request_mock(user)
    setattr(req_mock, audit_logging_settings.REQUEST_AUDIT_LOG_VAR, set())
    res_mock = Mock(status_code=200)
    assert AuditLogEntry.objects.count() == 0

    audit_log_service.commit_to_audit_log(req_mock, res_mock)

    assert AuditLogEntry.objects.count() == 0


@pytest.mark.parametrize(
    "queryset_type",
    [
        "queryset",
        "empty_queryset",
    ],
)
@pytest.mark.django_db
def test_get_target_queryset(queryset_type):
    user = UserFactory()
    req_mock = _create_default_request_mock(user)
    req_mock._request = Mock(
        path="/v1/endpoint", **{audit_logging_settings.REQUEST_AUDIT_LOG_VAR: set()}
    )
    if queryset_type == "queryset":
        UserFactory()
        instances = User.objects.all()
        object_ids = [str(user.pk) for user in instances]
    else:
        instances = User.objects.none()
        object_ids = []

    audit_log_service.add_audit_logged_object_ids(req_mock, instances)

    target_data = audit_log_service.get_target(req_mock._request)
    _assert_target_data(target_data, req_mock.path, object_ids)


@pytest.mark.parametrize(
    "list_type",
    [
        "list",
        "list_of_objects_without_pks",
        "list_of_nones",
        "list_of_strings",
        "empty_list",
    ],
)
@pytest.mark.django_db
def test_get_target_list(list_type):
    user = UserFactory()
    req_mock = _create_default_request_mock(user)
    req_mock._request = Mock(
        path="/v1/endpoint", **{audit_logging_settings.REQUEST_AUDIT_LOG_VAR: set()}
    )
    list_type_mapping = {
        "list": [user, UserFactory()],
        "list_of_objects_without_pks": [User(), User()],
        "list_of_nones": [None, None],
        "list_of_strings": ["test", "", " "],
        "empty_list": [],
    }
    instances = list_type_mapping[list_type]
    object_ids = [str(user.pk) for user in instances] if list_type == "list" else []

    audit_log_service.add_audit_logged_object_ids(req_mock, instances)

    target_data = audit_log_service.get_target(req_mock._request)
    _assert_target_data(target_data, req_mock.path, object_ids)


@pytest.mark.parametrize(
    "object_type",
    [
        "object",
        "object_without_pk",
        "none",
    ],
)
@pytest.mark.django_db
def test_get_target_object(object_type):
    user = UserFactory()
    req_mock = _create_default_request_mock(user)
    req_mock._request = Mock(
        path="/v1/endpoint", **{audit_logging_settings.REQUEST_AUDIT_LOG_VAR: set()}
    )
    object_type_mapping = {
        "object": user,
        "object_without_pk": User(),
        "none": None,
    }
    instances = object_type_mapping[object_type]
    object_ids = [str(user.pk)] if object_type == "object" else []

    audit_log_service.add_audit_logged_object_ids(req_mock, instances)

    target_data = audit_log_service.get_target(req_mock._request)
    _assert_target_data(target_data, req_mock.path, object_ids)
