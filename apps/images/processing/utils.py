from dataclasses import asdict

from apps.images.constants import ImageTransformations
from apps.images.data_models import (
    ImageTransformationDefinition,
    TransformationFilters,
    TransformationFiltersBlackAndWhite,
    TransformationFiltersBlur,
    TransformationFiltersThumbnail,
)
from apps.images.processing.data_models import (
    InternalImageTransformationDefinition,
    InternalTransformationMapper,
)
from apps.images.processing.transformations import (
    TransformationBlackAndWhite,
    TransformationBlur,
    TransformationThumbnail,
)


def transformations_mapper(
    transformation: ImageTransformations,
    filters: TransformationFilters | None = None,
) -> InternalTransformationMapper:
    dict_filters = {}
    if filters:
        dict_filters = asdict(filters)
    else:
        dict_filters = {}

    _mapper = {
        ImageTransformations.THUMBNAIL: {
            "transformation": TransformationThumbnail,
            "filters": TransformationFiltersThumbnail,
        },
        ImageTransformations.BLUR: {
            "transformation": TransformationBlur,
            "filters": TransformationFiltersBlur,
        },
        ImageTransformations.BLACK_AND_WHITE: {
            "transformation": TransformationBlackAndWhite,
            "filters": TransformationFiltersBlackAndWhite,
        },
    }

    transformation_map = _mapper[transformation]
    return InternalTransformationMapper(
        transformation=transformation_map["transformation"],  # type: ignore[arg-type] # don't know why its complaining
        filters=transformation_map["filters"](**dict_filters).to_internal(),
    )


def get_transformation_dataclasses(
    transformations: list[ImageTransformationDefinition],
) -> list[InternalImageTransformationDefinition]:
    dataclasses = []
    for transform in transformations:
        mapper = transformations_mapper(
            transformation=transform.transformation, filters=transform.filters
        )
        dataclasses.append(
            InternalImageTransformationDefinition(
                identifier=transform.identifier,
                transformation=mapper.transformation,
                filters=mapper.filters,
            )
        )
    return dataclasses
