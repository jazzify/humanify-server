import logging

from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.db.models import QuerySet

from apps.places.constants import PLACE_IMAGES_LIMIT
from apps.places.models import Place, PlaceImage, PlaceTag
from apps.places.tasks import (
    suggest_tags_from_uploaded_images,
    transform_uploaded_images,
)
from apps.users.models import BaseUser

logger = logging.getLogger(__name__)


def place_retrieve_all_by_user(user: BaseUser) -> QuerySet[Place]:
    return (
        Place.objects.select_related(
            "user",
        )
        .prefetch_related("images", "tags", "suggested_tags")
        .filter(user=user)
    )


def place_create(
    user: BaseUser,
    name: str,
    city: str,
    latitude: float,
    longitude: float,
    tag_names: list[str] | None = None,
    favorite: bool = False,
    description: str | None = None,
) -> Place:
    place: Place = Place.objects.create(
        user=user,
        name=name,
        city=city,
        latitude=latitude,
        longitude=longitude,
        favorite=favorite,
        description=description,
    )

    if tag_names:
        place_tags = [
            PlaceTag.objects.get_or_create(user=user, name=tag)[0] for tag in tag_names
        ]
        place.tags.add(*place_tags)

    return place


def place_retrieve_by_id_and_user(place_id: int, user: BaseUser) -> Place:
    try:
        return (
            Place.objects.select_related(
                "user",
            )
            .prefetch_related("images", "tags", "suggested_tags")
            .get(id=place_id, user=user)
        )
    except Place.DoesNotExist as e:
        raise ValidationError(
            {
                "place_id": [
                    f"Place with id {place_id} does not exist for user {user.email}"
                ]
            }
        )


def place_delete_by_id_and_user(place_id: int, user: BaseUser) -> None:
    try:
        Place.objects.select_related(
            "user",
        ).get(id=place_id, user=user).delete()
    except Place.DoesNotExist as e:
        raise ValidationError(
            {
                "place_id": [
                    f"Place with id {place_id} does not exist for user {user.email}"
                ]
            }
        )


def place_images_create(
    user: BaseUser, place_id: int, images: list[ImageFile]
) -> list[PlaceImage]:
    try:
        current_place_images = PlaceImage.objects.filter(place_id=place_id).count()
        if (len(images) + current_place_images) > PLACE_IMAGES_LIMIT:
            raise ValidationError(
                {
                    "files": [
                        f"A place cannot have more than {PLACE_IMAGES_LIMIT} images."
                    ]
                }
            )

        created_place_images = []
        images_for_detection: dict[int, str] = {}
        for image in images:
            place_image = PlaceImage(place_id=place_id, image=image)
            place_image.full_clean()
            place_image.save()
            images_for_detection[place_image.id] = place_image.image.path
            created_place_images.append(place_image)

            transform_uploaded_images.enqueue(
                user_id=user.id,
                file_path=place_image.image.path,
                parent_folder=str(place_image.id),
            )
        suggest_tags_from_uploaded_images.enqueue(
            user_id=user.id,
            place_id=place_id,
            images=images_for_detection,
        )

        return created_place_images

    except Place.DoesNotExist as e:
        raise ValidationError(
            {"place_id": [f"Place with id {place_id} does not exist"]}
        )
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f"Unhandled exception in place_images_create: {e}")
        raise e


def place_images_retrive_by_place_id_and_user(
    place_id: int, user: BaseUser
) -> QuerySet[PlaceImage]:
    return PlaceImage.objects.select_related(
        "place",
    ).filter(place_id=place_id, place__user=user)
