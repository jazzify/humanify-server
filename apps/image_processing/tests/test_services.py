from unittest.mock import patch

import pytest

from apps.image_processing.services import image_local_transform


@pytest.mark.django_db
@patch("apps.image_processing.services.get_manager_strategy")
@patch("apps.image_processing.services.get_transformer_strategy")
@patch("apps.image_processing.services.get_internal_transformations")
@patch("apps.image_processing.services.ProcessingImage.objects.get")
def test_image_local_transform(
    mock_processing_image_model,
    mock_get_internal_transformations,
    mock_get_transformer_strategy,
    mock_manager_strategy,
    processing_image_base,
    external_image_transformations,
):
    user_id = 1
    image_id = processing_image_base.id
    transformations = external_image_transformations
    is_chain = False

    mock_processing_image_model.return_value = processing_image_base

    image_local_transform(
        user_id=user_id,
        image_id=image_id,
        transformations=transformations,
        is_chain=is_chain,
    )

    mock_processing_image_model.assert_called_once_with(id=image_id, user_id=user_id)
    mock_get_internal_transformations.assert_called_once_with(
        external_transformations=external_image_transformations
    )
    mock_get_transformer_strategy.assert_called_once_with(
        transformations=mock_get_internal_transformations.return_value,
        is_chain=is_chain,
    )
    mock_manager_strategy.assert_called_once()
    mock_manager_strategy.return_value.return_value.apply_transformations.assert_called_once()
