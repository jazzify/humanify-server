from typing import Type

from apps.image_processing.constants import TRANSFORMATIONS_MULTIPROCESS_TRESHOLD
from apps.image_processing.core.managers.base import BaseImageManager
from apps.image_processing.core.managers.local import ImageLocalManager
from apps.image_processing.core.transformers.base import (
    BaseImageTransformer,
    InternalImageTransformationDefinition,
)
from apps.image_processing.core.transformers.chain import ImageChainTransformer
from apps.image_processing.core.transformers.multiprocess import (
    ImageMultiProcessTransformer,
)
from apps.image_processing.core.transformers.sequential import (
    ImageSequentialTransformer,
)


def get_transformer_strategy(
    transformations: list[InternalImageTransformationDefinition],
    is_chain: bool = False,
) -> Type[BaseImageTransformer]:
    transformer: Type[BaseImageTransformer] = ImageSequentialTransformer
    if is_chain:
        transformer = ImageChainTransformer
    elif len(transformations) >= TRANSFORMATIONS_MULTIPROCESS_TRESHOLD:
        transformer = ImageMultiProcessTransformer

    return transformer


def get_manager_strategy() -> Type[BaseImageManager]:
    # Currently, only local image processing is supported
    return ImageLocalManager
