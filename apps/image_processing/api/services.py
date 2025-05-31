import logging

from apps.image_processing.api.data_models import ImageTransformationDefinition
from apps.image_processing.api.utils import (
    get_local_transformer,
    get_transformation_dataclasses,
)
from apps.image_processing.src.data_models import (
    InternalTransformationManagerSaveResult,
)
from apps.image_processing.src.managers import ImageLocalManager

logger = logging.getLogger(__name__)


def image_local_transform(
    image_path: str,
    transformations: list[ImageTransformationDefinition],
    parent_folder: str,
    is_chain: bool = False,
) -> list[InternalTransformationManagerSaveResult]:
    """
    Transforms a local image using specified transformations and saves the results.

    This function processes an image located at the specified path using a list of
    image transformations. The transformed images are saved under the specified
    parent folder. The function returns a list of results indicating the paths
    where the transformed images were saved.

    Args:
        image_path (str): The path to the local image file to be transformed.
        transformations (list[ImageTransformationDefinition]): A list of
            transformation definitions to apply to the image.
        parent_folder (str): The name of the parent folder where transformed
            images will be saved.
        is_chain (bool, optional): A flag indicating whether to use a chain
            transformer. Defaults to False.

    Returns:
        list[InternalTransformationManagerSaveResult]: A list containing the
        results of the transformation, including the paths of the saved images.
    """
    transformations_data = get_transformation_dataclasses(transformations)
    transformer = get_local_transformer(
        transformations=transformations_data, is_chain=is_chain
    )
    image_manager = ImageLocalManager(image_path, transformer=transformer)
    applied_transformations = image_manager.apply_transformations()
    return image_manager.save(
        parent_folder=parent_folder, transformations=applied_transformations
    )
