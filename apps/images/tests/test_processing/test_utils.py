import pytest
from PIL import Image as PImage
from PIL import ImageFilter

from apps.images.constants import ImageTransformations
from apps.images.data_models import ImageTransformationDefinition
from apps.images.processing import utils
from apps.images.processing.data_models import (
    InternalTransformationFiltersBlackAndWhite,
    InternalTransformationFiltersBlur,
    InternalTransformationFiltersThumbnail,
    InternalTransformationMapper,
)
from apps.images.processing.transformations import (
    TransformationBlackAndWhite,
    TransformationBlur,
    TransformationThumbnail,
)


@pytest.mark.parametrize(
    "transformation, expected_callable",
    [
        (
            ImageTransformations.THUMBNAIL,
            InternalTransformationMapper(
                transformation=TransformationThumbnail,
                filters=InternalTransformationFiltersThumbnail(
                    size=(128, 128), resample=PImage.Resampling.BICUBIC, reducing_gap=2
                ),
            ),
        ),
        (
            ImageTransformations.BLUR,
            InternalTransformationMapper(
                transformation=TransformationBlur,
                filters=InternalTransformationFiltersBlur(filter=ImageFilter.BLUR()),
            ),
        ),
        (
            ImageTransformations.BLACK_AND_WHITE,
            InternalTransformationMapper(
                transformation=TransformationBlackAndWhite,
                filters=InternalTransformationFiltersBlackAndWhite(
                    dither=PImage.Dither.FLOYDSTEINBERG
                ),
            ),
        ),
    ],
)
def test_transformations_mapper(transformation, expected_callable):
    mapper = utils.transformations_mapper(transformation)

    if transformation == ImageTransformations.BLUR:
        assert mapper.transformation == expected_callable.transformation
        assert isinstance(mapper.filters, expected_callable.filters.__class__)
    else:
        assert mapper == expected_callable


def test_transformations_mapper_invalid():
    with pytest.raises(KeyError):
        utils.transformations_mapper("INVALID_TRANSFORMATION")


def test_get_transformation_dataclasses_empty():
    result_dataclasses = utils.get_transformation_dataclasses([])
    assert result_dataclasses == []


def test_get_transformation_dataclasses_callable_mock():
    mock_transformation_data = [
        ImageTransformationDefinition(
            identifier="test1",
            transformation=ImageTransformations.THUMBNAIL,
            filters=None,
        )
    ]

    result_dataclasses = utils.get_transformation_dataclasses(mock_transformation_data)

    assert len(result_dataclasses) == 1
    assert result_dataclasses[0].filters == InternalTransformationFiltersThumbnail(
        size=(128, 128), resample=PImage.Resampling.BICUBIC, reducing_gap=2
    )
    assert result_dataclasses[0].identifier == "test1"
