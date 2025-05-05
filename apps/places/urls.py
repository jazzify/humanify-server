from django.urls import path

from apps.places.apis import CreateListPlaceAPI, CreatePlaceImageAPI

urlpatterns = [
    path("", CreateListPlaceAPI.as_view(), name="place-create-list"),
    path(
        "<str:place_id>/images/",
        CreatePlaceImageAPI.as_view(),
        name="place-image-create",
    ),
]
