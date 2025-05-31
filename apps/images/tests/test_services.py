from unittest.mock import MagicMock, patch

import pytest

from apps.image_processing.data_models import InternalImageTransformationDefinition
from apps.image_processing.transformers import (
    ImageMultiProcessTransformer,
    ImageSequentialTransformer,
)
from apps.images.constants import (
    TRANSFORMATIONS_MULTIPROCESS_TRESHOLD,
    ImageTransformations,
)
from apps.images.data_models import ImageTransformationDefinition
from apps.images.services import get_local_transformer, image_local_transform


@pytest.fixture
def mock_get_transformation_dataclasses():
    with patch("apps.images.services.get_transformation_dataclasses") as mock:
        mock.return_value = [MagicMock(), MagicMock()]
        yield mock


@pytest.fixture
def mock_get_local_transformer():
    with patch("apps.images.services.get_local_transformer") as mock:
        mock_transformer_instance = MagicMock()
        mock.return_value = mock_transformer_instance
        yield mock


@pytest.fixture
def mock_image_local_manager():
    with patch("apps.images.services.ImageLocalManager") as mock:
        mock_manager_instance = MagicMock()
        mock_manager_instance.apply_transformations = MagicMock()
        mock_manager_instance.save.return_value = {
            "transformed_image.png": "/path/to/transformed_image.png"
        }
        mock.return_value = mock_manager_instance
        yield mock


def test_image_local_transform(
    mock_get_transformation_dataclasses,
    mock_get_local_transformer,
    mock_image_local_manager,
):
    image_path = "/fake/image.jpg"
    transformations = [
        ImageTransformationDefinition(
            identifier="test_thumb",
            transformation=ImageTransformations.THUMBNAIL,
            filters={"size": (100, 100)},
        )
    ]
    parent_folder = "test_parent"

    expected_save_result = {"transformed_image.png": "/path/to/transformed_image.png"}

    result = image_local_transform(image_path, transformations, parent_folder)

    mock_get_transformation_dataclasses.assert_called_once_with(transformations)
    mock_get_local_transformer.assert_called_once_with(
        transformations=mock_get_transformation_dataclasses.return_value, is_chain=False
    )

    mock_image_local_manager.assert_called_once_with(
        image_path, transformer=mock_get_local_transformer.return_value
    )

    mock_instance = mock_image_local_manager.return_value
    mock_instance.apply_transformations.assert_called_once()
    mock_instance.save.assert_called_once_with(parent_folder=parent_folder)

    assert result == expected_save_result


@pytest.mark.parametrize(
    "num_transformations, expected_transformer_type",
    [
        (TRANSFORMATIONS_MULTIPROCESS_TRESHOLD - 1, ImageSequentialTransformer),
        (TRANSFORMATIONS_MULTIPROCESS_TRESHOLD, ImageMultiProcessTransformer),
        (TRANSFORMATIONS_MULTIPROCESS_TRESHOLD + 1, ImageMultiProcessTransformer),
    ],
)
def test_get_local_transformer(
    num_transformations: int, expected_transformer_type: type
):
    mock_transformations = [
        MagicMock(spec=InternalImageTransformationDefinition)
        for _ in range(num_transformations)
    ]

    transformer = get_local_transformer(transformations=mock_transformations)

    assert isinstance(transformer, expected_transformer_type)
    if num_transformations > 0:
        assert transformer.transformations_data == mock_transformations
    else:
        assert transformer.transformations_data == []
