import uuid
from abc import ABC, abstractmethod

from PIL import Image as PImage
from PIL import ImageFilter


class ImageTransformationCallable(ABC):
    def __init__(self, image: PImage.Image, relative_path: str) -> None:
        self.image = image
        self.relative_path = relative_path
        self.file_name = self._generate_image_file_name(relative_path)
        self.apply_transformation()

    @classmethod
    def _generate_image_file_name(cls, relative_path: str) -> str:
        return f"{relative_path}/{uuid.uuid4()}.png"

    @abstractmethod
    def apply_transformation(self) -> None:
        raise NotImplementedError


class TransformationThumbnail(ImageTransformationCallable):
    def apply_transformation(self) -> None:
        self.image.thumbnail((128, 128))
        self.image.save(self.file_name)


class TransformationBlur(ImageTransformationCallable):
    def apply_transformation(self) -> None:
        new_img = self.image.filter(ImageFilter.BLUR)
        new_img.save(self.file_name)


class TransformationBlackAndWhite(ImageTransformationCallable):
    def apply_transformation(self) -> None:
        new_img = self.image.convert("L")
        new_img.save(self.file_name)
