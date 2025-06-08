from dataclasses import dataclass
from typing import Sequence

from PIL import Image as PImage
from PIL import ImageFilter

from apps.image_processing.data_models import (
    InternalTransformationFiltersBlackAndWhite,
    InternalTransformationFiltersBlur,
    InternalTransformationFiltersThumbnail,
    TransformationFilters,
)
from apps.image_processing_api.constants import (
    ImageTransformations,
    TransformationFilterBlurFilter,
    TransformationFilterDither,
    TransformationFilterThumbnailResampling,
)


@dataclass
class TransformationFiltersThumbnail(TransformationFilters):
    size: tuple[float, float] = (128, 128)
    resample: TransformationFilterThumbnailResampling = (
        TransformationFilterThumbnailResampling.BICUBIC
    )
    reducing_gap: float | None = 2

    def to_internal(self) -> InternalTransformationFiltersThumbnail:
        return InternalTransformationFiltersThumbnail(
            size=self.size,
            resample=PImage.Resampling[self.resample.name],
            reducing_gap=self.reducing_gap,
        )


@dataclass
class TransformationFiltersBlur(TransformationFilters):
    filter: TransformationFilterBlurFilter = TransformationFilterBlurFilter.BLUR
    radius: float | Sequence[float] = 10.0

    def to_internal(self) -> InternalTransformationFiltersBlur:
        return InternalTransformationFiltersBlur(
            filter={
                TransformationFilterBlurFilter.BLUR: ImageFilter.BLUR(),
                TransformationFilterBlurFilter.BOX_BLUR: ImageFilter.BoxBlur(
                    radius=self.radius
                ),
                TransformationFilterBlurFilter.GAUSSIAN_BLUR: ImageFilter.GaussianBlur(
                    radius=self.radius
                ),
            }[self.filter]
        )


@dataclass
class TransformationFiltersBlackAndWhite(TransformationFilters):
    dither: TransformationFilterDither = TransformationFilterDither.FLOYDSTEINBERG

    def to_internal(self) -> InternalTransformationFiltersBlackAndWhite:
        return InternalTransformationFiltersBlackAndWhite(
            dither=PImage.Dither[self.dither.name]
        )


@dataclass
class ImageTransformationDefinition:
    identifier: str
    transformation: ImageTransformations
    filters: TransformationFilters | None = None
