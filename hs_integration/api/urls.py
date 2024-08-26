from django.urls import path

from .views import CreateContactAPIView, CreateDealAPIView

urlpatterns = [
    path(
        "contact/",
        CreateContactAPIView.as_view(),
        name="create-contact",
    ),
    path("deal/", CreateDealAPIView.as_view(), name="create-deal"),
]
