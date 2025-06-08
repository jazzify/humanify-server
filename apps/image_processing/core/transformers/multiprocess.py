from concurrent import futures as cfutures
from dataclasses import asdict
from io import BytesIO
from typing import Callable

from django.core.files.base import ContentFile
from PIL import Image as PImage

from apps.image_processing.core.transformations.base import InternalImageTransformation
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


class ImageMultiProcessTransformer(BaseImageTransformer):
    name = TransformationBatch.MULTIPROCESS

    def __init__(
        self, transformations: list[InternalImageTransformationDefinition]
    ) -> None:
        super().__init__(transformations)
        self._transformations_applied: list[InternalImageTransformationResult] = []

    def _callback_process(
        self, identifier: str, transformation: ImageTransformation
    ) -> Callable[[cfutures.Future[InternalImageTransformation]], None]:
        def callback(future: cfutures.Future[InternalImageTransformation]) -> None:
            transformed_image = future.result().image_transformed
            self._transformations_applied.append(
                InternalImageTransformationResult(
                    identifier=identifier, image=transformed_image
                )
            )
            buffer = BytesIO()
            transformed_image.save(buffer, format="png")
            processed = ProcessedImage(
                identifier=identifier,
                file=ContentFile(buffer.getvalue(), name=f"{identifier}.png"),
                transformation=transformation,
            )
            processed.save()

        return callback

    def transform(
        self, image: PImage.Image, transformation_batch: TransformationBatch
    ) -> list[InternalImageTransformationResult]:
        with cfutures.ProcessPoolExecutor() as executor:
            for transform_data in self.transformations_data:
                image_copy = image.copy()
                future: cfutures.Future[InternalImageTransformation] = executor.submit(
                    transform_data.transformation,
                    image_copy,
                    transform_data.filters,
                )
                image_transformation = ImageTransformation.objects.create(
                    identifier=transform_data.identifier,
                    transformation=transform_data.transformation.name,
                    filters=asdict(transform_data.filters),
                    batch=transformation_batch,
                )
                future.add_done_callback(
                    self._callback_process(
                        transform_data.identifier, image_transformation
                    )
                )
        return self._transformations_applied
