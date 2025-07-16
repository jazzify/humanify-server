from apps.image_processing.core.transformations.base import (
    ExternalTransformationFilters,
    InternalImageTransformation,
)
from apps.image_processing.utils import (
    get_internal_transformations,
    transformations_mapper,
)


def test_get_internal_transformations(
    external_image_transformations,
):
    internal_transformations = get_internal_transformations(
        external_image_transformations
    )
    _identifiers = [
        transform.identifier for transform in external_image_transformations
    ]
    for transformation in internal_transformations:
        assert issubclass(transformation.transformation, InternalImageTransformation)
        assert issubclass(
            transformation.filters.__class__, ExternalTransformationFilters
        )
        assert transformation.identifier in _identifiers
    assert len(internal_transformations) == len(external_image_transformations)


def test_transformations_mapper(external_image_transformations):
    for transform in external_image_transformations:
        mapper = transformations_mapper(
            transformation_name=transform.transformation, filters=transform.filters
        )
        assert issubclass(mapper.transformation, InternalImageTransformation)
        assert issubclass(mapper.filters.__class__, ExternalTransformationFilters)
