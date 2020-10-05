# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_send_sms 1"] = {
    "errors": [],
    "messages": {"+358461231231": {"converted": "+358461231231", "status": "CREATED"}},
    "warnings": [],
}

snapshots["test_webhook_delivery_log 1"] = {
    "errors": [],
    "messages": {"+358461231231": {"converted": "+358461231231", "status": "CREATED"}},
    "warnings": [],
}

snapshots["test_webhook_delivery_log 2"] = {
    "errors": [],
    "messages": {
        "+358461231231": {
            "billingref": "Palvelutarjotin",
            "destination": "+358461231231",
            "sender": "hel.fi",
            "smscount": "1",
            "status": "DELIVERED",
            "statustime": "2020-07-21T09:18:00Z",
        }
    },
    "warnings": [],
}

snapshots["test_get_delivery_log 1"] = {
    "errors": [],
    "messages": {"+358461231231": {"converted": "+358461231231", "status": "CREATED"}},
    "warnings": [],
}
