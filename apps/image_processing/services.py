import logging

from apps.image_processing.core.transformers.base import (
    ExternalImageTransformationDefinition,
    InternalImageTransformationResult,
)
from apps.image_processing.models import (
    ProcessingImage,
)
from apps.image_processing.strategies import (
    get_manager_strategy,
    get_transformer_strategy,
)
from apps.image_processing.utils import (
    get_internal_transformations,
)

logger = logging.getLogger(__name__)


def image_local_transform(
    user_id: int,
    image_id: str,
    transformations: list[ExternalImageTransformationDefinition],
    is_chain: bool = False,
) -> list[InternalImageTransformationResult]:
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
    internal_transformations = get_internal_transformations(
        external_transformations=transformations
    )
    transformer = get_transformer_strategy(
        transformations=internal_transformations, is_chain=is_chain
    )
    manager = get_manager_strategy()

    image_manager = manager(
        image=image,
        transformer=transformer(transformations=internal_transformations),
    )
    transformations_applied = image_manager.apply_transformations()
    return transformations_applied
