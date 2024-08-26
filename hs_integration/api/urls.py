from django.urls import path

from .views import (
    AssociateContactWDealAPIView,
    CreateContactAPIView,
    CreateDealAPIView,
    ListContactsAPIView,
)

urlpatterns = [
    path(
        "contact/",
        CreateContactAPIView.as_view(),
        name="create-contact",
    ),
    path("deal/", CreateDealAPIView.as_view(), name="create-deal"),
    path(
        "associate/",
        AssociateContactWDealAPIView.as_view(),
        name="associate-contact-w-deal",
    ),
    path("contact/list/", ListContactsAPIView.as_view(), name="list-contacts"),
]
