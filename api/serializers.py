from api.models import DeliveryLog
from rest_framework import serializers


class DeliveryLogSerializer(serializers.ModelSerializer):
    payload = serializers.JSONField()

    class Meta:
        model = DeliveryLog
        fields = ("id", "payload")
