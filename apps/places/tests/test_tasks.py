from unittest.mock import patch

import pytest

from apps.places.tasks import transform_uploaded_images


@patch("apps.image_processing.api.services.processing.image_local_transform")
@pytest.mark.django_db
def test_transform_uploaded_images(mock_image_local_transform):
    file_path = "path/to/file.jpg"
    root_folder = "root_folder"
    parent_folder = "parent_folder"

    transform_uploaded_images.enqueue(file_path, root_folder, parent_folder)

    mock_image_local_transform.assert_called_once()
