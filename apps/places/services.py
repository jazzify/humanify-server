import logging

from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.db.models import QuerySet

from apps.places.constants import PLACE_IMAGES_LIMIT
from apps.places.models import Place, PlaceImage, PlaceTag
from apps.places.tasks import process_uploaded_images
from apps.users.models import BaseUser

logger = logging.getLogger(__name__)


def get_all_places_by_user(user: BaseUser) -> QuerySet[Place]:
    return (
        Place.objects.select_related(
            "user",
        )
        .prefetch_related("images", "tags")
        .filter(user=user)
    )


def create_place(
    user: BaseUser,
    name: str,
    city: str,
    latitude: float,
    longitude: float,
    tag_names: list[str] | None = None,
    favorite: bool | None = False,
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


def create_place_images(place_id: int, images: list[ImageFile]) -> list[PlaceImage]:
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

        for image in images:
            place_image = PlaceImage(place_id=place_id, image=image)
            place_image.full_clean
            place_image.save()
            created_place_images.append(place_image)

            process_uploaded_images.enqueue(
                file_path=place_image.image.path,
                root_folder="place_images",
                parent_folder=str(place_image.id),
            )

        return created_place_images

    except Place.DoesNotExist as e:
        raise ValidationError(
            {"place_id": [f"Place with id {place_id} does not exist"]}
        )
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f"Unhandled exception in create_place_images: {e}")
        raise e
