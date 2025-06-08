from dataclasses import asdict
from io import BytesIO
from typing import Generator
from uuid import UUID

from django.core.files.base import ContentFile
from PIL import Image as PImage

from apps.image_processing.core.transformers.base import (
    InternalImageTransformationDefinition,
    InternalImageTransformationResult,
)
from apps.image_processing.models import (
    ImageTransformation,
    ProcessedImage,
    TransformationBatch,
)

from .base import BaseImageTransformer


class ImageChainTransformer(BaseImageTransformer):
    name = TransformationBatch.CHAIN

    def _transform(
        self,
        image: PImage.Image,
        transformations: list[InternalImageTransformationDefinition],
        batch_id: UUID,
    ) -> Generator[PImage.Image]:
        if len(transformations) == 1:
            image_transformation = ImageTransformation.objects.create(
                identifier=transformations[0].identifier,
                transformation=transformations[0].transformation.name,
                filters=asdict(transformations[0].filters),
                batch_id=batch_id,
            )
            transformation = transformations[0].transformation(
                image,
                transformations[0].filters,
            )
            buffer = BytesIO()
            transformation.image_transformed.save(buffer, format="png")
            ProcessedImage.objects.create(
                identifier=transformations[0].identifier,
                file=ContentFile(
                    buffer.getvalue(), name=f"{transformations[0].identifier}.png"
                ),
                transformation=image_transformation,
            )
            yield transformation.image_transformed

        for transform_data in transformations:
            _image = transform_data.transformation(
                image,
                transform_data.filters,
            )
            image_transformation = ImageTransformation.objects.create(
                identifier=transform_data.identifier,
                transformation=transform_data.transformation.name,
                filters=asdict(transform_data.filters),
                batch_id=batch_id,
            )
            buffer = BytesIO()
            _image.image_transformed.save(buffer, format="png")
            ProcessedImage.objects.create(
                identifier=transform_data.identifier,
                file=ContentFile(
                    buffer.getvalue(), name=f"{transform_data.identifier}.png"
                ),
                transformation=image_transformation,
            )
            yield from self._transform(
                _image.image_transformed,
                transformations=transformations[1:],
                batch_id=batch_id,
            )

    def transform(
        self, image: PImage.Image, transformation_batch: TransformationBatch
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
        transformed_image = next(
            self._transform(image, self.transformations_data, transformation_batch.id)
        )

        return [
            InternalImageTransformationResult(
                identifier=identifier, image=transformed_image
            )
        ]
