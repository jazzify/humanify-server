from unittest.mock import MagicMock, patch

import pytest
from PIL import Image, ImageFilter

from apps.image_processing.constants import (
    TRANSFORMATION_FILTER_BLUR_FILTER,
    TRANSFORMATION_FILTER_DITHER,
    TRANSFORMATION_FILTER_THUMBNAIL_RESAMPLING,
)
from apps.image_processing.core.transformations.base import (
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


def test_image_transformation_callable_not_implemented():
    mock_img_instance = MagicMock()
    file_name = "thumbnail.png"

    class TestNewTransformation(InternalImageTransformation):
        pass

    with pytest.raises(TypeError):
        TestNewTransformation(mock_img_instance, file_name)


@pytest.mark.parametrize(
    "filters, expected_filters",
    [
        (
            ExternalTransformationFiltersThumbnail(
                size=(420, 420),
                reducing_gap=None,
                resample=TRANSFORMATION_FILTER_THUMBNAIL_RESAMPLING.BICUBIC,
            ),
            {
                "size": (420, 420),
                "resample": Image.Resampling.BICUBIC,
                "reducing_gap": None,
            },
        ),
        (
            ExternalTransformationFiltersThumbnail(
                size=(64, 64),
                reducing_gap=3,
                resample=TRANSFORMATION_FILTER_THUMBNAIL_RESAMPLING.NEAREST,
            ),
            {"size": (64, 64), "resample": Image.Resampling.NEAREST, "reducing_gap": 3},
        ),
    ],
)
@patch("PIL.Image.Image")
def test_image_generate_thumbnail(MockImage, filters, expected_filters):
    mock_img_instance = MockImage()
    mock_img_copy = mock_img_instance.copy.return_value = MagicMock()
    TransformationThumbnail(mock_img_instance, filters=filters)
    mock_img_copy.thumbnail.assert_called_once_with(**expected_filters)


@pytest.mark.parametrize(
    "filters, expected_filters",
    [
        (
            ExternalTransformationFiltersBlur(
                filter=TRANSFORMATION_FILTER_BLUR_FILTER.BLUR,
                radius=20,
            ),
            ImageFilter.BLUR(),
        ),
        (
            ExternalTransformationFiltersBlur(
                filter=TRANSFORMATION_FILTER_BLUR_FILTER.BOX_BLUR
            ),
            ImageFilter.BoxBlur(10.0),
        ),
        (
            ExternalTransformationFiltersBlur(
                filter=TRANSFORMATION_FILTER_BLUR_FILTER.GAUSSIAN_BLUR,
                radius=200,
            ),
            ImageFilter.GaussianBlur(200.0),
        ),
    ],
)
@patch("PIL.Image.Image")
def test_image_generate_blur(MockImage, filters, expected_filters):
    mock_img_instance = MockImage()
    TransformationBlur(mock_img_instance, filters=filters)
    if hasattr(expected_filters, "radius"):
        assert filters.to_internal().filter.radius
    mock_img_instance.filter.assert_called_once()


@pytest.mark.parametrize(
    "filters, expected_filters",
    [
        (
            ExternalTransformationFiltersBlackAndWhite(
                dither=TRANSFORMATION_FILTER_DITHER.FLOYDSTEINBERG
            ),
            {
                "mode": "L",
                "dither": Image.Dither.FLOYDSTEINBERG,
            },
        ),
        (
            ExternalTransformationFiltersBlackAndWhite(
                dither=TRANSFORMATION_FILTER_DITHER.NONE
            ),
            {
                "mode": "L",
                "dither": Image.Dither.NONE,
            },
        ),
        (
            ExternalTransformationFiltersBlackAndWhite(dither=None),
            {
                "mode": "L",
                "dither": None,
            },
        ),
    ],
)
@patch("PIL.Image.Image")
def test_image_generate_black_and_white(MockImage, filters, expected_filters):
    mock_img_instance = MockImage()
    TransformationBlackAndWhite(mock_img_instance, filters=filters)
    mock_img_instance.convert.assert_called_once_with(**expected_filters)
