import uuid
from abc import ABC, abstractmethod

from PIL import Image as PImage


class ImageTransformationCallable(ABC):
    def __init__(self, image: PImage.Image, relative_path: str) -> None:
        self.image = image
        self.relative_path = relative_path
        self.file_name = self._generate_image_file_name(relative_path)
        self._apply_transformation()

    @classmethod
    def _generate_image_file_name(cls, relative_path: str) -> str:
        return f"{relative_path}/{uuid.uuid4()}.png"

    @abstractmethod
    def _apply_transformation(self) -> None: ...
