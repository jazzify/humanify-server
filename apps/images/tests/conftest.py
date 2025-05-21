from unittest.mock import MagicMock

import pytest
from django.conf import settings
from PIL import Image as PImage
from PIL import ImageFilter

from apps.images.processing.data_models import (
    InternalImageTransformationDefinition,
    InternalImageTransformationResult,
)
from apps.images.processing.transformations import TransformationBlur
from apps.images.processing.transformers import BaseImageTransformer


@pytest.fixture
def temp_image_file():
    """Creates a temporary image file and returns its path."""
    img = PImage.new("RGB", (60, 30), color="red")
    file_path = settings.MEDIA_ROOT / "test_image.png"
    img.save(file_path, "PNG")
    return str(file_path)


@pytest.fixture
def blur_transformation_instance():
    """Returns an instance of ImageTransformationDefinition for blur."""
    return InternalImageTransformationDefinition(
        identifier="blur_test_id",
        transformation=TransformationBlur,
        filters={"filter": ImageFilter.GaussianBlur(1)},
    )


@pytest.fixture
def mock_transformer_with_data(blur_transformation_instance):
    """Returns a mock transformer that simulates applying a transformation."""
    transformer = MagicMock(spec=BaseImageTransformer)
    dummy_transformed_image = PImage.new("RGB", (60, 30), color="blue")
    transformed_data = [
        InternalImageTransformationResult(
            identifier=blur_transformation_instance.identifier,
            image=dummy_transformed_image,
        )
    ]
    transformer.transform.return_value = transformed_data
    return transformer


@pytest.fixture
def mock_transformer_empty_result():
    """Returns a mock transformer that simulates applying no transformations."""
    transformer = MagicMock(spec=BaseImageTransformer)
    transformer.transform.return_value = []
    return transformer
