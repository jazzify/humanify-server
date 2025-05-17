from dataclasses import dataclass, field
from typing import Any, Type

from apps.images.abstract_classes import ImageTransformationCallable
from apps.images.constants import ImageTransformations


@dataclass
class ImageTransformationCallableDataClass:
    transform: Type[ImageTransformationCallable]
    filters: dict[str, Any]
    file_relative_path: str


@dataclass
class ImageTransformationDataClass:
    name: ImageTransformations
    filters: dict[str, Any] = field(default_factory=lambda: {})
