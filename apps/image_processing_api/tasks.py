import logging
from typing import Any

from django_tasks import task

logger = logging.getLogger(__name__)


@task(queue_name="image_processing")
def transform_uploaded_images(
    user_id: int,
    image_id: str,
    parent_folder: str,
    transformations: list[dict[str, Any]],
    is_chain: bool = False,
) -> None:
    logger.debug(
        f"Transforming image {image_id} with transformations {transformations} for user {user_id}"
    )

    from apps.image_processing.services import image_local_transform
    from apps.image_processing.utils import get_filters_dataclasses_by_transformation
    from apps.image_processing_api.data_models import ImageTransformationDefinition

    transformations_to_apply = []
    for transformation in transformations:
        transformation_filter = transformation.get("filters", None)
        if transformation_filter:
            filters_dataclass = get_filters_dataclasses_by_transformation(
                transformation["transformation"]
            )
            transformation_filter = filters_dataclass(**transformation_filter)
        transformation_definition = ImageTransformationDefinition(
            identifier=transformation["identifier"],
            transformation=transformation["transformation"],
            filters=transformation_filter,
        )
        transformations_to_apply.append(transformation_definition)

    applied_transformations = image_local_transform(
        user_id=user_id,
        image_path=image_id,
        transformations=transformations_to_apply,
        parent_folder=parent_folder,
        is_chain=is_chain,
    )

    for applied_transformation in applied_transformations:
        logger.info(
            f"{applied_transformation.identifier}: {applied_transformation.path}"
        )
