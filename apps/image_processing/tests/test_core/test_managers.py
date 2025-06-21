from unittest.mock import patch

import pytest
from PIL import Image as PImage

from apps.image_processing.core.managers.base import (
    BaseImageManager,
)
from apps.image_processing.core.managers.local import ImageLocalManager
from apps.image_processing.core.transformers.base import BaseImageTransformer
from apps.image_processing.core.transformers.sequential import (
    ImageSequentialTransformer,
)
from apps.image_processing.models import TransformationBatch


class ImageProcesingTestManager(BaseImageManager):
    def _get_image(self):
        return PImage.new("RGB", (60, 30), color="red")


class ImageProcessingTestTransformer(BaseImageTransformer):
    name = "test_transformer"

    def _transform(self, image: PImage.Image):
        return image


@pytest.mark.django_db
def test_base_image_manager_init(processing_image_base):
    with patch.object(ImageProcesingTestManager, "_get_image") as mock_get_image:
        manager = ImageProcesingTestManager(
            image=processing_image_base, transformer=None
        )
        assert manager.get_image() == manager._opened_image
    mock_get_image.assert_called_once_with()


@pytest.mark.django_db
def test_apply_transformations_without_transformer(processing_image_base):
    manager = ImageProcesingTestManager(image=processing_image_base, transformer=None)
    with pytest.raises(NotImplementedError):
        manager.apply_transformations()


@pytest.mark.django_db
def test_apply_transformations_with_transformer(
    processing_image_base,
    image_transformations,
):
    transformer = ImageSequentialTransformer(transformations=image_transformations)
    manager = ImageProcesingTestManager(
        image=processing_image_base, transformer=transformer
    )
    transformations_applied = manager.apply_transformations()
    transformation_batch = TransformationBatch.objects.first()

    assert TransformationBatch.objects.count() == 1
    assert transformation_batch.input_image == processing_image_base
    assert transformation_batch.transformer == transformer.name
    assert len(transformations_applied) == len(image_transformations)
    assert transformations_applied[0].identifier == image_transformations[0].identifier
    assert isinstance(transformations_applied[0].image, PImage.Image)


@pytest.mark.django_db
@patch("apps.image_processing.core.managers.local.PImage")
def test_local_image_manager_get_image(mock_pimage, processing_image_base):
    manager = ImageLocalManager(image=processing_image_base)
    manager.get_image()
    mock_pimage.open.assert_called_once_with(processing_image_base.file.path)
