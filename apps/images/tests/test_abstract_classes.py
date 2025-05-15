from unittest.mock import MagicMock

import pytest

from apps.images.abstract_classes import ImageTransformationCallable


def test_image_transformation_callable_not_implemented():
    mock_img_instance = MagicMock()
    file_name = "thumbnail.png"

    class TestNewTransformation(ImageTransformationCallable):
        pass

    with pytest.raises(TypeError):
        TestNewTransformation(mock_img_instance, file_name)
