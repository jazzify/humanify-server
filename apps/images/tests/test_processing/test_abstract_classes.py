from typing import Any
from unittest.mock import MagicMock

import pytest
from PIL import Image as PImage

from apps.images.processing.abstract_classes import ImageTransformationCallable


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
            return image(**filters)

    transformation = TestNewTransformation(mock_img_instance, filters={})

    transformation.image_transformed.save.assert_not_called()
