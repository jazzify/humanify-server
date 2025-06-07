from django.urls import path

from apps.image_processing_api.apis import (
    ImageProcessingCreateListApi,
    ImageProcessTransformApi,
)

urlpatterns = [
    path(
        "", ImageProcessingCreateListApi.as_view(), name="image-processing-create-list"
    ),
    path(
        "transform/",
        ImageProcessTransformApi.as_view(),
        name="image-transform",
    ),
]
