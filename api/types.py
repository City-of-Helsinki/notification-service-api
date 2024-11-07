from typing import List, Optional, TypedDict


class Recipient(TypedDict):
    destination: str
    format: Optional[str]


class SendMessagePayload(TypedDict):
    sender: str
    to: List[Recipient]
    text: str


class MessageWebhookPayload(TypedDict):
    sender: str
    destination: str
    status: str
    statustime: str
    smscount: str
    billingref: str
