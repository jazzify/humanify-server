from typing import Generator

from PIL import Image as PImage

from apps.image_processing.core.transformers.base import (
    InternalImageTransformationDefinition,
    InternalImageTransformationResult,
)
from apps.image_processing.models import TransformationBatch

from .base import BaseImageTransformer


class ImageChainTransformer(BaseImageTransformer):
    """Applies a sequence of image transformations in a chain-like manner."""

    name = TransformationBatch.CHAIN

    def _internal_transform(
        self,
        image: PImage.Image,
        transformations: list[InternalImageTransformationDefinition],
    ) -> Generator[PImage.Image, None, None]:
        """
        Recursively applies transformations to the image.
        """
        if len(transformations) == 1:
            transformation = transformations[0].transformation(
                image,
                transformations[0].filters,
            )
            yield transformation.image_transformed

        for transform_data in transformations:
            _image = transform_data.transformation(
                image,
                transform_data.filters,
            )
            yield from self._internal_transform(
                _image.image_transformed,
                transformations=transformations[1:],
            )

    def _transform(
        self, image: PImage.Image
    ) -> list[InternalImageTransformationResult]:
        """
        Transforms an image using a defined sequence of transformations.
        """
        all_identifiers = [
            transform_data.identifier for transform_data in self.transformations_data
        ]
        identifier = "-".join(all_identifiers)

        # Optimize transformation order based on resource consumption while maintaining
        # the required order of certain transformations.
        # For example, applying the black and white filter to a cropped image will consume less resources.
        final_image = next(self._internal_transform(image, self.transformations_data))
        transformations_applied = [
            InternalImageTransformationResult(
                identifier=identifier,
                transformation_name=self.transformations_data[-1].transformation.name,
                applied_filters=self.transformations_data[-1].filters,
                image=final_image,
            )
        ]
        return transformations_applied
