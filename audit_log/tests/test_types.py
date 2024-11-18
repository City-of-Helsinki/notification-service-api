from dataclasses import replace

import pytest

from audit_log.enums import Operation
from audit_log.types import (
    AuditActorData,
    AuditCommitMessage,
    AuditEvent,
    AuditTarget,
    ObjectState,
    ObjectStateDiff,
)

TEST_IP_ADDRESS = "127.0.0.1"


# Create fixtures for reusable components
@pytest.fixture
def valid_actor():
    return AuditActorData(
        role="user", uuid="123", user_id="123", ip_address=TEST_IP_ADDRESS
    )


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
    assert valid_actor.user_id == "123"
    assert valid_actor.ip_address == TEST_IP_ADDRESS


@pytest.mark.parametrize(
    "role, uuid, user_id, ip_address",
    [
        (123, "123", "123", TEST_IP_ADDRESS),
        ("user", 123, "123", TEST_IP_ADDRESS),
        ("user", "123", 123, TEST_IP_ADDRESS),
        ("user", "123", "123", 123),
    ],
)
def test_audit_actor_data_invalid_types(role, uuid, user_id, ip_address):
    with pytest.raises(TypeError):
        AuditActorData(role=role, uuid=uuid, user_id=user_id, ip_address=ip_address)


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
        actor={
            "role": "user",
            "uuid": "123",
            "user_id": "123",
            "ip_address": TEST_IP_ADDRESS,
        },
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
    "object_states",
    [
        [{"old_object_state": {"number": 123, "string": "xyz"}}],
        [{"new_object_state": {"number": 123, "string": "xyz"}}],
        [{"object_state_diff": {"number": 123, "string": "xyz"}}],
        [
            {"old_object_state": {"number": 123, "string": "xyz"}},
            {"old_object_state": {"number": 321, "string": "zyx"}},
        ],
        [
            {
                "old_object_state": {"number": 123, "string": "old"},
                "new_object_state": {"number": 1234, "string": "new"},
            },
            {"old_object_state": {"number": 321, "string": "zyx"}},
            {"object_state_diff": {"number": 321, "string": "zyx"}},
        ],
        None,
    ],
)
def test_audit_event_valid_target_dict_with_object_states(object_states, valid_actor):
    event = AuditEvent(
        origin="test",
        date_time_epoch=1234567890,
        date_time="2024-11-14T16:00:00Z",
        status="success",
        actor=valid_actor,
        operation=Operation.CREATE,
        target={
            "path": "/test",
            "object_ids": ["1", "2", "3"],
            "object_states": object_states,
        },
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


@pytest.mark.parametrize(
    "object_states",
    [
        [ObjectState(old_object_state={"number": 123, "string": "xyz"})],
        [ObjectState(new_object_state={"number": 123, "string": "xyz"})],
        [ObjectStateDiff(object_state_diff={"number": 123, "string": "xyz"})],
        [
            ObjectState(
                old_object_state={"number": 123, "string": "xyz"},
                new_object_state={"number": 321, "string": "zyx"},
            )
        ],
        [
            ObjectState(
                old_object_state={"number": 123, "string": "old"},
                new_object_state={"number": 1234, "string": "new"},
            ),
            ObjectState(old_object_state={"number": 123, "string": "xyz"}),
            [ObjectStateDiff(object_state_diff={"number": 321, "string": "xyz"})],
        ],
        [],
        None,
    ],
)
def test_valid_audit_target_object_states(object_states, valid_target):
    target = replace(valid_target, object_states=object_states)
    assert isinstance(target, AuditTarget)


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
