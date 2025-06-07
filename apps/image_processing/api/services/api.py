from django.core.files.images import ImageFile

from apps.image_processing.models import Image
from apps.users.models import BaseUser


def image_processing_create(user: BaseUser, images: list[ImageFile]) -> list[Image]:
    return Image.objects.bulk_create([Image(user=user, file=image) for image in images])
