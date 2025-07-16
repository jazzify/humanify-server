from concurrent import futures as cfutures
from typing import Callable

from PIL import Image as PImage

from apps.image_processing.core.transformations.base import (
    ExternalTransformationFilters,
    InternalImageTransformation,
)
from apps.image_processing.core.transformers.base import (
    InternalImageTransformationDefinition,
    InternalImageTransformationResult,
)
from apps.image_processing.models import TransformationBatch

from .base import BaseImageTransformer


class ImageMultiProcessTransformer(BaseImageTransformer):
    name = TransformationBatch.MULTIPROCESS

    def __init__(
        self, transformations: list[InternalImageTransformationDefinition]
    ) -> None:
        """
        Initializes the ImageMultiProcessTransformer with a list of transformations to be fullfilled in parallel.
        """
        super().__init__(transformations)
        self._transformations_applied: list[InternalImageTransformationResult] = []

    def _callback_process(
        self, identifier: str, filters: ExternalTransformationFilters
    ) -> Callable[[cfutures.Future[InternalImageTransformation]], None]:
        """
        Creates a callback function to handle the completion of a transformation.
        """

        def callback(future: cfutures.Future[InternalImageTransformation]) -> None:
            """
            Processes the result of a completed transformation and stores it.
            """
            transformed_image = future.result().image_transformed
            self._transformations_applied.append(
                InternalImageTransformationResult(
                    identifier=identifier,
                    image=transformed_image,
                    transformation_name=future.result().name,
                    applied_filters=filters,
                )
            )

        return callback

    def _transform(
        self, image: PImage.Image
    ) -> list[InternalImageTransformationResult]:
        """
        Applies transformations to an image using a process pool executor.
        """
        with cfutures.ProcessPoolExecutor() as executor:
            for transform_data in self.transformations_data:
                image_copy = image.copy()
                future: cfutures.Future[InternalImageTransformation] = executor.submit(
                    transform_data.transformation,
                    image_copy,
                    transform_data.filters,
                )
                future.add_done_callback(
                    self._callback_process(
                        transform_data.identifier,
                        transform_data.filters,
                    )
                )
        return self._transformations_applied
