from unittest.mock import ANY, patch

import pytest

from apps.images.constants import ImageTransformations
from apps.images.data_models import ImageTransformationDataClass
from apps.places.tasks import transform_uploaded_images


@patch("PIL.ImageFilter.BoxBlur")
@patch("PIL.ImageFilter.GaussianBlur")
@patch("apps.images.services.image_local_transform")
@pytest.mark.django_db
def test_transform_uploaded_images(
    mock_image_local_transform, mock_gaussian_blur, mock_box_blur
):
    file_path = "path/to/file.jpg"
    root_folder = "root_folder"
    parent_folder = "parent_folder"

    transform_uploaded_images.enqueue(file_path, root_folder, parent_folder)

    mock_image_local_transform.assert_called_once_with(
        image_path=file_path,
        parent_folder=parent_folder,
        transformations=[
            ImageTransformationDataClass(
                identifier=ANY,
                transformation=ImageTransformations.THUMBNAIL,
                filters={"size": (64, 64)},
            ),
            ImageTransformationDataClass(
                identifier=ANY,
                transformation=ImageTransformations.THUMBNAIL,
            ),
            ImageTransformationDataClass(
                identifier=ANY,
                transformation=ImageTransformations.THUMBNAIL,
                filters={"size": (320, 320)},
            ),
            ImageTransformationDataClass(
                identifier=ANY,
                transformation=ImageTransformations.BLACK_AND_WHITE,
            ),
            ImageTransformationDataClass(
                identifier=ANY,
                transformation=ImageTransformations.BLACK_AND_WHITE,
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
                identifier=ANY,
                transformation=ImageTransformations.BLUR,
                filters={"filter": mock_gaussian_blur(48)},
            ),
            ImageTransformationDataClass(
                identifier=ANY,
                transformation=ImageTransformations.BLUR,
                filters={"filter": mock_box_blur(48)},
            ),
        ],
    )
