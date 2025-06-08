from dataclasses import dataclass
from typing import Sequence

from PIL import Image as PImage
from PIL import ImageFilter

from apps.image_processing.constants import TRANSFORMATION_FILTER_BLUR_FILTER
from apps.image_processing.models import ImageTransformation

from .base import (
    ExternalTransformationFilters,
    InternalImageTransformation,
    InternalImageTransformationFilters,
)


@dataclass
class InternalTransformationFiltersBlur(InternalImageTransformationFilters):
    filter: ImageFilter.MultibandFilter


@dataclass
class ExternalTransformationFiltersBlur(ExternalTransformationFilters):
    filter: TRANSFORMATION_FILTER_BLUR_FILTER = TRANSFORMATION_FILTER_BLUR_FILTER.BLUR
    radius: float | Sequence[float] = 10.0

    def to_internal(self) -> InternalTransformationFiltersBlur:
        return InternalTransformationFiltersBlur(
            filter={
                TRANSFORMATION_FILTER_BLUR_FILTER.BLUR: ImageFilter.BLUR(),
                TRANSFORMATION_FILTER_BLUR_FILTER.BOX_BLUR: ImageFilter.BoxBlur(
                    radius=self.radius
                ),
                TRANSFORMATION_FILTER_BLUR_FILTER.GAUSSIAN_BLUR: ImageFilter.GaussianBlur(
                    radius=self.radius
                ),
            }[self.filter]
        )


class TransformationBlur(InternalImageTransformation):
    name = ImageTransformation.BLUR

    def _image_transform(
        self, image: PImage.Image, filters: InternalTransformationFiltersBlur
    ) -> PImage.Image:
        new_img = image.filter(filters.filter)
        return new_img
