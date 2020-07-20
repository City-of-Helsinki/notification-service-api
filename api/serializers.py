from api.models import DeliveryLog
from rest_framework import serializers


class DeliveryLogSerializer(serializers.ModelSerializer):
    report = serializers.JSONField()

    class Meta:
        model = DeliveryLog
        fields = ("id", "report")
