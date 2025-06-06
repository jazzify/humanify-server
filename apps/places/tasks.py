import logging

from django_tasks import task

logger = logging.getLogger(__name__)


@task(queue_name="place_images")
def transform_uploaded_images(user_id: int, file_path: str, parent_folder: str) -> None:
    from apps.image_processing.api.constants import (
        ImageTransformations,
        TransformationFilterBlurFilter,
        TransformationFilterDither,
        TransformationFilterThumbnailResampling,
    )
    from apps.image_processing.api.data_models import (
        ImageTransformationDefinition,
        TransformationFiltersBlackAndWhite,
        TransformationFiltersBlur,
        TransformationFiltersThumbnail,
    )
    from apps.image_processing.api.services import image_local_transform

    logger.info(f"Transforming image {file_path}")
    transformations = [
        ImageTransformationDefinition(
            identifier="THUMBNAIL/default",
            transformation=ImageTransformations.THUMBNAIL,
        ),
        ImageTransformationDefinition(
            identifier="THUMBNAIL/size_64",
            transformation=ImageTransformations.THUMBNAIL,
            filters=TransformationFiltersThumbnail(size=(64, 64)),
        ),
        ImageTransformationDefinition(
            identifier="THUMBNAIL/s_320_gap_4",
            transformation=ImageTransformations.THUMBNAIL,
            filters=TransformationFiltersThumbnail(size=(320, 320), reducing_gap=4),
        ),
        ImageTransformationDefinition(
            identifier="THUMBNAIL/s_320_gap_8_lanczos",
            transformation=ImageTransformations.THUMBNAIL,
            filters=TransformationFiltersThumbnail(
                size=(320, 320),
                reducing_gap=8,
                resample=TransformationFilterThumbnailResampling.LANCZOS,
            ),
        ),
        ImageTransformationDefinition(
            identifier="BNW/default",
            transformation=ImageTransformations.BLACK_AND_WHITE,
        ),
        ImageTransformationDefinition(
            identifier="BNW/floydsteinberg",
            transformation=ImageTransformations.BLACK_AND_WHITE,
            filters=TransformationFiltersBlackAndWhite(
                dither=TransformationFilterDither.FLOYDSTEINBERG
            ),
        ),
        ImageTransformationDefinition(
            identifier="BNW/none",
            transformation=ImageTransformations.BLACK_AND_WHITE,
            filters=TransformationFiltersBlackAndWhite(
                dither=TransformationFilterDither.NONE
            ),
        ),
        ImageTransformationDefinition(
            identifier="BLUR/default",
            transformation=ImageTransformations.BLUR,
        ),
        ImageTransformationDefinition(
            identifier="BLUR/gaussian_86",
            transformation=ImageTransformations.BLUR,
            filters=TransformationFiltersBlur(
                filter=TransformationFilterBlurFilter.GAUSSIAN_BLUR,
                radius=86,
            ),
        ),
        ImageTransformationDefinition(
            identifier="BLUR/box_48",
            transformation=ImageTransformations.BLUR,
            filters=TransformationFiltersBlur(
                filter=TransformationFilterBlurFilter.BOX_BLUR,
                radius=48,
            ),
        ),
    ]
    applied_transformations = image_local_transform(
        user_id=user_id,
        image_path=file_path,
        transformations=transformations,
        parent_folder=parent_folder,
    )

    for transformation in applied_transformations:
        logger.info(f"{transformation.identifier}: {transformation.path}")


@task(queue_name="place_images")
def suggest_tags_from_uploaded_images(
    user_id: int, place_id: int, images: dict[int, str]
) -> None:
    from apps.image_processing.src.data_models import DetectorImage
    from apps.image_processing.src.detectors import CommonObjectDetector
    from apps.places.models import Place, PlaceTag

    user_place = (
        Place.objects.select_related("user")
        .prefetch_related("tags", "suggested_tags")
        .get(id=place_id)
    )
    place_tag_names = {tag.name for tag in user_place.tags.all()}

    detect_images = [
        DetectorImage(
            identifier=image_id,
            image=image_path,
        )
        for image_id, image_path in images.items()
    ]
    detector = CommonObjectDetector(images=detect_images)
    detected_objects = set()
    for result in detector.results:
        for obj in result.objects:
            if obj.name.lower() in place_tag_names:
                continue
            detected_objects.add(obj.name.lower())

    user_suggested_tags = list(
        PlaceTag.objects.filter(user_id=user_id, name__in=detected_objects)
    )

    for tag in user_suggested_tags:
        detected_objects.remove(tag.name)

    if detected_objects:
        new_suggested_tags = PlaceTag.objects.bulk_create(
            [PlaceTag(user_id=user_id, name=obj) for obj in detected_objects],
        )
        user_suggested_tags = list(user_suggested_tags) + new_suggested_tags
    user_place.suggested_tags.add(*user_suggested_tags)
