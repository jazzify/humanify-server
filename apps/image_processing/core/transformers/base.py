from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from io import BytesIO
from typing import Type

from django.core.files.base import ContentFile
from PIL import Image as PImage

from apps.image_processing.core.transformations.base import (
    ExternalTransformationFilters,
    InternalImageTransformation,
)
from apps.image_processing.models import (
    ImageTransformation,
    ProcessedImage,
    TransformationBatch,
)


@dataclass
class InternalImageTransformationDefinition:
    identifier: str
    transformation: Type[InternalImageTransformation]
    filters: ExternalTransformationFilters


@dataclass
class ExternalImageTransformationDefinition:
    identifier: str
    transformation: str
    filters: ExternalTransformationFilters | None = None


@dataclass
class InternalImageTransformationResult:
    identifier: str
    transformation_name: str
    applied_filters: ExternalTransformationFilters
    image: PImage.Image


class BaseImageTransformer(ABC):
    name: str

    def __init__(
        self,
        transformations: list[InternalImageTransformationDefinition],
    ) -> None:
        self.transformations_data = transformations

    @abstractmethod
    def _transform(
        self, image: PImage.Image
    ) -> list[InternalImageTransformationResult]: ...

    def transform(
        self, image: PImage.Image, transformation_batch: TransformationBatch
    ) -> list[InternalImageTransformationResult]:
        transformations_applied = self._transform(image)
        image_transformations = []
        processed_images = []
        for transform_data in transformations_applied:
            image_transformation = ImageTransformation(
                identifier=transform_data.identifier,
                transformation=transform_data.transformation_name,
                filters=asdict(transform_data.applied_filters),
                batch=transformation_batch,
            )
            buffer = BytesIO()
            transform_data.image.save(buffer, format="png")
            processed = ProcessedImage(
                identifier=transform_data.identifier,
                file=ContentFile(
                    buffer.getvalue(), name=f"{transform_data.identifier}.png"
                ),
                transformation=image_transformation,
            )
            processed_images.append(processed)
            image_transformations.append(image_transformation)
        ImageTransformation.objects.bulk_create(image_transformations)
        ProcessedImage.objects.bulk_create(processed_images)

        return transformations_applied
