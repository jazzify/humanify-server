from dataclasses import dataclass, field
from typing import Literal

from PIL import Image as PImage

from apps.image_processing.constants import TRANSFORMATION_FILTER_DITHER
from apps.image_processing.models import ImageTransformation

from .base import (
    ExternalTransformationFilters,
    InternalImageTransformation,
    InternalImageTransformationFilters,
)


@dataclass
class InternalTransformationFiltersBlackAndWhite(InternalImageTransformationFilters):
    mode: Literal["L"] = field(init=False, default="L")
    dither: PImage.Dither | None


@dataclass
class ExternalTransformationFiltersBlackAndWhite(ExternalTransformationFilters):
    dither: TRANSFORMATION_FILTER_DITHER | None = (
        TRANSFORMATION_FILTER_DITHER.FLOYDSTEINBERG
    )

    def to_internal(self) -> InternalTransformationFiltersBlackAndWhite:
        _dither = PImage.Dither[self.dither.name] if self.dither else None
        return InternalTransformationFiltersBlackAndWhite(dither=_dither)


class TransformationBlackAndWhite(InternalImageTransformation):
    name = ImageTransformation.BLACK_AND_WHITE

    def _image_transform(
        self, image: PImage.Image, filters: InternalTransformationFiltersBlackAndWhite
    ) -> PImage.Image:
        new_img = image.convert(
            mode=filters.mode,
            dither=filters.dither,
        )
        return new_img
