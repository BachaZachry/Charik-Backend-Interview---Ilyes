from rest_framework import serializers


class ContactSerializer(serializers.Serializer):
    email = serializers.EmailField()
    firstname = serializers.CharField(required=False)
    lastname = serializers.CharField(required=False)
    website = serializers.CharField(required=False)
    company = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)


class DealSerializer(serializers.Serializer):
    pipeline = serializers.CharField()
    dealstage = serializers.CharField()
    amount = serializers.DecimalField(max_digits=100, decimal_places=2)
    closedate = serializers.DateTimeField()


class AssociateContactWDealSerializer(serializers.Serializer):
    deal_id = serializers.CharField()
    contact_id = serializers.CharField()
