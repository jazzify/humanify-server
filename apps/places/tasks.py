from django_tasks import task


@task(queue_name="place_images")
def process_uploaded_images(
    file_path: str, root_folder: str, parent_folder: str
) -> None:
    from apps.images.constants import ImageTransformations
    from apps.images.services import ImageTransformationService

    image_service = ImageTransformationService(
        image_path=file_path,
        root_folder=root_folder,
        parent_folder=parent_folder,
        transformations=[transformation for transformation in ImageTransformations],
    )
    image_service.apply_transformations()
