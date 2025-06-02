from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from PIL import Image as PImage

from apps.image_processing.src.data_models import (
    InternalImageTransformationResult,
    InternalTransformationManagerSaveResult,
)
from apps.image_processing.src.transformers import BaseImageTransformer


class BaseImageManager(ABC):
    def __init__(
        self, image_path: str, transformer: BaseImageTransformer | None = None
    ) -> None:
        """
        Initializes a BaseImageManager instance.

        Args:
            image_path (str): The path of the image to be processed.
            transformer (BaseImageTransformer | None, optional): The transformer
                to be used to apply transformations to the image. Defaults to None.
        Attributes:
            image_path (str): The path of the image to be processed.
            transformer (BaseImageTransformer | None): The transformer to be used
                to apply transformations to the image.
            _transformations_applied (list[InternalImageTransformationResult]): The list
                of transformations that have been applied to the image.
            _opened_image (PIL.Image.Image): The opened image that has been processed
                by the transformers.
        """
        self.image_path = image_path
        self.transformer = transformer
        self._opened_image: PImage.Image = self._get_image()

    def apply_transformations(self) -> list[InternalImageTransformationResult]:
        """
        Applies transformations to the image.

        Applies the transformations specified by the transformer to the image and
        returns a list of InternalImageTransformationResult with the transformed images.

        Args:

        Returns:
            list[InternalImageTransformationResult]: A list of InternalImageTransformationResult
        """
        if not self.transformer:
            raise NotImplementedError("No transformer set")

        return self.transformer.transform(image=self._opened_image)

    def get_file(self) -> File[bytes]:
        file_name = self.image_path.split("/")[-1]
        bytes_image = BytesIO(self.get_image().tobytes())
        bytes_image.seek(0)
        return File(bytes_image, name=file_name)

    def get_image(self) -> PImage.Image:
        """
        Returns the opened original image.

        Returns:
            Image.Image: The original opened image.
        """
        return self._opened_image

    @abstractmethod
    def _get_image(self) -> PImage.Image:
        """
        Opens the image file and returns the opened image.

        Returns:
            PImage.Image: The opened image.
        """

    @abstractmethod
    def save(
        self,
        parent_folder: str,
        transformations: list[InternalImageTransformationResult],
    ) -> list[InternalTransformationManagerSaveResult]:
        """
        Saves the transformed images.

        The transformed images are saved under the specified parent folder.
        The function returns a dictionary with the paths of the saved images.

        Args:
            parent_folder (str): The name of the parent folder where the images
                will be saved.

        Returns:
            list[InternalTransformationManagerSaveResult]: A dictionary with {transformer_identifier and paths of the saved images.
        """
        ...


class ImageLocalManager(BaseImageManager):
    def _get_image(self) -> PImage.Image:
        return PImage.open(self.image_path)

    def save(
        self,
        parent_folder: str,
        transformations: list[InternalImageTransformationResult],
    ) -> list[InternalTransformationManagerSaveResult]:
        saved_images = []
        if len(transformations):
            path_default = f"{settings.MEDIA_ROOT}/processed/{parent_folder}"

            for transformation in transformations:
                path_id = f"{path_default}/{transformation.identifier}"
                Path(path_id).mkdir(parents=True, exist_ok=True)

                final_path = f"{path_id}/{datetime.now().timestamp()}.png"
                transformation.image.save(final_path, "PNG")
                saved_images.append(
                    InternalTransformationManagerSaveResult(
                        identifier=transformation.identifier, path=final_path
                    )
                )
        return saved_images
