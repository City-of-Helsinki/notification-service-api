import logging

from django.db import transaction
from django.http import HttpResponseBadRequest
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import DeliveryLog
from api.serializers import DeliveryLogSerializer, SendMessagePayloadSerializer
from api.types import SendMessagePayload
from api.utils import (
    collect_destinations,
    filter_valid_destinations,
    get_default_options,
    validate_send_message_payload,
)
from audit_log.enums import Operation
from audit_log.services import audit_log_service, create_api_commit_message_from_request
from notification_service.settings import QURIIRI_API_KEY, QURIIRI_API_URL
from quriiri.send import Sender

logger = logging.getLogger(__name__)

sms_sender = Sender(QURIIRI_API_KEY, QURIIRI_API_URL)


@extend_schema(
    request=SendMessagePayloadSerializer,
    responses={200: DeliveryLogSerializer},
    description="""
    Send an SMS message.
    Payload example:
    ```json
    {
        "sender": "Hel.fi",
        "to": [
            {
                "destination": "string",
                "format": "MOBILE"
            },
            {
                "destination": "string",
                "format": "MOBILE"
            },
            {
                "destination": "string",
                "format": "MOBILE"
            }
        ],
        "text": "SMS message"
    }
    ```
    """,
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def send_message(request):
    data: SendMessagePayload = request.data
    try:
        validate_send_message_payload(data)
    except ValueError as e:
        return HttpResponseBadRequest(e)

    destinations = collect_destinations(recipients=data["to"], number_type=None)
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

    try:
        audit_log_service._commit_to_audit_log(
            message=create_api_commit_message_from_request(
                request=request,
                operation=Operation.CREATE.value,
                object_ids=[str(log.pk)],
                new_objects=[log],
            )
        )
    except Exception as e:
        logger.error(f"Committing to audit log failed: {e}")

    return Response(DeliveryLogSerializer(log).data)


@extend_schema(
    parameters=[
        OpenApiParameter(
            "id", OpenApiTypes.INT, OpenApiParameter.PATH, description="Delivery log ID"
        )
    ],
    responses={200: DeliveryLogSerializer},
    description="Retrieve a delivery log.",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_delivery_log(request, id):
    user = request.user
    try:
        log = user.delivery_logs.get(id=id)
    except DeliveryLog.DoesNotExist:
        return Response(status=404, data={"error": f" Message ID: {id} does not exist"})

    audit_log_service._commit_to_audit_log(
        message=create_api_commit_message_from_request(
            request=request,
            operation=Operation.READ.value,
            object_ids=[str(id)],
            old_objects=[log],
        )
    )

    data = DeliveryLogSerializer(log).data
    return Response(data=data)


@extend_schema(
    parameters=[
        OpenApiParameter(
            "id", OpenApiTypes.INT, OpenApiParameter.PATH, description="Delivery log ID"
        )
    ],
    description="Webhook for delivery log updates.",
)
@api_view(["POST"])
# TODO: We probably need some basic authentication before writing data
def delivery_log_webhook(request, id):
    try:
        log = DeliveryLog.objects.get(id=id)
    except DeliveryLog.DoesNotExist:
        return Response(status=404, data={"error": f" Message ID: {id} does not exist"})
    log.update_report(request.data)

    audit_log_service._commit_to_audit_log(
        message=create_api_commit_message_from_request(
            request=request,
            operation=Operation.UPDATE.value,
            object_ids=[str(id)],
            new_objects=[log],
        )
    )

    return Response(status=200)
