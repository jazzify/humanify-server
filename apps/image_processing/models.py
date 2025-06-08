import uuid

from django.db import models

from apps.common.models import BaseModel
from apps.users.models import BaseUser


class ProcessingImage(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(BaseUser, on_delete=models.PROTECT, related_name="images")
    file = models.ImageField(upload_to="image_processing/api/")

    class Meta:
        ordering = ["-updated_at"]


class TransformationBatch(BaseModel):
    MULTIPROCESS = "multiprocess"
    SEQUENTIAL = "sequential"
    CHAIN = "chain"
    TRANSFORMER_CHOICES = {
        MULTIPROCESS: MULTIPROCESS,
        SEQUENTIAL: SEQUENTIAL,
        CHAIN: CHAIN,
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    input_image = models.ForeignKey(
        ProcessingImage, on_delete=models.PROTECT, related_name="transformation_batches"
    )
    transformer = models.CharField(max_length=100, choices=TRANSFORMER_CHOICES)


class ImageTransformation(BaseModel):
    THUMBNAIL = "thumbnail"
    BLUR = "blur"
    BLACK_AND_WHITE = "black_and_white"
    IMAGE_TRANSFORMATION_CHOICES = {
        THUMBNAIL: THUMBNAIL,
        BLUR: BLUR,
        BLACK_AND_WHITE: BLACK_AND_WHITE,
    }

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
    identifier = models.CharField(max_length=100)
    file = models.ImageField(upload_to="image_processing/processed/")
    transformation = models.OneToOneField(
        ImageTransformation, on_delete=models.PROTECT, related_name="processed_image"
    )

    @property
    def url(self) -> str:
        return self.file.url  # type: ignore[no-any-return]
