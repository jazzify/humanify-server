from typing import Generator

from PIL import Image as PImage

from apps.image_processing.core.transformers.base import (
    InternalImageTransformationDefinition,
    InternalImageTransformationResult,
)
from apps.image_processing.models import TransformationBatch

from .base import BaseImageTransformer


class ImageChainTransformer(BaseImageTransformer):
    name = TransformationBatch.CHAIN

    def _internal_transform(
        self,
        image: PImage.Image,
        transformations: list[InternalImageTransformationDefinition],
    ) -> Generator[PImage.Image]:
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
        all_identifiers = [
            transform_data.identifier for transform_data in self.transformations_data
        ]
        identifier = "-".join(all_identifiers)

        # TODO: We can make this more "efficient" by understanding the
        # wanted output image final state and appling the transformations
        # in the correct order, for example, instead of applying (Black and White -> Crop),
        # we can do (Crop -> Black and White) the output image should be the same but
        # applying the black and white filter to a cropped image will consume less resources.
        # however, the order of the transformations is important, since there are
        # some transformations that MUST be applied first.
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
