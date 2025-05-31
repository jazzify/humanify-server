import logging
from typing import Type

from apps.image_processing.api.constants import TRANSFORMATIONS_MULTIPROCESS_TRESHOLD
from apps.image_processing.api.data_models import ImageTransformationDefinition
from apps.image_processing.api.utils import get_transformation_dataclasses
from apps.image_processing.src.data_models import (
    InternalImageTransformationDefinition,
    InternalTransformationManagerSaveResult,
)
from apps.image_processing.src.managers import ImageLocalManager
from apps.image_processing.src.transformers import (
    BaseImageTransformer,
    ImageChainTransformer,
    ImageMultiProcessTransformer,
    ImageSequentialTransformer,
)

logger = logging.getLogger(__name__)


def get_local_transformer(
    transformations: list[InternalImageTransformationDefinition],
    is_chain: bool = False,
) -> BaseImageTransformer:
    transformer: Type[BaseImageTransformer] = ImageSequentialTransformer
    if is_chain:
        transformer = ImageChainTransformer
    elif len(transformations) >= TRANSFORMATIONS_MULTIPROCESS_TRESHOLD:
        transformer = ImageMultiProcessTransformer

    return transformer(transformations=transformations)


def image_local_transform(
    image_path: str,
    transformations: list[ImageTransformationDefinition],
    parent_folder: str,
    is_chain: bool = False,
) -> list[InternalTransformationManagerSaveResult]:
    transformations_data = get_transformation_dataclasses(transformations)
    transformer = get_local_transformer(
        transformations=transformations_data, is_chain=is_chain
    )
    image_manager = ImageLocalManager(image_path, transformer=transformer)
    image_manager.apply_transformations()
    return image_manager.save(parent_folder=parent_folder)
