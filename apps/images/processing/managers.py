from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from django.conf import settings
from PIL import Image as PImage

from apps.images.processing.data_models import ImageTransformedDataClass
from apps.images.processing.transformers import BaseImageTransformer


class BaseImageManager(ABC):
    def __init__(
        self, image_path: str, transformer: BaseImageTransformer | None = None
    ) -> None:
        self.image_path = image_path
        self.transformer = transformer
        self._transformations_applied: list[ImageTransformedDataClass] = []
        self._opened_image: PImage.Image = self._get_image()

    def apply_transformations(self) -> None:
        if self.transformer:
            self._transformations_applied = self.transformer.transform(
                image=self._opened_image
            )

    def get_image(self) -> PImage.Image:
        return self._opened_image

    @abstractmethod
    def _get_image(self) -> PImage.Image: ...

    @abstractmethod
    def save(self, parent_folder: str) -> dict[str, str]: ...


class ImageLocalManager(BaseImageManager):
    def _get_image(self) -> PImage.Image:
        return PImage.open(self.image_path)

    def save(self, parent_folder: str) -> dict[str, str]:
        if len(self._transformations_applied):
            saved_urls = {}
            path_default = f"{settings.MEDIA_ROOT}/processed/{parent_folder}"

            for transformation in self._transformations_applied:
                path_id = f"{path_default}/{transformation.identifier}"
                Path(path_id).mkdir(parents=True, exist_ok=True)

                final_path = f"{path_id}/{datetime.now().timestamp()}.png"
                transformation.image.save(final_path, "PNG")
                saved_urls[transformation.identifier] = final_path
            return saved_urls
        return {}
