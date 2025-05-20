import logging

from apps.images.constants import TRANSFORMATIONS_MULTIPROCESS_TRESHOLD
from apps.images.data_models import ImageTransformationDataClass
from apps.images.processing.data_models import (
    ImageProcessingTransformationDataClass,
    InternalTransformationManagerSave,
)
from apps.images.processing.managers import ImageLocalManager
from apps.images.processing.transformers import (
    BaseImageTransformer,
    ImageMultiProcessTransformer,
    ImageSequentialTransformer,
)
from apps.images.processing.utils import get_transformation_dataclasses

logger = logging.getLogger(__name__)


def get_local_transformer(
    transformations: list[ImageProcessingTransformationDataClass],
) -> BaseImageTransformer:
    if len(transformations) < TRANSFORMATIONS_MULTIPROCESS_TRESHOLD:
        return ImageSequentialTransformer(transformations=transformations)
    return ImageMultiProcessTransformer(transformations=transformations)


def image_local_transform(
    image_path: str,
    transformations: list[ImageTransformationDataClass],
    parent_folder: str,
) -> list[InternalTransformationManagerSave]:
    transformations_data = get_transformation_dataclasses(transformations)
    transformer = get_local_transformer(transformations=transformations_data)
    image_manager = ImageLocalManager(image_path, transformer=transformer)
    image_manager.apply_transformations()
    return image_manager.save(parent_folder=parent_folder)
