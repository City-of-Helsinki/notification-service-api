from rest_framework import serializers

from api.models import DeliveryLog


class DeliveryLogSerializer(serializers.ModelSerializer):
    report = serializers.JSONField()

    class Meta:
        model = DeliveryLog
        fields = ("id", "report")
