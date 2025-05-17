import inspect
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image, ImageFilter

from apps.images.processing import transformations as image_transformations
from apps.images.processing.abstract_classes import ImageTransformationCallable


def test_image_tranformation_implementation():
    for _, cls_obj in inspect.getmembers(image_transformations):
        obj_module = getattr(cls_obj, "__module__", None)
        if obj_module and cls_obj.__module__ == image_transformations.__name__:
            assert inspect.isclass(cls_obj)
            assert not inspect.ismethod(cls_obj)
            assert not inspect.ismethodwrapper(cls_obj)
            assert issubclass(cls_obj, ImageTransformationCallable)


@pytest.mark.parametrize(
    "filters, expected_filters",
    [
        (
            {},
            {
                "size": (128, 128),
                "resample": Image.Resampling.BICUBIC,
                "reducing_gap": 2,
            },
        ),
        (
            {"Bad": "Filter"},
            {
                "size": (128, 128),
                "resample": Image.Resampling.BICUBIC,
                "reducing_gap": 2,
            },
        ),
        (
            {"size": (64, 64), "resample": Image.Resampling.NEAREST, "reducing_gap": 3},
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
    "filters, expected_filters",
    [
        ({}, {"filter": ImageFilter.BLUR}),
        ({"Bad": "Filter"}, {"filter": ImageFilter.BLUR}),
        ({"filter": ImageFilter.BoxBlur(5)}, {"filter": None}),
    ],
)
@patch("PIL.Image.Image")
def test_image_generate_blur(MockImage, filters, expected_filters):
    mock_img_instance = MockImage()
    image_transformations.TransformationBlur(mock_img_instance, filters=filters)

    if expected_filters["filter"]:
        mock_img_instance.filter.assert_called_once_with(expected_filters["filter"])
    else:
        mock_img_instance.filter.assert_called_once_with(filters["filter"])


@pytest.mark.parametrize(
    "filters, expected_filters",
    [
        (
            {},
            {
                "mode": "L",
                "matrix": None,
                "dither": None,
                "palette": Image.Palette.ADAPTIVE,
                "colors": 256,
            },
        ),
        (
            {"Bad": "Filter"},
            {
                "mode": "L",
                "matrix": None,
                "dither": None,
                "palette": Image.Palette.ADAPTIVE,
                "colors": 256,
            },
        ),
        (
            {"dither": Image.Dither.FLOYDSTEINBERG},
            {
                "mode": "L",
                "matrix": None,
                "dither": Image.Dither.FLOYDSTEINBERG,
                "palette": Image.Palette.ADAPTIVE,
                "colors": 256,
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
