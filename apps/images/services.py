import logging
from typing import Type

from apps.images.constants import TRANSFORMATIONS_MULTIPROCESS_TRESHOLD
from apps.images.data_models import ImageTransformationDataClass
from apps.images.processing.data_models import (
    ImageProcessingTransformationDataClass,
    InternalTransformationManagerSave,
)
from apps.images.processing.managers import ImageLocalManager
from apps.images.processing.transformers import (
    BaseImageTransformer,
    ImageChainTransformer,
    ImageMultiProcessTransformer,
    ImageSequentialTransformer,
)
from apps.images.processing.utils import get_transformation_dataclasses

logger = logging.getLogger(__name__)


def get_local_transformer(
    transformations: list[ImageProcessingTransformationDataClass],
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
    transformations: list[ImageTransformationDataClass],
    parent_folder: str,
    is_chain: bool = False,
) -> list[InternalTransformationManagerSave]:
    transformations_data = get_transformation_dataclasses(transformations)
    transformer = get_local_transformer(
        transformations=transformations_data, is_chain=is_chain
    )
    image_manager = ImageLocalManager(image_path, transformer=transformer)
    image_manager.apply_transformations()
    return image_manager.save(parent_folder=parent_folder)
