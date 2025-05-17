from django_tasks import task


@task(queue_name="place_images")
def transform_uploaded_images(
    file_path: str, root_folder: str, parent_folder: str
) -> None:
    from PIL import ImageFilter

    from apps.images.constants import ImageTransformations
    from apps.images.data_models import ImageTransformationDataClass
    from apps.images.services import ImageTransformationService

    transformations = [
        ImageTransformationDataClass(
            name=ImageTransformations.THUMBNAIL,
            filters={"size": (64, 64)},
        ),
        ImageTransformationDataClass(name=ImageTransformations.THUMBNAIL),
        ImageTransformationDataClass(
            name=ImageTransformations.THUMBNAIL,
            filters={"size": (320, 320)},
        ),
        ImageTransformationDataClass(name=ImageTransformations.BLACK_AND_WHITE),
        ImageTransformationDataClass(
            name=ImageTransformations.BLACK_AND_WHITE,
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
            name=ImageTransformations.BLUR,
            filters={"filter": ImageFilter.GaussianBlur(48)},
        ),
        ImageTransformationDataClass(
            name=ImageTransformations.BLUR, filters={"filter": ImageFilter.BoxBlur(48)}
        ),
    ]

    image_service = ImageTransformationService(
        image_path=file_path,
        root_folder=root_folder,
        parent_folder=parent_folder,
        transformations=transformations,
    )
    image_service.apply_transformations()
