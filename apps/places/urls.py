from django.urls import path

from apps.places.apis import CreateListPlaceAPIView

urlpatterns = [
    path("", CreateListPlaceAPIView.as_view(), name="place-create-list"),
]
