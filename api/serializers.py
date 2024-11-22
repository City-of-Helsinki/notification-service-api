from rest_framework import serializers

from api.models import DeliveryLog


class DeliveryLogSerializer(serializers.ModelSerializer):
    report = serializers.JSONField()

    class Meta:
        model = DeliveryLog
        fields = ("id", "report")


class DestinationSerializer(serializers.Serializer):
    destination = serializers.CharField()
    format = serializers.ChoiceField(
        choices=["MOBILE"]
    )  # You might have other formats in the future


class SendMessagePayloadSerializer(serializers.Serializer):
    sender = serializers.CharField()
    to = DestinationSerializer(many=True)
    text = serializers.CharField()
