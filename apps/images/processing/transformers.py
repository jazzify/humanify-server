from abc import ABC, abstractmethod
from concurrent import futures as cfutures
from typing import Callable

from PIL import Image as PImage

from apps.images.processing.data_models import (
    ImageTransformationDataClass,
    ImageTransformedDataClass,
)
from apps.images.processing.transformations import ImageTransformationCallable


class BaseImageTransformer(ABC):
    def __init__(self, transformations: list[ImageTransformationDataClass]) -> None:
        self.transformations_data = transformations

    @abstractmethod
    def transform(self, image: PImage.Image) -> list[ImageTransformedDataClass]: ...


class ImageMultiProcessTransformer(BaseImageTransformer):
    def __init__(self, transformations: list[ImageTransformationDataClass]) -> None:
        super().__init__(transformations)
        self._transformations_applied: list[ImageTransformedDataClass] = []

    def _callback_process(
        self, identifier: str
    ) -> Callable[[cfutures.Future[ImageTransformationCallable]], None]:
        def callback(future: cfutures.Future[ImageTransformationCallable]) -> None:
            self._transformations_applied.append(
                ImageTransformedDataClass(
                    identifier=identifier, image=future.result().image_transformed
                )
            )

        return callback

    def transform(self, image: PImage.Image) -> list[ImageTransformedDataClass]:
        with cfutures.ProcessPoolExecutor() as executor:
            for transform_data in self.transformations_data:
                image_copy = image.copy()
                future: cfutures.Future[ImageTransformationCallable] = executor.submit(
                    transform_data.transformation,
                    image_copy,
                    transform_data.filters,
                )
                future.add_done_callback(
                    self._callback_process(transform_data.identifier)
                )
        return self._transformations_applied


class ImageSequentialTransformer(BaseImageTransformer):
    def transform(self, image: PImage.Image) -> list[ImageTransformedDataClass]:
        transformations = []
        for transform_data in self.transformations_data:
            transformation = transform_data.transformation(
                image,
                transform_data.filters,
            )
            transformations.append(
                ImageTransformedDataClass(
                    identifier=transform_data.identifier,
                    image=transformation.image_transformed,
                )
            )
        return transformations
