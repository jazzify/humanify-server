from typing import Any

from django.core.files.images import ImageFile

from apps.image_processing.models import Image
from apps.image_processing_api.tasks import transform_uploaded_images
from apps.users.models import BaseUser


def image_processing_create(user: BaseUser, images: list[ImageFile]) -> list[Image]:
    return Image.objects.bulk_create([Image(user=user, file=image) for image in images])


def image_processing_transform(
    user: BaseUser,
    image_ids: list[int],
    transformations: list[dict[str, Any]],
    is_chain: bool = False,
) -> list[dict[str, Any]]:
    images = Image.objects.select_related("user").filter(user=user, id__in=image_ids)

    tasks_results = []
    for image in images:
        task = transform_uploaded_images.enqueue(
            user_id=user.id,
            file_path=image.file.path,
            parent_folder=str(image.id),
            transformations=transformations,
            is_chain=is_chain,
        )
        tasks_results.append(
            {"id": image.id, "task_id": task.id, "task_status": task.status}
        )
    return tasks_results
