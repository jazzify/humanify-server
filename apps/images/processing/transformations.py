from abc import ABC, abstractmethod
from typing import Any

from PIL import Image as PImage
from PIL import ImageFilter


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

    Args:
        image (PImage.Image): The PIL image that will undergo the transformation.
        filters (dict[str, Any]): A dictionary with the filters that will be
            applied to the image. The filters are specific to the concrete
            implementation of the transformator.
    """

    def __init__(
        self,
        image: PImage.Image,
        filters: dict[str, Any],
    ) -> None:
        self.image_transformed = self._image_transform(image=image, filters=filters)

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


class TransformationThumbnail(ImageTransformationCallable):
    def _image_transform(
        self,
        image: PImage.Image,
        filters: dict[str, Any],
    ) -> PImage.Image:
        new_img = image.copy()
        new_filters = {
            "size": filters.get("size", (128, 128)),
            "resample": filters.get("resample", PImage.Resampling.BICUBIC),
            "reducing_gap": filters.get("reducing_gap", 2),
        }
        new_img.thumbnail(**new_filters)
        return new_img


class TransformationBlur(ImageTransformationCallable):
    def _image_transform(
        self, image: PImage.Image, filters: dict[str, ImageFilter.Filter]
    ) -> PImage.Image:
        filter = filters.get("filter", ImageFilter.BLUR)
        new_img = image.filter(filter)
        return new_img


class TransformationBlackAndWhite(ImageTransformationCallable):
    def _image_transform(
        self, image: PImage.Image, filters: dict[str, Any]
    ) -> PImage.Image:
        new_filters = {
            "mode": "L",
            "matrix": filters.get("matrix", None),
            "dither": filters.get("dither", None),
            "palette": filters.get("palette", PImage.Palette.ADAPTIVE),
            "colors": filters.get("colors", 256),
        }
        new_img = image.convert(**new_filters)
        return new_img
