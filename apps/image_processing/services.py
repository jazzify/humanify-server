import logging
from dataclasses import asdict
from io import BytesIO

from django.core.files import File

from apps.image_processing.core.managers import ImageLocalManager
from apps.image_processing.data_models import (
    InternalImageTransformationResult,
    InternalTransformationManagerSaveResult,
)
from apps.image_processing.models import (
    Image,
    ImageTransformation,
    ProcessedImage,
    TransformationBatch,
)
from apps.image_processing.utils import (
    get_local_transformer,
    get_transformation_dataclasses,
)
from apps.image_processing_api.data_models import ImageTransformationDefinition

logger = logging.getLogger(__name__)


def image_processing_save_procedure(
    user_id: int,
    image_file: File[bytes],
    image_path: str,
    transformer: str,
    transformations: list[ImageTransformationDefinition],
    transformations_applied: list[InternalImageTransformationResult],
) -> None:
    try:
        image = Image.objects.select_related("user").get(
            user_id=user_id, file=image_path
        )
    except Image.DoesNotExist:
        image = Image.objects.create(user_id=user_id, file=image_file)

    transformation_batch = TransformationBatch(
        input_image=image,
        transformer=transformer,
    )
    transformation_batch.full_clean()
    transformation_batch.save()

    image_transformations = []
    for transformation in transformations:
        filters = asdict(transformation.filters) if transformation.filters else None
        image_transformations.append(
            ImageTransformation(
                identifier=transformation.identifier,
                transformation=transformation.transformation,
                filters=filters,
                batch=transformation_batch,
            )
        )
    ImageTransformation.objects.bulk_create(image_transformations)

    image_transformations_dict = {
        transformation.identifier: transformation
        for transformation in image_transformations
    }
    processed_images = []
    for transformation_applied in transformations_applied:
        bytes_image = BytesIO(transformation_applied.image.tobytes())
        bytes_image.seek(0)
        processed_images.append(
            ProcessedImage(
                identifier=transformation_applied.identifier,
                file=File(bytes_image, name=f"{transformation_applied.identifier}.png"),
                transformation=image_transformations_dict[
                    transformation_applied.identifier
                ],
            )
        )
    ProcessedImage.objects.bulk_create(processed_images)


def image_local_transform(
    user_id: int,
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
        user_id (int): The user_id who is performing the transformation.
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
    transformations_applied = image_manager.apply_transformations()
    images_save = image_manager.save(
        parent_folder=parent_folder, transformations=transformations_applied
    )
    image_processing_save_procedure(
        user_id=user_id,
        image_file=image_manager.get_file(),
        image_path=image_path,
        transformer=transformer.name,
        transformations=transformations,
        transformations_applied=transformations_applied,
    )
    return images_save
