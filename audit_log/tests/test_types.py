import pytest

from audit_log.enums import Operation
from audit_log.types import AuditActorData, AuditCommitMessage, AuditEvent, AuditTarget

TEST_IP_ADDRESS = "127.0.0.1"


# Create fixtures for reusable components
@pytest.fixture
def valid_actor():
    return AuditActorData(role="user", uuid="123", ip_address=TEST_IP_ADDRESS)


@pytest.fixture
def valid_target():
    return AuditTarget(path="/test", object_ids=["1", "2", "3"])


@pytest.fixture
def valid_event(valid_actor, valid_target):
    return AuditEvent(
        origin="test",
        date_time_epoch=1234567890,
        date_time="2024-11-14T16:00:00Z",
        status="success",
        actor=valid_actor,
        operation=Operation.CREATE,
        target=valid_target,
    )


# Tests for AuditActorData
def test_audit_actor_data_valid(valid_actor):
    assert valid_actor.role == "user"
    assert valid_actor.uuid == "123"
    assert valid_actor.ip_address == TEST_IP_ADDRESS


@pytest.mark.parametrize(
    "role, uuid, ip_address",
    [
        (123, "123", TEST_IP_ADDRESS),
        ("user", 123, TEST_IP_ADDRESS),
        ("user", "123", 123),
    ],
)
def test_audit_actor_data_invalid_types(role, uuid, ip_address):
    with pytest.raises(TypeError):
        AuditActorData(role=role, uuid=uuid, ip_address=ip_address)


# Tests for AuditTarget
def test_audit_target_valid(valid_target):
    assert valid_target.path == "/test"
    assert valid_target.object_ids == ["1", "2", "3"]


@pytest.mark.parametrize(
    "path, object_ids",
    [
        (123, ["1", "2", "3"]),
        ("/test", [1, 2, 3]),
    ],
)
def test_audit_target_invalid_types(path, object_ids):
    with pytest.raises(TypeError):
        AuditTarget(path=path, object_ids=object_ids)


# Tests for AuditEvent
def test_audit_event_valid(valid_event):
    assert valid_event.origin == "test"
    assert valid_event.date_time_epoch == 1234567890
    assert valid_event.date_time == "2024-11-14T16:00:00Z"
    assert valid_event.status == "success"
    assert isinstance(valid_event.actor, AuditActorData)
    assert valid_event.operation == Operation.CREATE
    assert isinstance(valid_event.target, AuditTarget)


def test_audit_event_valid_actor_dict(valid_target):
    event = AuditEvent(
        origin="test",
        date_time_epoch=1234567890,
        date_time="2024-11-14T16:00:00Z",
        status="success",
        actor={"role": "user", "uuid": "123", "ip_address": TEST_IP_ADDRESS},
        operation=Operation.CREATE,
        target=valid_target,
    )
    assert isinstance(event.actor, AuditActorData)


def test_audit_event_valid_target_dict(valid_actor):
    event = AuditEvent(
        origin="test",
        date_time_epoch=1234567890,
        date_time="2024-11-14T16:00:00Z",
        status="success",
        actor=valid_actor,
        operation=Operation.CREATE,
        target={"path": "/test", "object_ids": ["1", "2", "3"]},
    )
    assert isinstance(event.target, AuditTarget)


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("origin", 123),
        ("date_time_epoch", "1234567890"),
        ("date_time", 1234567890),
        ("status", 123),
        ("actor", "user"),
        ("operation", 123),
        ("target", "test"),
    ],
)
def test_audit_event_invalid_fields(valid_actor, valid_target, field, invalid_value):
    kwargs = {
        "origin": "test",
        "date_time_epoch": 1234567890,
        "date_time": "2024-11-14T16:00:00Z",
        "status": "success",
        "actor": valid_actor,
        "operation": Operation.CREATE,
        "target": valid_target,
    }
    kwargs[field] = invalid_value
    with pytest.raises(TypeError):
        AuditEvent(**kwargs)


# Tests for AuditCommitMessage
def test_audit_commit_message_valid(valid_event):
    message = AuditCommitMessage(audit_event=valid_event)
    assert isinstance(message.audit_event, AuditEvent)


def test_audit_commit_message_valid_event_dict(valid_actor, valid_target):
    message = AuditCommitMessage(
        audit_event={
            "origin": "test",
            "date_time_epoch": 1234567890,
            "date_time": "2024-11-14T16:00:00Z",
            "status": "success",
            "actor": valid_actor,
            "operation": Operation.CREATE,
            "target": valid_target,
        }
    )
    assert isinstance(message.audit_event, AuditEvent)


def test_audit_commit_message_invalid_event():
    with pytest.raises(TypeError):
        AuditCommitMessage(audit_event=123)
