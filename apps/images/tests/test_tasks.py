from unittest.mock import patch

import pytest

from apps.images.constants import ImageTransformations
from apps.images.tasks import transform_uploaded_images


@patch("apps.images.services.ImageTransformationService")
@pytest.mark.django_db
def test_transform_uploaded_images(mock_image_service):
    file_path = "path/to/file.jpg"
    root_folder = "root_folder"
    parent_folder = "parent_folder"

    transform_uploaded_images.enqueue(file_path, root_folder, parent_folder)

    mock_image_service.assert_called_once_with(
        image_path=file_path,
        root_folder=root_folder,
        parent_folder=parent_folder,
        transformations=[transformation for transformation in ImageTransformations],
    )
    mock_image_service.return_value.apply_transformations.assert_called_once()
