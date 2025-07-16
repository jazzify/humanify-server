from PIL import Image as PImage

from apps.image_processing.core.transformers.base import (
    InternalImageTransformationResult,
)
from apps.image_processing.models import TransformationBatch

from .base import BaseImageTransformer


class ImageSequentialTransformer(BaseImageTransformer):
    """
    Applies a list of transformations in sequence order to the input image.
    """

    name = TransformationBatch.SEQUENTIAL

    def _transform(
        self, image: PImage.Image
    ) -> list[InternalImageTransformationResult]:
        """
        Applies transformations to an image in sequence order.
        """
        transformations = []
        for transform_data in self.transformations_data:
            transformation = transform_data.transformation(
                image,
                transform_data.filters,
            )
            transformations.append(
                InternalImageTransformationResult(
                    identifier=transform_data.identifier,
                    transformation_name=transform_data.transformation.name,
                    applied_filters=transform_data.filters,
                    image=transformation.image_transformed,
                )
            )
        return transformations
