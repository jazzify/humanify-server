from django.urls import path

from apps.places.apis import PlaceAPI, PlaceImageAPI

urlpatterns = [
    path("", PlaceAPI.as_view(), name="place-create-list"),
    path(
        "<str:place_id>/images/",
        PlaceImageAPI.as_view(),
        name="place-image-create",
    ),
]
