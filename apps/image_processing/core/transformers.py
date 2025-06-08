from abc import ABC, abstractmethod
from concurrent import futures as cfutures
from dataclasses import asdict
from io import BytesIO
from typing import Callable, Generator
from uuid import UUID

from django.core.files.base import ContentFile
from PIL import Image as PImage

from apps.image_processing.constants import InternalTransformerNames
from apps.image_processing.data_models import (
    InternalImageTransformation,
    InternalImageTransformationDefinition,
    InternalImageTransformationResult,
)
from apps.image_processing.models import (
    ImageTransformation,
    ProcessedImage,
    TransformationBatch,
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
        self, image: PImage.Image, transformation_batch: TransformationBatch
    ) -> list[InternalImageTransformationResult]: ...


class ImageMultiProcessTransformer(BaseImageTransformer):
    name = InternalTransformerNames.MULTIPROCESS

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
                    transform_data.filters.to_internal(),
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


class ImageSequentialTransformer(BaseImageTransformer):
    name = InternalTransformerNames.SEQUENTIAL

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
                transform_data.filters.to_internal(),
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


class ImageChainTransformer(BaseImageTransformer):
    name = InternalTransformerNames.CHAIN

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
                transformations[0].filters.to_internal(),
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
                transform_data.filters.to_internal(),
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
