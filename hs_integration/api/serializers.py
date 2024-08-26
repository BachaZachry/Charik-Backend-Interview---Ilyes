from rest_framework import serializers


class ContactSerializer(serializers.Serializer):
    email = serializers.EmailField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()


class DealSerializer(serializers.Serializer):
    pipeline = serializers.CharField()
    dealstage = serializers.CharField()
    amount = serializers.DecimalField(max_digits=100, decimal_places=2)
    closedate = serializers.DateTimeField()
