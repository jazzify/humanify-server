from PIL import Image as PImage

from apps.images.processing.data_models import (
    InternalImageTransformation,
    InternalTransformationFiltersBlackAndWhite,
    InternalTransformationFiltersBlur,
    InternalTransformationFiltersThumbnail,
)


class TransformationThumbnail(InternalImageTransformation):
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


class TransformationBlur(InternalImageTransformation):
    def _image_transform(
        self, image: PImage.Image, filters: InternalTransformationFiltersBlur
    ) -> PImage.Image:
        new_img = image.filter(filters.filter)
        return new_img


class TransformationBlackAndWhite(InternalImageTransformation):
    def _image_transform(
        self, image: PImage.Image, filters: InternalTransformationFiltersBlackAndWhite
    ) -> PImage.Image:
        new_img = image.convert(
            mode=filters.mode,
            dither=filters.dither,
        )
        return new_img
