import logging

from django_tasks import task

logger = logging.getLogger(__name__)


@task(queue_name="place_images")
def suggest_tags_from_uploaded_images(
    user_id: int, place_id: int, images: dict[int, str]
) -> None:
    from apps.image_processing.core.detectors.base import DetectorImage
    from apps.image_processing.core.detectors.common_object_detector import (
        CommonObjectDetector,
    )
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
