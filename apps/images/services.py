import logging
import uuid
from concurrent import futures as cfutures
from pathlib import Path
from typing import Callable, Type

from django.conf import settings
from PIL import Image as PImage

from apps.images.constants import (
    TRANSFORMATIONS_MULTIPROCESS_TRESHOLD,
    ImageTransformations,
)
from apps.images.data_models import (
    ImageTransformationCallableDataClass,
    ImageTransformationDataClass,
)
from apps.images.processing.abstract_classes import ImageTransformationCallable
from apps.images.processing.transformations import (
    TransformationBlackAndWhite,
    TransformationBlur,
    TransformationThumbnail,
)

logger = logging.getLogger(__name__)


class ImageTransformationService:
    def __init__(
        self,
        image_path: str,
        root_folder: str,
        parent_folder: str,
        transformations: list[ImageTransformationDataClass],
    ) -> None:
        self._TRANSFORMATIONS_MAPPER: dict[
            ImageTransformations, Type[ImageTransformationCallable]
        ] = {
            ImageTransformations.THUMBNAIL: TransformationThumbnail,
            ImageTransformations.BLACK_AND_WHITE: TransformationBlackAndWhite,
            ImageTransformations.BLUR: TransformationBlur,
        }
        self.image_path = image_path
        self.root_folder = root_folder
        self.parent_folder = parent_folder
        self.transformations = transformations
        self._transformation_callables: list[ImageTransformationCallableDataClass] = []
        self._is_multiprocess_execution = (
            len(self._transformation_callables) < TRANSFORMATIONS_MULTIPROCESS_TRESHOLD
        )

        for transformation in self.transformations:
            if transformation.name not in self._TRANSFORMATIONS_MAPPER.keys():
                logger.error(f"Invalid/unsupported transformation: {transformation}")
                continue

            file_relative_path = self._create_transformation_folders(
                transformation.name
            )

            file_name = f"{file_relative_path}/{uuid.uuid4()}.png"
            self._transformation_callables.append(
                ImageTransformationCallableDataClass(
                    transform=self._TRANSFORMATIONS_MAPPER[transformation.name],
                    filters=transformation.filters,
                    file_relative_path=file_name,
                )
            )

    def _save(self, image: PImage.Image, file_name: str) -> None:
        image.save(file_name)
        logger.info(f"Saved image: {file_name}")

    def _callback_save(
        self, file_name: str
    ) -> Callable[[cfutures.Future[ImageTransformationCallable]], None]:
        def callback(future: cfutures.Future[ImageTransformationCallable]) -> None:
            self._save(future.result().image_transformed, file_name)

        return callback

    def _create_transformation_folders(
        self, transformation: ImageTransformations
    ) -> str:
        processed_folder = (
            f"{settings.MEDIA_ROOT}/processed/{self.root_folder}/{self.parent_folder}"
        )
        transformation_folder = f"{processed_folder}/{transformation}"
        Path(transformation_folder).mkdir(parents=True, exist_ok=True)
        return transformation_folder

    def apply_transformations(self) -> None:
        if len(self._transformation_callables) == 0:
            return
        logger.info(f"Transforming image: {self.image_path}")

        with PImage.open(self.image_path) as image:
            if (
                len(self._transformation_callables)
                < TRANSFORMATIONS_MULTIPROCESS_TRESHOLD
            ):
                for transformation in self._transformation_callables:
                    transformator_callable = transformation.transform(
                        image=image,
                        filters=transformation.filters,
                    )
                    file_name = transformation.file_relative_path
                    self._save(transformator_callable.image_transformed, file_name)
            else:
                with cfutures.ProcessPoolExecutor(
                    max_workers=5, max_tasks_per_child=20
                ) as executor:
                    for transformation in self._transformation_callables:
                        future = executor.submit(
                            transformation.transform,
                            image,
                            transformation.filters,
                        )
                        future.add_done_callback(
                            self._callback_save(transformation.file_relative_path)
                        )
