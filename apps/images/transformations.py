from typing import Any

from PIL import Image as PImage
from PIL import ImageFilter

from apps.images.processing.abstract_classes import ImageTransformationCallable


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
