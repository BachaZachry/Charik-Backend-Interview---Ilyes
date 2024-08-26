from rest_framework import serializers


class ContactSerializer(serializers.Serializer):
    email = serializers.EmailField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()
