import uuid
from abc import ABC, abstractmethod
from typing import Any

from PIL import Image as PImage


# TODO: Change to Protocol?
# This abstract class should be a Protocol however I decided to
# use an abstract class to allow code execution on instantiation
# and enforce the use of the _image_transform method this gives
# support to image transformation multiprocessing part for the
# ImageTransformationService.apply_transformations method
# TODO: Drop local persistance support
# Local persistence should be handled in the business logic layer
# and not in the transformator itself
# TODO: Make `filters` a class
# Refactor to custom data models for the filters with default
# values that can be overwritten and adds type checking
class ImageTransformationCallable(ABC):
    """
    Abstract class that applies Image transformations at subclass
    instantiation

    This class is an abstract class that on instantiation applies
    a given image transformation to the image provided. The
    transformed image is stored as an instance variable and can
    be accessed with the `image_transformed` attribute.

    The class is also responsible for locally persisting the
    transformed image. If `local_persist` is set to True the
    transformedimage will be saved to the local file system
    with a filename that is randomly generated. The file name
    can be accessed with the `file_name` attribute.

    Args:
        image (PImage.Image): The PIL image that will undergo the transformation.
        filters (dict[str, Any]): A dictionary with the filters that will be
            applied to the image. The filters are specific to the concrete
            implementation of the transformator.
        relative_path (str | None): The relative path to the directory where the
            transformed image will be saved. This parameter is optional and
            defaults to `None`. If `local_persist` is set to `True` this parameter
            must be provided.
        local_persist (bool): A boolean indicating whether the transformed
            image should be saved to the local file system. Defaults to `True`.
    """

    def __init__(
        self,
        image: PImage.Image,
        filters: dict[str, Any],
        relative_path: str | None = None,
        local_persist: bool = True,
    ) -> None:
        self.image_transformed = self._image_transform(image=image, filters=filters)
        if local_persist:
            if relative_path is None:
                raise ValueError(
                    "relative_path cannot be None when local_persist is True"
                )

            self.file_name = f"{relative_path}/{uuid.uuid4()}.png"
            self.image_transformed.save(self.file_name)

    @abstractmethod
    def _image_transform(
        self,
        image: PImage.Image,
        filters: dict[str, Any],
    ) -> PImage.Image:
        """
        Abstract method that should be implemented by the concrete
        implementation of the transformator.

        This method takes a PIL image and applies the transformation
        specified by the filters to the image.

        Args:
            image (PImage.Image): The PIL image that will undergo the
                transformation.
            filters (dict[str, Any]): A dictionary with the filters that will be
                applied to the image.

        Returns:
            PImage.Image: The transformed PIL image.
        """
