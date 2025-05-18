from dataclasses import dataclass, field
from typing import Any, Type

from PIL import Image as PImage

from apps.images.processing.transformations import ImageTransformationCallable


@dataclass
class ImageTransformationDataClass:
    identifier: str
    transformation: Type[ImageTransformationCallable]
    filters: dict[str, Any] = field(default_factory=lambda: {})


@dataclass
class ImageTransformedDataClass:
    identifier: str
    image: PImage.Image
