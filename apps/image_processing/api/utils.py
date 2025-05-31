from dataclasses import asdict
from typing import Type

from apps.image_processing.api.constants import (
    TRANSFORMATIONS_MULTIPROCESS_TRESHOLD,
    ImageTransformations,
)
from apps.image_processing.api.data_models import (
    ImageTransformationDefinition,
    TransformationFilters,
    TransformationFiltersBlackAndWhite,
    TransformationFiltersBlur,
    TransformationFiltersThumbnail,
)
from apps.image_processing.src.data_models import (
    InternalImageTransformationDefinition,
    InternalTransformationMapper,
)
from apps.image_processing.src.transformations import (
    TransformationBlackAndWhite,
    TransformationBlur,
    TransformationThumbnail,
)
from apps.image_processing.src.transformers import (
    BaseImageTransformer,
    ImageChainTransformer,
    ImageMultiProcessTransformer,
    ImageSequentialTransformer,
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
        # TODO: search for a better way to handle typing here?
        transformation=transformation_map["transformation"],  # type: ignore[arg-type] # don't know why its complaining
        filters=transformation_map["filters"](**dict_filters).to_internal(),
    )


def get_local_transformer(
    transformations: list[InternalImageTransformationDefinition],
    is_chain: bool = False,
) -> BaseImageTransformer:
    transformer: Type[BaseImageTransformer] = ImageSequentialTransformer
    if is_chain:
        transformer = ImageChainTransformer
    elif len(transformations) >= TRANSFORMATIONS_MULTIPROCESS_TRESHOLD:
        transformer = ImageMultiProcessTransformer

    return transformer(transformations=transformations)


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
