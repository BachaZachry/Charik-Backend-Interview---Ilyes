from hubspot.crm.contacts import SimplePublicObjectInputForCreate
from hubspot.crm.contacts.exceptions import ApiException
from rest_framework import status, views
from rest_framework.response import Response

from hs_integration.apps import HsIntegrationConfig as hs

from .serializers import ContactSerializer


class CreateContactAPIView(views.APIView):
    def post(self, request):
        # Validate input data
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create contact
        try:
            # Setup contact properties object
            contact_object = SimplePublicObjectInputForCreate(
                properties=serializer.validated_data
            )
            # Create contact
            response = hs.contacts_api.create(
                simple_public_object_input_for_create=contact_object,
            )
        except ApiException as e:
            return Response(
                {"error": f"Error creating a contact: {e.reason}"},
                status=e.status,
            )

        return Response(
            {"message": "Contact created successfully.", "id": response.id},
            status=status.HTTP_201_CREATED,
        )
