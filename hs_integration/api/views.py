from drf_spectacular.utils import OpenApiExample, extend_schema
from hubspot.crm.associations import BatchInputPublicAssociation
from hubspot.crm.associations.exceptions import ApiException as AssociationException
from hubspot.crm.contacts import (
    SimplePublicObjectInputForCreate as ContactObjectForCreate,
)
from hubspot.crm.contacts.exceptions import ApiException as ContactApiException
from hubspot.crm.deals import SimplePublicObjectInputForCreate as DealObjectForCreate
from hubspot.crm.deals.exceptions import ApiException as DealApiException
from rest_framework import status, views
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from config.settings import PERSONAL_ID
from hs_integration.apps import HsIntegrationConfig as hs

from .serializers import (
    AssociateContactWDealSerializer,
    ContactSerializer,
    DealSerializer,
)


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
            serializer.validated_data["hubspot_owner_id"] = PERSONAL_ID
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


class AssociateContactWDealAPIView(views.APIView):
    @extend_schema(
        request=AssociateContactWDealSerializer,
        responses={
            201: OpenApiExample(
                "Successful Response",
                value={"message": "Contact associated with deal successfully"},
            )
        },
        description="Associate an existing contact with a deal in HubSpot",
        summary="Associate Contact with a deal in HubSpot",
        tags=["Association"],
    )
    def post(self, request):
        # Validate input data
        serializer = AssociateContactWDealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # We utilize v3 api which contains only batch associations
            batch_input_public_association = BatchInputPublicAssociation(
                inputs=[
                    {
                        "from": {"id": serializer.validated_data["contact_id"]},
                        "to": {"id": serializer.validated_data["deal_id"]},
                        "type": "contact_to_deal",
                    }
                ]
            )
            # Associate contact with a deal
            hs.association_api.create(
                from_object_type="contact",
                to_object_type="deal",
                batch_input_public_association=batch_input_public_association,
            )
        except AssociationException as e:
            return Response(
                {"error": f"Error associating contact with deal: {e.reason}"},
                status=e.status,
            )

        return Response(
            {
                "message": "Contact associated with deal successfully",
            },
            status=status.HTTP_200_OK,
        )


class HubSpotContactsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    page_query_param = "after"


class ListContactsAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        paginator = HubSpotContactsPagination()
        page = request.query_params.get(paginator.page_query_param, 1)
        limit = paginator.get_page_size(request)

        try:
            response = hs.contacts_api.get_page(
                limit=limit, after=(int(page) - 1) * limit
            )
            contacts = [contact.to_dict() for contact in response.results]
            paginated_data = paginator.paginate_queryset(contacts, request)
        except ContactApiException as e:
            return Response(
                {"error": f"Error retrieving contacts: {e.reason}"},
                status=e.status,
            )

        return paginator.get_paginated_response(paginated_data)
