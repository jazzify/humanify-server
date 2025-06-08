from abc import ABC, abstractmethod
from dataclasses import dataclass

from PIL import Image as PImage

from apps.image_processing.core.transformers.base import (
    BaseImageTransformer,
    InternalImageTransformationResult,
)
from apps.image_processing.models import ProcessingImage, TransformationBatch


@dataclass
class InternalTransformationManagerSaveResult:
    identifier: str
    path: str


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
            image (ProcessingImage): The path of the image to be processed.
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
