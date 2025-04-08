from django.db.models import QuerySet

from apps.places.models import Place, PlaceImage, PlaceTag
from apps.users.models import BaseUser


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
    images: list[str] | None = None,
    favorite: bool | None = False,
    description: str | None = None,
) -> Place:
    place = Place.objects.create(
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

    if images:
        PlaceImage.objects.bulk_create(
            [PlaceImage(place=place, image=image) for image in images]
        )

    return place
