from django.db import transaction
from django.http import HttpResponseBadRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import DeliveryLog
from api.serializers import DeliveryLogSerializer
from api.types import SendMessagePayload
from api.utils import (
    collect_destinations,
    filter_valid_destinations,
    get_default_options,
    validate_send_message_payload,
)
from notification_service.settings import QURIIRI_API_KEY, QURIIRI_API_URL
from quriiri.send import Sender

sms_sender = Sender(QURIIRI_API_KEY, QURIIRI_API_URL)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def send_message(request):
    """
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
    """
    data: SendMessagePayload = request.data
    try:
        validate_send_message_payload(data)
    except ValueError as e:
        return HttpResponseBadRequest(e)

    destinations = collect_destinations(recipients=data["to"], number_type=None)
    # Get unique list of phone numbers converted to international format
    unique_valid_destinations = list(
        set(
            filter_valid_destinations(
                destinations, convert_to_international_format=True
            )
        )
    )

    if not unique_valid_destinations:
        return HttpResponseBadRequest("No valid destinations for SMS sender.")

    log = DeliveryLog.objects.create(user=request.user)
    options = get_default_options(request, id=log.id)

    resp = sms_sender.send_sms(
        data["sender"], unique_valid_destinations, data["text"], **options
    )

    log.report = resp
    log.save()

    return Response(DeliveryLogSerializer(log).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_delivery_log(request, id):
    user = request.user
    try:
        log = user.delivery_logs.get(id=id)
    except DeliveryLog.DoesNotExist:
        return Response(status=404, data={"error": f" Message ID: {id} does not exist"})
    data = DeliveryLogSerializer(log).data
    return Response(data=data)


@api_view(["POST"])
# TODO: We probably need some basic authentication before writing data
def delivery_log_webhook(request, id):
    try:
        log = DeliveryLog.objects.get(id=id)
    except DeliveryLog.DoesNotExist:
        # Response error so Quriiri will retry to send the report several times
        return Response(status=404, data={"error": f" Message ID: {id} does not exist"})
    log.update_report(request.data)

    return Response(status=200)
