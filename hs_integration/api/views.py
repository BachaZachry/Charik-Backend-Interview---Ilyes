from urllib.parse import urlencode

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
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
        description="Associate an existing contact created by the owner with a deal in HubSpot",
        summary="Associate Contact with a deal in HubSpot",
        tags=["Association"],
    )
    def post(self, request):
        # Validate input data
        serializer = AssociateContactWDealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Check if the contact is created by the same hubspot_owner
            contact_id = serializer.validated_data["contact_id"]
            contact = hs.contacts_api.get_by_id(
                contact_id=contact_id, properties=["hubspot_owner_id"]
            )
            if contact.properties.get("hubspot_owner_id") != PERSONAL_ID:
                return Response(
                    {"error": "Contact is not created by the same owner."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # We utilize v3 api which contains only batch associations
            batch_input_public_association = BatchInputPublicAssociation(
                inputs=[
                    {
                        "from": {"id": contact_id},
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
    page_size = 3
    page_size_query_param = "page_size"


class ListContactsAPIView(views.APIView):
    @extend_schema(
        summary="List Contacts",
        description="Retrieve a paginated list of contacts from HubSpot along with any associations they have.",
        parameters=[
            OpenApiParameter(
                name="after",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Pagination cursor to fetch results after a specific contact",
                required=False,
            ),
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Successful Response",
                value={
                    "results": [
                        {
                            "id": "1",
                            "created_at": "2024-08-26T15:32:48.871000Z",
                            "archived": "false",
                            "archived_at": "null",
                            "properties_with_history": "null",
                            "properties": {
                                "email": "john@example.com",
                                "firstname": "John",
                                "hs_object_id": "1",
                                "lastname": "Doe",
                                "hubspot_owner_id": "id",
                            },
                            "updated_at": "2024-08-26T15:34:38.107000Z",
                            "associations": {
                                "deals": {
                                    "paging": "null",
                                    "results": [
                                        {"id": "deal1", "type": "contact_to_deal"},
                                        {"id": "deal2", "type": "contact_to_deal"},
                                    ],
                                },
                            },
                        }
                    ],
                    "paging": {
                        "next": {
                            "link": "http://localhost:8000/contact/list/?after=1000",
                            "after": "1000",
                        }
                    },
                },
                response_only=True,
            ),
            OpenApiExample(
                "Error Response",
                value={
                    "error": "Error retrieving contacts: API rate limit exceeded",
                },
                response_only=True,
                status_codes=["400"],
            ),
        ],
        tags=["Contacts"],
    )
    def get(self, request):
        after = request.query_params.get("after", 0)
        try:
            # Get all contacts
            response = hs.contacts_api.get_page(
                limit=10,
                after=after,
                associations=["deals"],
                properties=["hubspot_owner_id", "email", "firstname", "lastname"],
            )

            # Filter to get contacts owned by the user
            # And get the correct format
            contacts = [
                contact.to_dict()
                for contact in response.results
                if contact.properties.get("hubspot_owner_id") == PERSONAL_ID
            ]
        except ContactApiException as e:
            return Response(
                {"error": f"Error retrieving contacts: {e.reason}"},
                status=e.status,
            )

        response_data = {"results": contacts}
        # Implement pagination in order to check next pages if there are any
        if response.paging:
            next_page_url = "http://localhost:8000/contact/list/"
            next_page_params = urlencode({"after": response.paging.next.after})
            response_data["paging"] = {
                "next": {
                    "link": f"{next_page_url}?{next_page_params}",
                    "after": response.paging.next.after,
                }
            }

        return Response(response_data, status=status.HTTP_200_OK)
