import uuid
from abc import ABC, abstractmethod
from concurrent import futures as cfutures
from typing import Callable, Generator

from PIL import Image as PImage

from apps.images.processing.data_models import (
    InternalImageTransformation,
    InternalImageTransformationDefinition,
    InternalImageTransformationResult,
)


class BaseImageTransformer(ABC):
    def __init__(
        self, transformations: list[InternalImageTransformationDefinition]
    ) -> None:
        self.transformations_data = transformations

    @abstractmethod
    def transform(
        self, image: PImage.Image
    ) -> list[InternalImageTransformationResult]: ...


class ImageMultiProcessTransformer(BaseImageTransformer):
    def __init__(
        self, transformations: list[InternalImageTransformationDefinition]
    ) -> None:
        super().__init__(transformations)
        self._transformations_applied: list[InternalImageTransformationResult] = []

    def _callback_process(
        self, identifier: str
    ) -> Callable[[cfutures.Future[InternalImageTransformation]], None]:
        def callback(future: cfutures.Future[InternalImageTransformation]) -> None:
            self._transformations_applied.append(
                InternalImageTransformationResult(
                    identifier=identifier, image=future.result().image_transformed
                )
            )

        return callback

    def transform(self, image: PImage.Image) -> list[InternalImageTransformationResult]:
        with cfutures.ProcessPoolExecutor() as executor:
            for transform_data in self.transformations_data:
                image_copy = image.copy()
                future: cfutures.Future[InternalImageTransformation] = executor.submit(
                    transform_data.transformation,
                    image_copy,
                    transform_data.filters,
                )
                future.add_done_callback(
                    self._callback_process(transform_data.identifier)
                )
        return self._transformations_applied


class ImageSequentialTransformer(BaseImageTransformer):
    def transform(self, image: PImage.Image) -> list[InternalImageTransformationResult]:
        transformations = []
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
        return transformations


class ImageChainTransformer(BaseImageTransformer):
    def _transform(
        self,
        image: PImage.Image,
        transformations: list[InternalImageTransformationDefinition],
    ) -> Generator[PImage.Image]:
        if len(transformations) == 1:
            yield (
                transformations[0]
                .transformation(
                    image,
                    transformations[0].filters,
                )
                .image_transformed
            )

        for transform_data in transformations:
            _image = transform_data.transformation(
                image,
                transform_data.filters,
            )
            yield from self._transform(
                _image.image_transformed, transformations=transformations[1:]
            )

    def transform(self, image: PImage.Image) -> list[InternalImageTransformationResult]:
        identifier = uuid.uuid4()
        transformed_image = next(
            self._transform(image, list(reversed(self.transformations_data)))
        )
        return [
            InternalImageTransformationResult(
                identifier=str(identifier), image=transformed_image
            )
        ]
