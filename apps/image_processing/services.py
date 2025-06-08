import logging

from apps.image_processing.core.managers.local import ImageLocalManager
from apps.image_processing.core.transformers.base import (
    InternalImageTransformationResult,
)
from apps.image_processing.models import (
    ProcessingImage,
)
from apps.image_processing.utils import (
    get_local_transformer,
    get_transformation_dataclasses,
)
from apps.image_processing_api.data_models import ImageTransformationDefinition

logger = logging.getLogger(__name__)


def image_local_transform(
    user_id: int,
    image_id: str,
    transformations: list[ImageTransformationDefinition],
    parent_folder: str,
    is_chain: bool = False,
) -> list[InternalImageTransformationResult]:  # TODO: return model structure
    """
    Transforms a local image using specified transformations and saves the results.

    This function processes an image located at the specified path using a list of
    image transformations. The transformed images are saved under the specified
    parent folder. The function returns a list of results indicating the paths
    where the transformed images were saved.

    Args:
        user_id (int): The user_id who is performing the transformation.
        image_id (str): The identifier of the image to be transformed.
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
    image = ProcessingImage.objects.get(id=image_id, user_id=user_id)
    transformations_data = get_transformation_dataclasses(transformations)
    transformer = get_local_transformer(
        transformations=transformations_data, is_chain=is_chain
    )
    image_manager = ImageLocalManager(image=image, transformer=transformer)
    transformations_applied = image_manager.apply_transformations()
    return transformations_applied
