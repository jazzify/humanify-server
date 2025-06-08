from dataclasses import dataclass

from PIL import Image as PImage

from apps.image_processing.constants import TRANSFORMATION_FILTER_THUMBNAIL_RESAMPLING
from apps.image_processing.models import ImageTransformation

from .base import (
    ExternalTransformationFilters,
    InternalImageTransformation,
    InternalImageTransformationFilters,
)


@dataclass
class InternalTransformationFiltersThumbnail(InternalImageTransformationFilters):
    size: tuple[float, float]
    resample: PImage.Resampling
    reducing_gap: float | None


@dataclass
class ExternalTransformationFiltersThumbnail(ExternalTransformationFilters):
    size: tuple[float, float] = (128, 128)
    resample: TRANSFORMATION_FILTER_THUMBNAIL_RESAMPLING = (
        TRANSFORMATION_FILTER_THUMBNAIL_RESAMPLING.BICUBIC
    )
    reducing_gap: float | None = 2

    def to_internal(self) -> InternalTransformationFiltersThumbnail:
        return InternalTransformationFiltersThumbnail(
            size=self.size,
            resample=PImage.Resampling[self.resample.name],
            reducing_gap=self.reducing_gap,
        )


class TransformationThumbnail(InternalImageTransformation):
    name = ImageTransformation.THUMBNAIL

    def _image_transform(
        self,
        image: PImage.Image,
        filters: InternalTransformationFiltersThumbnail,
    ) -> PImage.Image:
        new_img = image.copy()
        new_img.thumbnail(
            size=filters.size,
            resample=filters.resample,
            reducing_gap=filters.reducing_gap,
        )
        return new_img
