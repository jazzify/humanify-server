from typing import Any
from unittest.mock import MagicMock

import pytest
from PIL import Image as PImage

from apps.images.abstract_classes import ImageTransformationCallable


def test_image_transformation_callable_not_implemented():
    mock_img_instance = MagicMock()
    file_name = "thumbnail.png"

    class TestNewTransformation(ImageTransformationCallable):
        pass

    with pytest.raises(TypeError):
        TestNewTransformation(mock_img_instance, file_name)


def test_image_transformation_init():
    mock_img_instance = MagicMock()
    relative_path = "test/"

    class TestNewTransformation(ImageTransformationCallable):
        def _image_transform(
            self, image: PImage.Image, filters: dict[str, Any]
        ) -> PImage.Image:
            return image

    transformation = TestNewTransformation(
        mock_img_instance, filters={}, relative_path=relative_path
    )

    transformation.image_transformed.save.assert_called_once()
    save_args, _ = transformation.image_transformed.save.call_args

    assert save_args[0].startswith(relative_path)


def test_image_transformation_init_validations():
    mock_img_instance = MagicMock()

    class TestNewTransformation(ImageTransformationCallable):
        def _image_transform(
            self, image: PImage.Image, filters: dict[str, Any]
        ) -> PImage.Image:
            return PImage.new("RGB", (100, 100))

    with pytest.raises(ValueError):
        TestNewTransformation(mock_img_instance, filters={}, local_persist=True)
