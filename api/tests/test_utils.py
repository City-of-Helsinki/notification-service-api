import pytest

from api.utils import filter_valid_destinations, validate_send_message_payload

REGION_FI_VALID_PHONE_NUMBERS = [
    "+358 40 123 4567",
    "+358 50 123 4567",
    "+358 5 0 1 2 3 4 5 6 7",
    "+358 5 0 123 4 56 7",
    "040 123 4567",
    "041 123 4567",
    "050 123 4567",
    "0 5  0 123 4 5 6 7",
    "(09) 10 12345",
    "+12124567890",
    "+12124567890",
    "+1 212.456.7890",
    # Randomly generated numbers with
    # https://www.random-name-generator.com/finland-phone-number-generator.
    "045 50071",
    "+3584550071",
    "018 835339",
    "06 47893819",
    "08 6700313",
    "05 8802237",
    "02 390141",
    "+3582390141",
    "09 1049703",
    "+35891049703",
    "03 11481210",
    "+358311481210",
    "+492511793147",
    "+46806519853",
    "+4567044733",
]


def test_validate_send_message_payload_valid_data():
    """Test with valid data."""
    data = {
        "sender": "Hel.fi",
        "to": [{"destination": "string", "format": "MOBILE"}],
        "text": "SMS message",
    }
    validate_send_message_payload(data)  # No exception should be raised


def test_validate_send_message_payload_missing_keys():
    """Test with missing keys."""
    data = {"sender": "Hel.fi", "to": [{"destination": "string"}]}
    with pytest.raises(ValueError) as excinfo:
        validate_send_message_payload(data)
    assert (
        excinfo.value.args[0]
        == "Missing required keys: 'sender', 'to', and 'text' are required."
    )


def test_validate_send_message_payload_invalid_sender_type():
    """Test with invalid sender type."""
    data = {
        "sender": 123,  # Invalid sender type
        "to": [{"destination": "string"}],
        "text": "SMS message",
    }
    with pytest.raises(ValueError) as excinfo:
        validate_send_message_payload(data)
    assert excinfo.value.args[0] == "'Sender' must be a string"


def test_validate_send_message_payload_invalid_to_type():
    """Test with invalid 'to' field type."""
    data = {"sender": "Hel.fi", "to": "invalid", "text": "SMS message"}
    with pytest.raises(ValueError) as excinfo:
        validate_send_message_payload(data)
    assert (
        excinfo.value.args[0]
        == "'To' must be a list of dictionaries, each with a string 'destination' field."  # noqa
    )


def test_validate_send_message_payload_invalid_to_item_type():
    """Test with invalid item type in 'to' field."""
    data = {"sender": "Hel.fi", "to": [123], "text": "SMS message"}
    with pytest.raises(ValueError) as excinfo:
        validate_send_message_payload(data)
    assert (
        excinfo.value.args[0]
        == "'To' must be a list of dictionaries, each with a string 'destination' field."  # noqa
    )


def test_validate_send_message_payload_missing_destination_in_to():
    """Test with missing 'destination' in a 'to' item."""
    data = {"sender": "Hel.fi", "to": [{"format": "MOBILE"}], "text": "SMS message"}
    with pytest.raises(ValueError) as excinfo:
        validate_send_message_payload(data)
    assert (
        excinfo.value.args[0]
        == "'To' must be a list of dictionaries, each with a string 'destination' field."  # noqa
    )


def test_validate_send_message_payload_invalid_text_type():
    """Test with invalid text type."""
    data = {
        "sender": "Hel.fi",
        "to": [{"destination": "string"}],
        "text": 123,  # Invalid text type
    }
    with pytest.raises(ValueError) as excinfo:
        validate_send_message_payload(data)
    assert excinfo.value.args[0] == "'Text' must be a string"


def test_filter_valid_destinations_valid_numbers():
    """Test with valid phone numbers."""
    destinations = [
        "+358501234567",
        "0401234567",  # Assuming REGION is set appropriately
    ]
    valid_numbers = filter_valid_destinations(destinations)
    assert len(valid_numbers) == len(destinations) == 2


@pytest.mark.parametrize("phone_number", REGION_FI_VALID_PHONE_NUMBERS)
def test_filter_valid_destinations_different_valid_formats(phone_number):
    assert filter_valid_destinations([phone_number])


def test_filter_valid_destinations_invalid_numbers():
    """Test with invalid phone numbers."""
    destinations = [
        "invalid",
        "12345",
    ]
    valid_numbers = filter_valid_destinations(destinations)
    assert len(valid_numbers) == 0  # No valid numbers


def test_filter_valid_destinations_mixed_numbers():
    """Test with a mix of valid and invalid phone numbers."""
    destinations = [
        "+358501234567",
        "invalid",
        "0401234567",
    ]
    valid_numbers = filter_valid_destinations(destinations)
    assert len(valid_numbers) == 2


def test_filter_valid_destinations_international_format():
    """Test with convert_to_international_format=True."""
    destinations = ["0401234567"]
    valid_numbers = filter_valid_destinations(
        destinations, convert_to_international_format=True
    )
    assert len(valid_numbers) == 1
    assert isinstance(valid_numbers[0], str)
    assert valid_numbers[0].startswith("+")  # Check for international format
