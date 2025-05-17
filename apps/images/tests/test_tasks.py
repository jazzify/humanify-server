from unittest.mock import patch

import pytest
from PIL import ImageFilter

from apps.images.constants import ImageTransformations
from apps.images.data_models import ImageTransformationDataClass
from apps.images.tasks import transform_uploaded_images


@patch("PIL.ImageFilter.BoxBlur")
@patch("PIL.ImageFilter.GaussianBlur")
@patch("apps.images.services.ImageTransformationService")
@pytest.mark.django_db
def test_transform_uploaded_images(
    mock_image_service, mock_gaussian_blur, mock_box_blur
):
    file_path = "path/to/file.jpg"
    root_folder = "root_folder"
    parent_folder = "parent_folder"

    transform_uploaded_images.enqueue(file_path, root_folder, parent_folder)

    mock_image_service.assert_called_once_with(
        image_path=file_path,
        root_folder=root_folder,
        parent_folder=parent_folder,
        transformations=[
            ImageTransformationDataClass(
                name=ImageTransformations.THUMBNAIL,
                filters={"size": (64, 64)},
            ),
            ImageTransformationDataClass(name=ImageTransformations.THUMBNAIL),
            ImageTransformationDataClass(
                name=ImageTransformations.THUMBNAIL,
                filters={"size": (320, 320)},
            ),
            ImageTransformationDataClass(name=ImageTransformations.BLACK_AND_WHITE),
            ImageTransformationDataClass(
                name=ImageTransformations.BLACK_AND_WHITE,
                filters={
                    "matrix": (
                        0.312453,
                        0.957580,
                        0.980423,
                        0,
                        0.112671,
                        0.915160,
                        0.972169,
                        0,
                        0.319334,
                        0.919193,
                        0.950227,
                        0,
                    )
                },
            ),
            ImageTransformationDataClass(
                name=ImageTransformations.BLUR,
                filters={"filter": mock_gaussian_blur(48)},
            ),
            ImageTransformationDataClass(
                name=ImageTransformations.BLUR, filters={"filter": mock_box_blur(48)}
            ),
        ],
    )
    mock_image_service.return_value.apply_transformations.assert_called_once()
