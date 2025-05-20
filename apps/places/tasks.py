import logging

from django_tasks import task

logger = logging.getLogger(__name__)


@task(queue_name="place_images")
def transform_uploaded_images(
    file_path: str, root_folder: str, parent_folder: str
) -> None:
    from apps.images.constants import (
        ImageTransformations,
        TransformationFilterBlurFilter,
        TransformationFilterDither,
        TransformationFilterThumbnailResampling,
    )
    from apps.images.data_models import (
        ImageTransformationDataClass,
        TransformationFiltersBlackAndWhite,
        TransformationFiltersBlur,
        TransformationFiltersThumbnail,
    )
    from apps.images.services import image_local_transform

    logger.info(f"Transforming image {file_path}")
    transformations = [
        ImageTransformationDataClass(
            identifier="THUMBNAIL/default",
            transformation=ImageTransformations.THUMBNAIL,
        ),
        ImageTransformationDataClass(
            identifier="THUMBNAIL/size_64",
            transformation=ImageTransformations.THUMBNAIL,
            filters=TransformationFiltersThumbnail(size=(64, 64)),
        ),
        ImageTransformationDataClass(
            identifier="THUMBNAIL/s_320_gap_4",
            transformation=ImageTransformations.THUMBNAIL,
            filters=TransformationFiltersThumbnail(size=(320, 320), reducing_gap=4),
        ),
        ImageTransformationDataClass(
            identifier="THUMBNAIL/s_320_gap_8_lanczos",
            transformation=ImageTransformations.THUMBNAIL,
            filters=TransformationFiltersThumbnail(
                size=(320, 320),
                reducing_gap=8,
                resample=TransformationFilterThumbnailResampling.LANCZOS,
            ),
        ),
        ImageTransformationDataClass(
            identifier="BNW/default",
            transformation=ImageTransformations.BLACK_AND_WHITE,
        ),
        ImageTransformationDataClass(
            identifier="BNW/floydsteinberg",
            transformation=ImageTransformations.BLACK_AND_WHITE,
            filters=TransformationFiltersBlackAndWhite(
                dither=TransformationFilterDither.FLOYDSTEINBERG
            ),
        ),
        ImageTransformationDataClass(
            identifier="BNW/none",
            transformation=ImageTransformations.BLACK_AND_WHITE,
            filters=TransformationFiltersBlackAndWhite(
                dither=TransformationFilterDither.NONE
            ),
        ),
        ImageTransformationDataClass(
            identifier="BLUR/default",
            transformation=ImageTransformations.BLUR,
        ),
        ImageTransformationDataClass(
            identifier="BLUR/gaussian_86",
            transformation=ImageTransformations.BLUR,
            filters=TransformationFiltersBlur(
                filter=TransformationFilterBlurFilter.GAUSSIAN_BLUR,
                radius=86,
            ),
        ),
        ImageTransformationDataClass(
            identifier="BLUR/box_48",
            transformation=ImageTransformations.BLUR,
            filters=TransformationFiltersBlur(
                filter=TransformationFilterBlurFilter.BOX_BLUR,
                radius=48,
            ),
        ),
    ]
    applied_transformations = image_local_transform(
        image_path=file_path,
        transformations=transformations,
        parent_folder=parent_folder,
    )

    for transformation in applied_transformations:
        logger.info(f"{transformation.identifier}: {transformation.path}")
