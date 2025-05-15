import logging
from concurrent import futures as cfutures
from pathlib import Path
from typing import Type

from django.conf import settings
from PIL import Image as PImage

from apps.images.constants import ImageTransformations
from apps.images.data_models import TransformationDataClass
from apps.images.transformations import (
    ImageTransformationCallable,
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
        transformations: list[ImageTransformations],
    ) -> None:
        self._SUPORTED_TRANSFORMATIONS: dict[
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
        self._transformations: list[TransformationDataClass] = []
        self._create_transformations_folders()

    def _create_transformations_folders(self) -> None:
        """
        Creates the folders required for the processed images.
        """
        processed_folder = (
            f"{settings.MEDIA_ROOT}/processed/{self.root_folder}/{self.parent_folder}"
        )
        Path(processed_folder).mkdir(parents=True, exist_ok=True)

        for transformation in self.transformations:
            if transformation not in self._SUPORTED_TRANSFORMATIONS.keys():
                logger.error(f"Invalid/unsupported transformation: {transformation}")
                continue

            transformation_folder = f"{processed_folder}/{transformation.value}"
            Path(transformation_folder).mkdir(parents=True, exist_ok=True)

            self._transformations.append(
                TransformationDataClass(
                    transformation=self._SUPORTED_TRANSFORMATIONS[transformation],
                    file_relative_path=transformation_folder,
                )
            )

    def apply_transformations(self) -> None:
        logger.info(f"Processing image: {self.image_path}")
        with cfutures.ProcessPoolExecutor(max_workers=5) as executor, PImage.open(
            self.image_path
        ) as img:
            image_copy = img.copy()
            futures: list[cfutures.Future[ImageTransformationCallable]] = [
                executor.submit(
                    transformation.transformation,
                    image_copy,
                    transformation.file_relative_path,
                )
                for transformation in self._transformations
            ]
            for f in cfutures.as_completed(futures):
                logger.info(f"Transformation completed for: {f.result().file_name}")
