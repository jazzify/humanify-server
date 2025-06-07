from unittest.mock import MagicMock, patch

import pytest

from apps.image_processing.core.managers import ImageLocalManager
from apps.image_processing.data_models import InternalImageTransformationResult
from apps.image_processing.models import (
    ImageTransformation,
    ProcessedImage,
    ProcessingImage,
    TransformationBatch,
)
from apps.image_processing.services import (
    image_local_transform,
    image_processing_save_procedure,
)
from apps.image_processing_api.constants import ImageTransformations
from apps.image_processing_api.data_models import (
    ImageTransformationDefinition,
    TransformationFiltersThumbnail,
)


@pytest.fixture
def mock_get_transformation_dataclasses():
    with patch("apps.image_processing.services.get_transformation_dataclasses") as mock:
        mock.return_value = [MagicMock(), MagicMock()]
        yield mock


@pytest.fixture
def mock_get_local_transformer():
    with patch("apps.image_processing.services.get_local_transformer") as mock:
        mock_transformer_instance = MagicMock()
        mock.return_value = mock_transformer_instance
        yield mock


@pytest.fixture
def mock_image_local_manager():
    with patch("apps.image_processing.services.ImageLocalManager") as mock:
        mock_manager_instance = MagicMock()
        mock_manager_instance.apply_transformations = MagicMock()
        mock_manager_instance.get_file.return_value = 1
        mock_manager_instance.save.return_value = {
            "transformed_image.png": "/path/to/transformed_image.png"
        }
        mock.return_value = mock_manager_instance
        yield mock


@patch("apps.image_processing.services.image_processing_save_procedure")
def test_image_local_transform(
    mock_image_processing_save_procedure,
    mock_get_transformation_dataclasses,
    mock_get_local_transformer,
    mock_image_local_manager,
):
    user_id = 1
    image_path = "/fake/image.jpg"
    transformations = [
        ImageTransformationDefinition(
            identifier="test_thumb",
            transformation=ImageTransformations.THUMBNAIL,
            filters=TransformationFiltersThumbnail(size=(100, 100)),
        )
    ]
    parent_folder = "test_parent"

    expected_save_result = {"transformed_image.png": "/path/to/transformed_image.png"}

    result = image_local_transform(user_id, image_path, transformations, parent_folder)

    mock_get_transformation_dataclasses.assert_called_once_with(transformations)
    mock_get_local_transformer.assert_called_once_with(
        transformations=mock_get_transformation_dataclasses.return_value, is_chain=False
    )

    mock_image_local_manager.assert_called_once_with(
        image_path, transformer=mock_get_local_transformer.return_value
    )

    mock_instance = mock_image_local_manager.return_value
    mock_instance.apply_transformations.assert_called_once()
    mock_instance.save.assert_called_once_with(
        parent_folder=parent_folder,
        transformations=mock_instance.apply_transformations.return_value,
    )

    mock_image_processing_save_procedure.assert_called_once_with(
        user_id=user_id,
        image_file=1,
        image_path=image_path,
        transformer=mock_get_local_transformer().name,
        transformations=transformations,
        transformations_applied=mock_instance.apply_transformations.return_value,
    )
    assert result == expected_save_result


@pytest.mark.django_db
def test_image_processing_save_procedure_integration(user, temp_image_file):
    user_id = user.id

    transformer_name = "chain"
    transformations_defs = [
        ImageTransformationDefinition(
            identifier="thumb_integration",
            transformation=ImageTransformations.THUMBNAIL,
            filters=TransformationFiltersThumbnail(size=(100, 100)),
        ),
        ImageTransformationDefinition(
            identifier="resize_integration",
            transformation=ImageTransformations.BLUR,
        ),
    ]
    mock_applied_image_data = MagicMock()
    mock_applied_image_data.tobytes.return_value = b"transformedimagedata"
    transformations_applied_results = [
        InternalImageTransformationResult(
            identifier="thumb_integration", image=mock_applied_image_data
        ),
        InternalImageTransformationResult(
            identifier="resize_integration", image=mock_applied_image_data
        ),
    ]

    local_manage = ImageLocalManager(image_path=temp_image_file)
    mock_image_file = local_manage.get_file()

    image_processing_save_procedure(
        user_id=user_id,
        image_file=mock_image_file,
        image_path=temp_image_file,
        transformer=transformer_name,
        transformations=transformations_defs,
        transformations_applied=transformations_applied_results,
    )

    assert ProcessingImage.objects.count() == 1
    saved_image = ProcessingImage.objects.first()
    assert saved_image.user_id == user_id
    assert saved_image.file.name == "image_processing/api/test_image.png"

    assert TransformationBatch.objects.count() == 1
    saved_batch = TransformationBatch.objects.first()
    assert saved_batch.input_image == saved_image
    assert saved_batch.transformer == transformer_name

    assert ImageTransformation.objects.count() == 2
    db_transformations = ImageTransformation.objects.order_by("identifier")
    assert db_transformations[0].identifier == "resize_integration"
    assert db_transformations[0].transformation == ImageTransformations.BLUR
    assert db_transformations[0].filters == None
    assert db_transformations[0].batch == saved_batch

    assert db_transformations[1].identifier == "thumb_integration"
    assert db_transformations[1].transformation == ImageTransformations.THUMBNAIL
    assert db_transformations[1].filters == {
        "size": [100, 100],
        "reducing_gap": 2,
        "resample": "bicubic",
    }
    assert db_transformations[1].batch == saved_batch

    assert ProcessedImage.objects.count() == 2
    db_processed_images = ProcessedImage.objects.order_by("identifier")
    assert db_processed_images[0].identifier == "resize_integration"
    assert (
        db_processed_images[0].file.name
        == "image_processing/processed/resize_integration.png"
    )
    assert db_processed_images[0].transformation == db_transformations[0]

    assert db_processed_images[1].identifier == "thumb_integration"
    assert (
        db_processed_images[1].file.name
        == "image_processing/processed/thumb_integration.png"
    )
    assert db_processed_images[1].transformation == db_transformations[1]
