from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type

from PIL import Image as PImage

from apps.image_processing.core.transformations.base import (
    ExternalTransformationFilters,
    InternalImageTransformation,
)
from apps.image_processing.models import TransformationBatch


@dataclass
class InternalImageTransformationDefinition:
    identifier: str
    transformation: Type[InternalImageTransformation]
    filters: ExternalTransformationFilters


@dataclass
class ExternalImageTransformationDefinition:
    identifier: str
    transformation: str
    filters: ExternalTransformationFilters | None = None


@dataclass
class InternalImageTransformationResult:
    identifier: str
    image: PImage.Image


class BaseImageTransformer(ABC):
    name: str

    def __init__(
        self,
        transformations: list[InternalImageTransformationDefinition],
    ) -> None:
        self.transformations_data = transformations

    @abstractmethod
    def transform(
        self, image: PImage.Image, transformation_batch: TransformationBatch
    ) -> list[InternalImageTransformationResult]: ...
