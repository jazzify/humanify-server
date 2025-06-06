import uuid

from django.db import models

from apps.common.models import BaseModel
from apps.image_processing.api.constants import ImageTransformations
from apps.image_processing.src.constants import InternalTransformerNames
from apps.users.models import BaseUser


class Image(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(BaseUser, on_delete=models.PROTECT, related_name="images")
    file = models.ImageField(upload_to="image_processing/api/")

    class Meta:
        ordering = ["-updated_at"]

    @property
    def url(self) -> str:
        return self.file.url  # type: ignore[no-any-return]


class TransformationBatch(BaseModel):
    TRANSFORMER_CHOICES = [
        (name.value, name.value) for name in InternalTransformerNames
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    input_image = models.OneToOneField(
        Image, on_delete=models.PROTECT, related_name="transformation_batches"
    )
    transformer = models.CharField(max_length=100, choices=TRANSFORMER_CHOICES)


class ImageTransformation(BaseModel):
    IMAGE_TRANSFORMATION_CHOICES = [
        (name.value, name.value) for name in ImageTransformations
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    identifier = models.CharField(max_length=100)
    transformation = models.CharField(
        max_length=100, choices=IMAGE_TRANSFORMATION_CHOICES
    )
    filters = models.JSONField(null=True, blank=True)
    batch = models.ForeignKey(
        TransformationBatch, on_delete=models.PROTECT, null=True, blank=True
    )


class ProcessedImage(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    identifier = models.CharField(max_length=255)
    file = models.ImageField(upload_to="image_processing/processed/")
    transformation = models.ForeignKey(
        ImageTransformation, on_delete=models.CASCADE, related_name="processed_images"
    )

    @property
    def url(self) -> str:
        return self.file.url  # type: ignore[no-any-return]
