from dataclasses import asdict, dataclass
from typing import Type

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
    ExternalImageTransformationDefinition,
    InternalImageTransformationDefinition,
)
from apps.image_processing.models import ImageTransformation


@dataclass
class InternalTransformationMapper:
    transformation: Type[InternalImageTransformation]
    filters: ExternalTransformationFilters


def transformations_mapper(
    transformation_name: str,
    filters: ExternalTransformationFilters | None = None,
) -> InternalTransformationMapper:
    """
    Maps an external transformation definition to an internal transformation.

    Args:
        transformation_name (str): The name of the transformation.
        filters (ExternalTransformationFilters | None, optional):
            The filters to apply to the transformation. Defaults to None.

    Returns:
        InternalTransformationMapper: The internal transformation with the corresponding filters.
    """

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
        transformation=transformation_map["transformation"],  # type: ignore[arg-type]
        filters=transformation_map["filters"](**dict_filters),
    )


def get_internal_transformations(
    external_transformations: list[ExternalImageTransformationDefinition],
) -> list[InternalImageTransformationDefinition]:
    """
    Converts a list of external transformation definitions to a list of internal transformation definitions.

    Args:
        external_transformations (list[ExternalImageTransformationDefinition]):
            A list of external transformation definitions.

    Returns:
        list[InternalImageTransformationDefinition]:
            A list of internal transformation definitions.
    """

    dataclasses = []
    for transform in external_transformations:
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
