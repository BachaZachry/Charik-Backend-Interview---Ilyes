from django.urls import path

from .views import CreateContactAPIView

urlpatterns = [
    path(
        "contact/",
        CreateContactAPIView.as_view(),
        name="create-contact",
    ),
]
