import logging
from typing import Any, List, Optional, Union

import phonenumbers
from django.urls import reverse

from api.const import NOTIFICATION_TYPE_MOBILE, REGION
from api.types import Recipient, SendMessagePayload
from notification_service.settings import DEBUG, QURIIRI_REPORT_URL

logger = logger = logging.getLogger(__name__)


def collect_destinations(
    recipients: List[Recipient], number_type: Optional[str] = NOTIFICATION_TYPE_MOBILE
):
    if not format:
        return [r["destination"] for r in recipients]
    return [
        r["destination"]
        for r in recipients
        if r.get("format", "").lower() == number_type
    ]


def get_default_options(request, **kwargs):
    options = {}
    relative_drurl = reverse("delivery_log_webhook", kwargs={"id": kwargs.get("id")})
    if DEBUG:
        # Dev setting to receive delivery log
        options["drurl"] = f"{QURIIRI_REPORT_URL}{relative_drurl}"
    else:
        options["drurl"] = request.build_absolute_uri(relative_drurl)
    return options


def filter_valid_destinations(
    destinations: List[str], convert_to_international_format: bool = False
) -> List[str]:
    """
    Filters a list of recipients numbers and returns a list of valid phone numbers.

    Args:
        destinations: A list of recipients phone numbers as string.
        convert_to_international_format: If True, converts valid phone numbers
                                            to international format.

    Returns:
        A list of valid phone number objects as they were inputted or
        in international format.
    """
    valid_recipients = []
    for destination in destinations:
        try:
            phone_number = phonenumbers.parse(destination, REGION)
        except phonenumbers.NumberParseException:
            logger.warning(f"Invalid phone number format: {destination}")
            continue

        if phonenumbers.is_valid_number(phone_number):
            if convert_to_international_format:
                destination = phonenumbers.format_number(
                    phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
            valid_recipients.append(destination)
        else:
            logger.warning(f"Invalid phone number: {destination}")

    return valid_recipients


def validate_send_message_payload(post_data: Union[Any, SendMessagePayload]) -> None:
    """
    Validates the data to ensure it conforms to the SendMessagePayload structure.

    Payload example
    {
        "sender": "Hel.fi",
        "to": [
            {
                "destination": "string",
                "format": "MOBILE",
            },
            {
                "destination": "string",
                "format": "MOBILE",
            },
            {
                "destination": "string",
                "format": "MOBILE",
            }
        ],
        "text": "SMS message"
    }

    Args:
        data: The data to validate.

    Raises:
        ValueError: If the data is not valid.
    """

    if not isinstance(post_data, dict):
        raise ValueError("Data must be a dictionary")

    if not all(key in post_data for key in ("sender", "to", "text")):
        raise ValueError(
            "Missing required keys: 'sender', 'to', and 'text' are required."
        )

    if not isinstance(post_data["sender"], str):
        raise ValueError("'Sender' must be a string")

    if not isinstance(post_data["to"], list) or not all(
        isinstance(recipient, dict)
        and "destination" in recipient
        and isinstance(recipient["destination"], str)
        for recipient in post_data["to"]
    ):
        raise ValueError(
            "'To' must be a list of dictionaries, "
            "each with a string 'destination' field."
        )

    if not isinstance(post_data["text"], str):
        raise ValueError("'Text' must be a string")
