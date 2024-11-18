from unittest.mock import Mock

import pytest
from rest_framework import status

from audit_log.enums import Status
from audit_log.models import DummyTestModel
from audit_log.settings import (
    audit_logging_settings,
    StoreObjectState,
)
from audit_log.types import (
    ObjectState,
    ObjectStateDiff,
)
from audit_log.utils import (
    create_object_states,
    diff_dicts,
    get_remote_address,
    get_response_status,
)

TEST_IP_ADDRESS_V4 = "1.2.3.4"
TEST_IP_ADDRESS_v6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"


@pytest.mark.parametrize(
    "remote_address,expected,x_forwarded_for",
    [
        (f"{TEST_IP_ADDRESS_V4}:443", TEST_IP_ADDRESS_V4, True),
        (TEST_IP_ADDRESS_V4, TEST_IP_ADDRESS_V4, True),
        (
            f"[{TEST_IP_ADDRESS_v6}]:443",
            TEST_IP_ADDRESS_v6,
            True,
        ),
        (
            TEST_IP_ADDRESS_v6,
            TEST_IP_ADDRESS_v6,
            True,
        ),
        (TEST_IP_ADDRESS_V4, TEST_IP_ADDRESS_V4, False),
        (
            TEST_IP_ADDRESS_v6,
            TEST_IP_ADDRESS_v6,
            False,
        ),
    ],
)
def test_get_remote_address(remote_address, expected, x_forwarded_for):
    req_mock = Mock(
        headers={"x-forwarded-for": remote_address} if x_forwarded_for else {},
        META={"REMOTE_ADDR": remote_address} if not x_forwarded_for else {},
    )
    assert get_remote_address(req_mock) == expected


@pytest.mark.parametrize(
    "status_code,audit_status",
    [
        (status.HTTP_200_OK, Status.SUCCESS.value),
        (status.HTTP_201_CREATED, Status.SUCCESS.value),
        (status.HTTP_204_NO_CONTENT, Status.SUCCESS.value),
        (status.HTTP_401_UNAUTHORIZED, Status.FORBIDDEN.value),
        (status.HTTP_403_FORBIDDEN, Status.FORBIDDEN.value),
        (status.HTTP_302_FOUND, None),
        (status.HTTP_404_NOT_FOUND, None),
        (status.HTTP_502_BAD_GATEWAY, None),
    ],
)
def test_get_response_status(status_code, audit_status):
    res_mock = Mock(status_code=status_code)

    assert get_response_status(res_mock) == audit_status


@pytest.mark.parametrize(
    "old_dict, new_dict, expected_diff",
    [
        ({}, {}, {}),
        ({"a": 1}, {"a": 1}, {}),
        ({"a": 1}, {"a": 2}, {"a": 2}),
        ({"a": 1}, {"b": 2}, {"b": 2}),
        ({"a": 1, "b": 2}, {"a": 2, "b": 2}, {"a": 2}),
    ],
)
def test_diff_dicts(old_dict, new_dict, expected_diff):
    assert diff_dicts(old_dict, new_dict) == expected_diff


@pytest.mark.parametrize(
    "store_object_state, expected_output_type",
    [
        (StoreObjectState.NONE, type(None)),
        (StoreObjectState.DIFF, ObjectStateDiff),
        (StoreObjectState.ALL, ObjectState),
        (StoreObjectState.NEW_ONLY, ObjectState),
        (StoreObjectState.OLD_ONLY, ObjectState),
        (StoreObjectState.OLD_AND_NEW_BOTH, ObjectState),
    ],
)
def test_create_object_states_output_type(
    store_object_state,
    expected_output_type,
    monkeypatch,
):
    monkeypatch.setattr(
        audit_logging_settings, "STORE_OBJECT_STATE", store_object_state
    )

    new_objects = [DummyTestModel(number_field=1, text_field="New")]
    old_objects = [DummyTestModel(number_field=1, text_field="Old")]

    result = create_object_states(new_objects, old_objects)

    if store_object_state == StoreObjectState.NONE:
        assert result is None
    else:
        assert isinstance(result[0], expected_output_type)


def test_create_object_states_diff(
    monkeypatch,
):
    monkeypatch.setattr(
        audit_logging_settings, "STORE_OBJECT_STATE", StoreObjectState.DIFF
    )

    new_objects = [DummyTestModel(number_field=1, text_field="New")]
    old_objects = [DummyTestModel(number_field=1, text_field="Old")]

    result = create_object_states(new_objects, old_objects)

    assert len(result) == 1
    assert result[0].object_state_diff == {"text_field": "New"}


def test_create_object_states_all(
    monkeypatch,
):
    monkeypatch.setattr(
        audit_logging_settings, "STORE_OBJECT_STATE", StoreObjectState.ALL
    )

    new_objects = [DummyTestModel(number_field=1, text_field="New")]
    old_objects = [DummyTestModel(number_field=1, text_field="Old")]

    result = create_object_states(new_objects, old_objects)

    assert len(result) == 1
    assert result[0].old_object_state == {
        "boolean_field": False,
        "number_field": 1,
        "text_field": "Old",
    }
    assert result[0].new_object_state == {
        "boolean_field": False,
        "number_field": 1,
        "text_field": "New",
    }
    assert result[0].object_state_diff == {"text_field": "New"}


def test_create_object_states_with_old_and_new(
    monkeypatch,
):
    monkeypatch.setattr(
        audit_logging_settings, "STORE_OBJECT_STATE", StoreObjectState.OLD_AND_NEW_BOTH
    )

    new_objects = [DummyTestModel(number_field=1, text_field="New")]
    old_objects = [DummyTestModel(number_field=1, text_field="Old")]

    result = create_object_states(new_objects, old_objects)

    assert len(result) == 1
    assert result[0].old_object_state == {
        "boolean_field": False,
        "number_field": 1,
        "text_field": "Old",
    }
    assert result[0].new_object_state == {
        "boolean_field": False,
        "number_field": 1,
        "text_field": "New",
    }


def test_create_object_states_different_lengths(
    monkeypatch,
):
    monkeypatch.setattr(
        audit_logging_settings, "STORE_OBJECT_STATE", StoreObjectState.OLD_AND_NEW_BOTH
    )

    new_objects = [
        DummyTestModel(number_field=1, text_field="Old"),
        DummyTestModel(number_field=2, text_field="New"),
    ]
    old_objects = [DummyTestModel(number_field=1, text_field="Old")]

    result = create_object_states(new_objects, old_objects)

    assert len(result) == 2
    assert (
        result[0].new_object_state
        == result[0].old_object_state
        == {
            "boolean_field": False,
            "number_field": 1,
            "text_field": "Old",
        }
    )
    assert result[1].old_object_state == {}
    assert result[1].new_object_state == {
        "boolean_field": False,
        "number_field": 2,
        "text_field": "New",
    }
