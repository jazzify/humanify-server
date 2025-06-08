from dataclasses import asdict, dataclass
from typing import Type

from apps.image_processing.constants import TRANSFORMATIONS_MULTIPROCESS_TRESHOLD
from apps.image_processing.core.transformations.base import (
    ExternalTransformationFilters,
    InternalImageTransformation,
)
from apps.image_processing.core.transformations.black_and_white import (
    ExternalTransformationFiltersBlackAndWhite,
    TransformationBlackAndWhite,
)
from apps.image_processing.core.transformations.blur import (
    ExternalTransformationFiltersBlur,
    TransformationBlur,
)
from apps.image_processing.core.transformations.thumbnail import (
    ExternalTransformationFiltersThumbnail,
    TransformationThumbnail,
)
from apps.image_processing.core.transformers.base import (
    BaseImageTransformer,
    InternalImageTransformationDefinition,
)
from apps.image_processing.core.transformers.chain import ImageChainTransformer
from apps.image_processing.core.transformers.multiprocess import (
    ImageMultiProcessTransformer,
)
from apps.image_processing.core.transformers.sequential import (
    ImageSequentialTransformer,
)
from apps.image_processing.models import ImageTransformation
from apps.image_processing_api.data_models import ImageTransformationDefinition


@dataclass
class InternalTransformationMapper:
    transformation: Type[InternalImageTransformation]
    filters: ExternalTransformationFilters


def transformations_mapper(
    transformation_name: str,
    filters: ExternalTransformationFilters | None = None,
) -> InternalTransformationMapper:
    dict_filters = {}
    if filters:
        dict_filters = asdict(filters)
    else:
        dict_filters = {}

    _mapper = {
        ImageTransformation.THUMBNAIL: {
            "transformation": TransformationThumbnail,
            "filters": ExternalTransformationFiltersThumbnail,
        },
        ImageTransformation.BLUR: {
            "transformation": TransformationBlur,
            "filters": ExternalTransformationFiltersBlur,
        },
        ImageTransformation.BLACK_AND_WHITE: {
            "transformation": TransformationBlackAndWhite,
            "filters": ExternalTransformationFiltersBlackAndWhite,
        },
    }

    transformation_map = _mapper[transformation_name]
    return InternalTransformationMapper(
        # TODO: search for a better way to handle typing here?
        transformation=transformation_map["transformation"],  # type: ignore[arg-type] # don't know why its complaining
        filters=transformation_map["filters"](**dict_filters),
    )


def get_transformation_dataclasses(
    transformations: list[ImageTransformationDefinition],
) -> list[InternalImageTransformationDefinition]:
    dataclasses = []
    for transform in transformations:
        mapper = transformations_mapper(
            transformation_name=transform.transformation, filters=transform.filters
        )
        dataclasses.append(
            InternalImageTransformationDefinition(
                identifier=transform.identifier,
                transformation=mapper.transformation,
                filters=mapper.filters,
            )
        )
    return dataclasses


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
