import inspect
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image, ImageFilter

from apps.image_processing.src import transformations as image_transformations
from apps.image_processing.src.data_models import (
    InternalImageTransformation,
    InternalTransformationFiltersBlackAndWhite,
    InternalTransformationFiltersBlur,
    InternalTransformationFiltersThumbnail,
)


def test_image_transformation_callable_not_implemented():
    mock_img_instance = MagicMock()
    file_name = "thumbnail.png"

    class TestNewTransformation(InternalImageTransformation):
        pass

    with pytest.raises(TypeError):
        TestNewTransformation(mock_img_instance, file_name)


def test_image_tranformation_implementation():
    for _, cls_obj in inspect.getmembers(image_transformations):
        obj_module = getattr(cls_obj, "__module__", None)
        if obj_module and cls_obj.__module__ == image_transformations.__name__:
            assert inspect.isclass(cls_obj)
            assert not inspect.ismethod(cls_obj)
            assert not inspect.ismethodwrapper(cls_obj)
            assert issubclass(cls_obj, InternalImageTransformation)


@pytest.mark.parametrize(
    "filters, expected_filters",
    [
        (
            InternalTransformationFiltersThumbnail(
                size=(420, 420), reducing_gap=None, resample=Image.Resampling.BICUBIC
            ),
            {
                "size": (420, 420),
                "resample": Image.Resampling.BICUBIC,
                "reducing_gap": None,
            },
        ),
        (
            InternalTransformationFiltersThumbnail(
                size=(64, 64), reducing_gap=3, resample=Image.Resampling.NEAREST
            ),
            {"size": (64, 64), "resample": Image.Resampling.NEAREST, "reducing_gap": 3},
        ),
    ],
)
@patch("PIL.Image.Image")
def test_image_generate_thumbnail(MockImage, filters, expected_filters):
    mock_img_instance = MockImage()
    mock_img_copy = mock_img_instance.copy.return_value = MagicMock()
    image_transformations.TransformationThumbnail(mock_img_instance, filters=filters)
    mock_img_copy.thumbnail.assert_called_once_with(**expected_filters)


@pytest.mark.parametrize(
    "filters",
    [
        InternalTransformationFiltersBlur(filter=ImageFilter.BLUR),
        InternalTransformationFiltersBlur(filter=ImageFilter.BoxBlur(5)),
        InternalTransformationFiltersBlur(filter=ImageFilter.GaussianBlur(42)),
    ],
)
@patch("PIL.Image.Image")
def test_image_generate_blur(MockImage, filters):
    mock_img_instance = MockImage()
    image_transformations.TransformationBlur(mock_img_instance, filters=filters)
    mock_img_instance.filter.assert_called_once_with(filters.filter)


@pytest.mark.parametrize(
    "filters, expected_filters",
    [
        (
            InternalTransformationFiltersBlackAndWhite(
                dither=Image.Dither.FLOYDSTEINBERG
            ),
            {
                "mode": "1",
                "dither": Image.Dither.FLOYDSTEINBERG,
            },
        ),
        (
            InternalTransformationFiltersBlackAndWhite(dither=Image.Dither.NONE),
            {
                "mode": "1",
                "dither": Image.Dither.NONE,
            },
        ),
        (
            InternalTransformationFiltersBlackAndWhite(dither=None),
            {
                "mode": "1",
                "dither": None,
            },
        ),
    ],
)
@patch("PIL.Image.Image")
def test_image_generate_black_and_white(MockImage, filters, expected_filters):
    mock_img_instance = MockImage()
    image_transformations.TransformationBlackAndWhite(
        mock_img_instance, filters=filters
    )
    mock_img_instance.convert.assert_called_once_with(**expected_filters)
