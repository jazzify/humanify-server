from dataclasses import dataclass
from typing import Type

from apps.images.abstract_classes import ImageTransformationCallable


@dataclass
class TransformationDataClass:
    transform: Type[ImageTransformationCallable]
    file_relative_path: str
