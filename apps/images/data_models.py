from dataclasses import dataclass, field
from typing import Any, Type

from apps.images.constants import ImageTransformations
from apps.images.processing.transformations import ImageTransformationCallable


@dataclass
class ImageTransformationCallableDataClass:
    transform: Type[ImageTransformationCallable]
    filters: dict[str, Any]
    file_relative_path: str


@dataclass
class ImageTransformationDataClass:
    name: ImageTransformations
    filters: dict[str, Any] = field(default_factory=lambda: {})
