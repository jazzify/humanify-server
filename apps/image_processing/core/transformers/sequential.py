from dataclasses import asdict
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image as PImage

from apps.image_processing.core.transformers.base import (
    InternalImageTransformationResult,
)
from apps.image_processing.models import (
    ImageTransformation,
    ProcessedImage,
    TransformationBatch,
)

from .base import BaseImageTransformer


class ImageSequentialTransformer(BaseImageTransformer):
    name = TransformationBatch.SEQUENTIAL

    def transform(
        self, image: PImage.Image, transformation_batch: TransformationBatch
    ) -> list[
        InternalImageTransformationResult
    ]:  # TODO: change return to model result struct
        # response = {}
        transformations = []
        image_transformations = []
        processed_images = []
        for transform_data in self.transformations_data:
            transformation = transform_data.transformation(
                image,
                transform_data.filters,
            )
            transformations.append(
                InternalImageTransformationResult(
                    identifier=transform_data.identifier,
                    image=transformation.image_transformed,
                )
            )
            image_transformation = ImageTransformation(
                identifier=transform_data.identifier,
                transformation=transform_data.transformation.name,
                filters=asdict(transform_data.filters),
                batch=transformation_batch,
            )
            buffer = BytesIO()
            transformation.image_transformed.save(buffer, format="png")
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
        return transformations
