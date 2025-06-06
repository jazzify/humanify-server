from django.urls import path

from apps.image_processing.api.apis import ImageProcessingCreateListApi

urlpatterns = [
    path(
        "", ImageProcessingCreateListApi.as_view(), name="image-processing-create-list"
    ),
]
