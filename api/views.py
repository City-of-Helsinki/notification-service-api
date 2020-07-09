import json

from api.models import DeliveryLog
from api.serializers import DeliveryLogSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_message(request):
    content = {"message": "Welcome to the BookStore!"}
    return Response(content)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_delivery_log(request, uuid):
    user = request.user
    try:
        log = user.delivery_logs.get(id=uuid)
        data = DeliveryLogSerializer(log).data
        data["payload"] = json.loads(log.payload)
        return Response(data)
    except DeliveryLog.DoesNotExist:
        return Response(
            status=404, data={"error": f" Message ID: {uuid} does not " f"exist"}
        )


@api_view(["GET"])
# TODO: Need authentication for deliver log webhook (ask Quriiri)
def delivery_log_webhook(request, uuid):
    pass
