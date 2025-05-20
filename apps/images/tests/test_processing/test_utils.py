from unittest.mock import MagicMock, patch

import pytest

from apps.images.constants import ImageTransformations
from apps.images.data_models import ImageTransformationDataClass
from apps.images.processing import utils
from apps.images.processing.data_models import ImageProcessingTransformationDataClass
from apps.images.processing.transformations import (
    InternalImageTransformation,
    TransformationBlackAndWhite,
    TransformationBlur,
    TransformationThumbnail,
)


@pytest.mark.parametrize(
    "transformation, expected_callable",
    [
        (ImageTransformations.THUMBNAIL, TransformationThumbnail),
        (ImageTransformations.BLUR, TransformationBlur),
        (ImageTransformations.BLACK_AND_WHITE, TransformationBlackAndWhite),
    ],
)
def test_get_transformation_callable(transformation, expected_callable):
    callable_class = utils.get_transformation_callable(transformation)
    assert callable_class == expected_callable
    assert issubclass(callable_class, InternalImageTransformation)


def test_get_transformation_callable_invalid():
    with pytest.raises(KeyError):
        utils.get_transformation_callable("INVALID_TRANSFORMATION")


def test_get_transformation_dataclasses():
    mock_transformation_data = [
        ImageTransformationDataClass(
            identifier="thumb1",
            transformation=ImageTransformations.THUMBNAIL,
            filters={"size": (50, 50)},
        ),
        ImageTransformationDataClass(
            identifier="blur1",
            transformation=ImageTransformations.BLUR,
            filters={"radius": 2},
        ),
    ]

    result_dataclasses = utils.get_transformation_dataclasses(mock_transformation_data)

    assert len(result_dataclasses) == 2

    # Check first dataclass
    assert isinstance(result_dataclasses[0], ImageProcessingTransformationDataClass)
    assert result_dataclasses[0].identifier == "thumb1"
    assert result_dataclasses[0].transformation == TransformationThumbnail
    assert result_dataclasses[0].filters == {"size": (50, 50)}

    # Check second dataclass
    assert isinstance(result_dataclasses[1], ImageProcessingTransformationDataClass)
    assert result_dataclasses[1].identifier == "blur1"
    assert result_dataclasses[1].transformation == TransformationBlur
    assert result_dataclasses[1].filters == {"radius": 2}


def test_get_transformation_dataclasses_empty():
    result_dataclasses = utils.get_transformation_dataclasses([])
    assert result_dataclasses == []


@patch("apps.images.processing.utils.get_transformation_callable")
def test_get_transformation_dataclasses_callable_mock(mock_get_callable):
    mock_callable_instance = MagicMock()
    mock_get_callable.return_value = mock_callable_instance

    mock_transformation_data = [
        ImageTransformationDataClass(
            identifier="test1",
            transformation=ImageTransformations.THUMBNAIL,
            filters={},
        )
    ]

    result_dataclasses = utils.get_transformation_dataclasses(mock_transformation_data)

    mock_get_callable.assert_called_once_with(ImageTransformations.THUMBNAIL)
    assert len(result_dataclasses) == 1
    assert result_dataclasses[0].transformation == mock_callable_instance
