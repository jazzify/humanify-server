import uuid
from abc import ABC, abstractmethod
from typing import Any

from PIL import Image as PImage


class ImageTransformationCallable(ABC):
    """
    Abstract class that applies a transformation to an image on instantiation
    """

    def __init__(
        self,
        image: PImage.Image,
        filters: dict[str, Any],
        relative_path: str | None = None,
        local_persist: bool = True,
    ) -> None:
        self.image_transformed = self._image_transform(image=image, filters=filters)
        if local_persist:
            if relative_path is None:
                raise ValueError(
                    "relative_path cannot be None when local_persist is True"
                )

            self.file_name = f"{relative_path}/{uuid.uuid4()}.png"
            self.image_transformed.save(self.file_name)

    @abstractmethod
    def _image_transform(
        self,
        image: PImage.Image,
        filters: dict[str, Any],
    ) -> PImage.Image: ...
