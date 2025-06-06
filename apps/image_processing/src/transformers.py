from abc import ABC, abstractmethod
from concurrent import futures as cfutures
from typing import Callable, Generator

from PIL import Image as PImage

from apps.image_processing.src.constants import InternalTransformerNames
from apps.image_processing.src.data_models import (
    InternalImageTransformation,
    InternalImageTransformationDefinition,
    InternalImageTransformationResult,
)


class BaseImageTransformer(ABC):
    name: str

    def __init__(
        self,
        transformations: list[InternalImageTransformationDefinition],
    ) -> None:
        self.transformations_data = transformations

    @abstractmethod
    def transform(
        self, image: PImage.Image
    ) -> list[InternalImageTransformationResult]: ...


class ImageMultiProcessTransformer(BaseImageTransformer):
    name = InternalTransformerNames.MULTIPROCESS

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
    name = InternalTransformerNames.SEQUENTIAL

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
    name = InternalTransformerNames.CHAIN

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
            self._transform(image, list(reversed(self.transformations_data)))
        )
        return [
            InternalImageTransformationResult(
                identifier=identifier, image=transformed_image
            )
        ]
