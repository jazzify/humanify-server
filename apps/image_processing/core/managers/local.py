from PIL import Image as PImage

from .base import BaseImageManager


class ImageLocalManager(BaseImageManager):
    def _get_image(self) -> PImage.Image:
        image_path = self.image.file.path
        return PImage.open(image_path)
