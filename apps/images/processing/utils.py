from apps.images.constants import ImageTransformations
from apps.images.data_models import ImageTransformationDataClass
from apps.images.processing.data_models import ImageProcessingTransformationDataClass
from apps.images.processing.transformations import (
    ImageTransformationCallable,
    TransformationBlackAndWhite,
    TransformationBlur,
    TransformationThumbnail,
)


def get_transformation_dataclasses(
    transformations: list[ImageTransformationDataClass],
) -> list[ImageProcessingTransformationDataClass]:
    dataclasses = []
    for transformation in transformations:
        dataclasses.append(
            ImageProcessingTransformationDataClass(
                identifier=transformation.identifier,
                transformation=get_transformation_callable(
                    transformation.transformation
                ),
                filters=transformation.filters,
            )
        )
    return dataclasses


def get_transformation_callable(
    transformation: ImageTransformations,
) -> type[ImageTransformationCallable]:
    return {
        ImageTransformations.THUMBNAIL: TransformationThumbnail,
        ImageTransformations.BLUR: TransformationBlur,
        ImageTransformations.BLACK_AND_WHITE: TransformationBlackAndWhite,
    }[transformation]
