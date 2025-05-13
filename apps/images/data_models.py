from dataclasses import dataclass
from typing import Type

from apps.images.transformations import ImageTransformationCallable


@dataclass
class TransformationDataClass:
    transformation: Type[ImageTransformationCallable]
    file_relative_path: str
