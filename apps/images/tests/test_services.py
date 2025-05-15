import os
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from django.conf import settings

from apps.images.constants import ImageTransformations
from apps.images.services import ImageTransformationService


@patch("apps.images.services.TransformationBlur")
@patch("apps.images.services.TransformationBlackAndWhite")
@patch("apps.images.services.TransformationThumbnail")
@patch("apps.images.services.cfutures.as_completed")
@patch("apps.images.services.PImage.open")
@patch("apps.images.services.cfutures.ProcessPoolExecutor")
def test_apply_transformations(
    mock_executor,
    mock_pil_open,
    mock_as_completed,
    TransformationThumbnail,
    TransformationBlackAndWhite,
    TransformationBlur,
):
    img_path = Path("path/to/image.jpg")
    transformations = [
        ImageTransformations.THUMBNAIL,
        ImageTransformations.BLACK_AND_WHITE,
        ImageTransformations.BLUR,
    ]
    mock_img_opened = MagicMock()
    mock_img_copy = MagicMock()

    mock_img_opened.copy.return_value = mock_img_copy
    mock_pil_open.return_value.__enter__.return_value = mock_img_opened
    mock_pool_executor_instance = mock_executor.return_value.__enter__.return_value

    image_service = ImageTransformationService(
        img_path, "root", "parent", transformations
    )
    image_service.apply_transformations()

    mock_pool_executor_instance.submit.assert_has_calls(
        [
            call(
                TransformationThumbnail,
                mock_img_copy,
                f"{settings.MEDIA_ROOT}/processed/root/parent/thumbnail",
            ),
            call(
                TransformationBlackAndWhite,
                mock_img_copy,
                f"{settings.MEDIA_ROOT}/processed/root/parent/black_and_white",
            ),
            call(
                TransformationBlur,
                mock_img_copy,
                f"{settings.MEDIA_ROOT}/processed/root/parent/blur",
            ),
        ],
        any_order=True,
    )
    mock_as_completed.assert_called_once()


@patch(
    "apps.images.services.ImageTransformationService._create_transformations_folders"
)
def test_initialize_image_service(mock__create_transformations_folders):
    img_path = "path/to/image.jpg"
    transformations = [
        ImageTransformations.THUMBNAIL,
        ImageTransformations.BLACK_AND_WHITE,
        ImageTransformations.BLUR,
    ]

    image_service = ImageTransformationService(
        img_path, "root", "parent", transformations
    )

    mock__create_transformations_folders.assert_called_once()
    assert image_service.transformations == transformations
    assert image_service.image_path == img_path
    assert image_service.root_folder == "root"
    assert image_service.parent_folder == "parent"


def test_create_transformations_folders():
    root_folder = "root"
    parent_folder = "parent"
    transformations = [
        ImageTransformations.THUMBNAIL,
        ImageTransformations.BLACK_AND_WHITE,
        ImageTransformations.BLUR,
    ]

    image_service = ImageTransformationService(
        "path/to/image.jpg", root_folder, parent_folder, transformations
    )

    for transformation in transformations:
        assert os.path.exists(
            f"{settings.MEDIA_ROOT}/processed/{root_folder}/{parent_folder}/{transformation}"
        )

    assert len(image_service._transformations) == len(transformations)


def test_create_transformations_folder_unsupported_transformation():
    root_folder = "root"
    parent_folder = "parent"
    transformations = ["unsupported_transformation"]

    image_service = ImageTransformationService(
        "path/to/image.jpg", root_folder, parent_folder, transformations
    )

    assert len(image_service._transformations) == 0
