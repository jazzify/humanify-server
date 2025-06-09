import logging
from typing import Any

from django_tasks import task

logger = logging.getLogger(__name__)


@task(queue_name="image_processing")
def transform_uploaded_images(
    user_id: int,
    image_id: str,
    transformations: list[dict[str, Any]],
    is_chain: bool = False,
) -> None:
    logger.debug(
        f"Transforming image {image_id} with transformations {transformations} for user {user_id}"
    )

    from apps.image_processing.core.transformers.base import (
        ExternalImageTransformationDefinition,
    )
    from apps.image_processing.services import image_local_transform
    from apps.image_processing_api.utils import (
        get_filters_dataclasses_by_transformation,
    )

    transformations_to_apply = []
    for transformation in transformations:
        transformation_filter = transformation.get("filters", None)
        if transformation_filter:
            filters_dataclass = get_filters_dataclasses_by_transformation(
                transformation["transformation"]
            )
            transformation_filter = filters_dataclass(**transformation_filter)
        transformation_definition = ExternalImageTransformationDefinition(
            identifier=transformation["identifier"],
            transformation=transformation["transformation"],
            filters=transformation_filter,
        )
        transformations_to_apply.append(transformation_definition)

    applied_transformations = image_local_transform(
        user_id=user_id,
        image_id=image_id,
        transformations=transformations_to_apply,
        is_chain=is_chain,
    )
