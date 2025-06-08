from abc import ABC, abstractmethod
from pathlib import Path

from django.conf import settings
from PIL import Image as PImage

from apps.image_processing.core.transformers import BaseImageTransformer
from apps.image_processing.data_models import (
    InternalImageTransformationResult,
    InternalTransformationManagerSaveResult,
)
from apps.image_processing.models import ProcessingImage, TransformationBatch


class BaseImageManager(ABC):
    def __init__(
        self, image: ProcessingImage, transformer: BaseImageTransformer | None = None
    ) -> None:
        """
        Initializes a BaseImageManager instance.

        Args:
            image (ProcessingImage): The path of the image to be processed.
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
        self.image = image
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

        transformation_batch = TransformationBatch(
            input_image=self.image,
            transformer=self.transformer.name,
        )
        transformation_batch.full_clean()
        transformation_batch.save()

        transformations = self.transformer.transform(
            image=self._opened_image, transformation_batch=transformation_batch
        )

        return transformations

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
        image_path = self.image.file.path
        return PImage.open(image_path)

    def save(
        self,
        parent_folder: str,
        transformations: list[InternalImageTransformationResult],
    ) -> list[InternalTransformationManagerSaveResult]:
        saved_images = []
        if len(transformations):
            path_default = f"{settings.MEDIA_ROOT}/image_processing/processed"
            Path(path_default).mkdir(parents=True, exist_ok=True)

            for transformation in transformations:
                path_id = f"{path_default}/{transformation.identifier}.png"
                transformation.image.save(path_id, "PNG")
                saved_images.append(
                    InternalTransformationManagerSaveResult(
                        identifier=transformation.identifier, path=path_id
                    )
                )
        return saved_images
