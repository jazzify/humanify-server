import logging

from django_tasks import task

logger = logging.getLogger(__name__)


@task(queue_name="place_images")
def transform_uploaded_images(
    file_path: str, root_folder: str, parent_folder: str
) -> None:
    import uuid

    from PIL import ImageFilter

    from apps.images.constants import ImageTransformations
    from apps.images.data_models import ImageTransformationDataClass
    from apps.images.services import image_local_transform

    logger.info(f"Transforming image {file_path}")
    transformations = [
        ImageTransformationDataClass(
            identifier=f"{uuid.uuid4()}",
            transformation=ImageTransformations.THUMBNAIL,
            filters={"size": (64, 64)},
        ),
        ImageTransformationDataClass(
            identifier=f"{uuid.uuid4()}",
            transformation=ImageTransformations.THUMBNAIL,
        ),
        ImageTransformationDataClass(
            identifier=f"{uuid.uuid4()}",
            transformation=ImageTransformations.THUMBNAIL,
            filters={"size": (320, 320)},
        ),
        ImageTransformationDataClass(
            identifier=f"{uuid.uuid4()}",
            transformation=ImageTransformations.BLACK_AND_WHITE,
        ),
        ImageTransformationDataClass(
            identifier=f"{uuid.uuid4()}",
            transformation=ImageTransformations.BLACK_AND_WHITE,
            filters={
                "matrix": (
                    0.312453,
                    0.957580,
                    0.980423,
                    0,
                    0.112671,
                    0.915160,
                    0.972169,
                    0,
                    0.319334,
                    0.919193,
                    0.950227,
                    0,
                )
            },
        ),
        ImageTransformationDataClass(
            identifier=f"{uuid.uuid4()}",
            transformation=ImageTransformations.BLUR,
            filters={"filter": ImageFilter.GaussianBlur(48)},
        ),
        ImageTransformationDataClass(
            identifier=f"{uuid.uuid4()}",
            transformation=ImageTransformations.BLUR,
            filters={"filter": ImageFilter.BoxBlur(48)},
        ),
    ]
    applied_transformations = image_local_transform(
        image_path=file_path,
        transformations=transformations,
        parent_folder=parent_folder,
    )

    for identifier, final_path in applied_transformations.items():
        logger.info(f"{identifier}: {final_path}")
