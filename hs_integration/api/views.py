from drf_spectacular.utils import OpenApiExample, extend_schema
from hubspot.crm.contacts import (
    SimplePublicObjectInputForCreate as ContactObjectForCreate,
)
from hubspot.crm.contacts.exceptions import ApiException as ContactApiException
from hubspot.crm.deals import SimplePublicObjectInputForCreate as DealObjectForCreate
from hubspot.crm.deals.exceptions import ApiException as DealApiException
from rest_framework import status, views
from rest_framework.response import Response

from hs_integration.apps import HsIntegrationConfig as hs

from .serializers import ContactSerializer, DealSerializer


class CreateContactAPIView(views.APIView):
    @extend_schema(
        request=ContactSerializer,
        responses={
            201: OpenApiExample(
                "Successful Response",
                value={"message": "Contact created successfully", "id": "1234"},
            )
        },
        description="Create a new contact in HubSpot",
        summary="Create HubSpot Contact",
        tags=["Contacts"],
    )
    def post(self, request):
        # Validate input data
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Setup contact properties object
            contact_object = ContactObjectForCreate(
                properties=serializer.validated_data
            )
            # Create a contact
            response = hs.contacts_api.create(
                simple_public_object_input_for_create=contact_object,
            )
        except ContactApiException as e:
            return Response(
                {"error": f"Error creating a contact: {e.reason}"},
                status=e.status,
            )

        return Response(
            {"message": "Contact created successfully.", "id": response.id},
            status=status.HTTP_201_CREATED,
        )


class CreateDealAPIView(views.APIView):
    @extend_schema(
        request=DealSerializer,
        responses={
            201: OpenApiExample(
                "Successful Response",
                value={"message": "Deal created successfully", "id": "1234"},
            )
        },
        description="Create a new deal in HubSpot",
        summary="Create HubSpot Deal",
        tags=["Deals"],
    )
    def post(self, request):
        # Validate input data
        serializer = DealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Setup deal properties object
            serializer.validated_data["dealname"] = "Deal - Bacha Ilyes"
            serializer.validated_data["amount"] = str(
                serializer.validated_data["amount"]
            )
            contact_object = DealObjectForCreate(properties=serializer.validated_data)
            # Create a deal
            response = hs.deals_api.create(
                simple_public_object_input_for_create=contact_object,
            )
        except DealApiException as e:
            return Response(
                {"error": f"Error creating a deal: {e.reason}"},
                status=e.status,
            )

        return Response(
            {"message": "Deal created successfully.", "id": response.id},
            status=status.HTTP_201_CREATED,
        )
