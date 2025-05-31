from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal, Type

from PIL import Image as PImage
from PIL import ImageFilter


@dataclass
class InternalImageTransformationFilters(ABC): ...


@dataclass
class InternalImageTransformation(ABC):
    """
    Abstract class that applies Subclass transformation at subclass
    instantiation to the image provided with the filters provided

    The transformed image is stored as an instance variable and can
    be accessed with the `image_transformed` attribute.

    Args:
        image (PImage.Image): The PIL image that will undergo the transformation.
        filters (TransformationFilter): A TransformationFilter instance with the
        filters that will be applied to the image. The filters are specific to
        the concrete implementation of the transformation.
    """

    def __init__(
        self,
        image: PImage.Image,
        filters: InternalImageTransformationFilters,
    ) -> None:
        self.image_transformed = self._image_transform(image=image, filters=filters)

    @abstractmethod
    def _image_transform(
        self,
        image: PImage.Image,
        filters: Any,  # Each subclass will have its own filters
    ) -> PImage.Image:
        """
        Abstract method that should be implemented by the concrete
        transformation.

        This method takes a PIL image and applies the transformation
        specified by the filters to the image.

        Args:
            image (PImage.Image): The PIL image that will undergo the
                transformation.
            filters (dict[str, Any]): A dictionary with the filters
                that will be applied to the image.

        Returns:
            PImage.Image: A new PIL image with the applied filters.
        """


@dataclass
class InternalTransformationFiltersThumbnail(InternalImageTransformationFilters):
    size: tuple[float, float]
    resample: PImage.Resampling
    reducing_gap: float | None


@dataclass
class InternalTransformationFiltersBlur(InternalImageTransformationFilters):
    filter: ImageFilter.MultibandFilter


@dataclass
class InternalTransformationFiltersBlackAndWhite(InternalImageTransformationFilters):
    mode: Literal["1"] = field(init=False, default="1")
    dither: PImage.Dither | None


@dataclass
class InternalImageTransformationDefinition:
    identifier: str
    transformation: Type[InternalImageTransformation]
    filters: InternalImageTransformationFilters


@dataclass
class InternalImageTransformationResult:
    identifier: str
    image: PImage.Image


@dataclass
class InternalTransformationManagerSaveResult:
    identifier: str
    path: str


@dataclass
class InternalTransformationMapper:
    transformation: Type[InternalImageTransformation]
    filters: InternalImageTransformationFilters
