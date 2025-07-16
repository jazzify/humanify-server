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
    Applies a series of transformations to a image and saves the transformed
    image/s locally.

    Args:
        user_id (int): The user_id who is performing the transformation.
        image_id (str): The id of the ProcessingImage to be transformed.
        transformations (list[ExternalImageTransformationDefinition]): A list of
            transformation definitions to apply to the image.
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
