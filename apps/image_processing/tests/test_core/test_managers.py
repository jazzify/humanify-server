from unittest.mock import patch

import pytest
from django.conf import settings
from PIL import Image as PImage

from apps.image_processing.core.managers.local import (
    BaseImageManager,
    ImageLocalManager,
)
from apps.image_processing.models import ProcessingImage
from apps.image_processing.tests.factories import ProcessingImageFactory


class TestManager(BaseImageManager):
    def _get_image(self):
        return "test_image"


@pytest.mark.django_db
def test_base_image_manager_init():
    processing_image = ProcessingImageFactory()
    manager = TestManager(image=processing_image, transformer=None)
    assert manager._opened_image == "test_image"
    assert manager.get_image() == manager._opened_image


def test_base_image_manager_apply_transformations():
    processing_image = ProcessingImageFactory()
    manager = TestManager(image=processing_image, transformer=None)
    with pytest.raises(NotImplementedError):
        manager.apply_transformations()


# def test_image_loading():
#     manager = ImageLocalManager(image_path=)
#     assert isinstance(manager._opened_image, PImage.Image)
#     assert manager.get_image() == manager._opened_image

# def test_apply_transformations_with_transformer(
#     mock_transformer_with_data, blur_transformation_instance
# ):
#     manager = ImageLocalManager(
#         image_path=, transformer=mock_transformer_with_data
#     )
#     transformations_applied = manager.apply_transformations()

#     mock_transformer_with_data.transform.assert_called_once_with(
#         image=manager._opened_image
#     )
#     assert len(transformations_applied) == 1
#     assert (
#         transformations_applied[0].identifier
#         == blur_transformation_instance.identifier
#     )
#     assert isinstance(transformations_applied[0].image, PImage.Image)

# def test_apply_transformations_without_transformer():
#     manager = ImageLocalManager(image_path=, transformer=None)
#     with pytest.raises(NotImplementedError):
#         manager.apply_transformations()
