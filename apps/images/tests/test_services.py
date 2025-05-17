import os
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from django.conf import settings

from apps.images.constants import ImageTransformations
from apps.images.data_models import ImageTransformationDataClass
from apps.images.services import ImageTransformationService


@patch("apps.images.services.TransformationBlur")
@patch("apps.images.services.TransformationBlackAndWhite")
@patch("apps.images.services.TransformationThumbnail")
@patch("apps.images.services.PImage.open")
@patch("apps.images.services.cfutures.ProcessPoolExecutor")
@patch("apps.images.services.TRANSFORMATIONS_MULTIPROCESS_TRESHOLD")
def test_apply_transformations_multiprocess(
    mock_transformations_treshold,
    mock_executor,
    mock_pil_open,
    TransformationThumbnail,
    TransformationBlackAndWhite,
    TransformationBlur,
):
    img_path = Path("path/to/image.jpg")
    transformations = [
        ImageTransformationDataClass(name=ImageTransformations.THUMBNAIL),
        ImageTransformationDataClass(name=ImageTransformations.BLUR),
        ImageTransformationDataClass(name=ImageTransformations.BLACK_AND_WHITE),
    ]
    mock_transformations_treshold.return_value = len(transformations) - 1
    mock_img_opened = MagicMock()

    mock_pil_open.return_value.__enter__.return_value = mock_img_opened
    mock_pool_executor_instance = mock_executor.return_value.__enter__.return_value

    with patch(
        "apps.images.services.TRANSFORMATIONS_MULTIPROCESS_TRESHOLD",
        len(transformations) - 1,
    ):
        image_service = ImageTransformationService(
            img_path, "root", "parent", transformations
        )
        image_service.apply_transformations()
        mock_pool_executor_instance.submit.assert_has_calls(
            [
                call(
                    TransformationThumbnail,
                    mock_img_opened,
                    {},
                ),
                call(
                    TransformationBlackAndWhite,
                    mock_img_opened,
                    {},
                ),
                call(
                    TransformationBlur,
                    mock_img_opened,
                    {},
                ),
            ],
            any_order=True,
        )


@patch("apps.images.services.TransformationBlur")
@patch("apps.images.services.TransformationBlackAndWhite")
@patch("apps.images.services.TransformationThumbnail")
@patch("apps.images.services.PImage.open")
def test_apply_transformations_singleprocess(
    mock_pil_open,
    TransformationThumbnail,
    TransformationBlackAndWhite,
    TransformationBlur,
):
    img_path = Path("path/to/image.jpg")
    transformations = [
        ImageTransformationDataClass(name=ImageTransformations.THUMBNAIL),
        ImageTransformationDataClass(name=ImageTransformations.BLUR),
        ImageTransformationDataClass(name=ImageTransformations.BLACK_AND_WHITE),
    ]
    mock_img_opened = MagicMock()
    mock_pil_open.return_value.__enter__.return_value = mock_img_opened

    with patch(
        "apps.images.services.TRANSFORMATIONS_MULTIPROCESS_TRESHOLD",
        len(transformations) + 1,
    ):
        image_service = ImageTransformationService(
            img_path, "root", "parent", transformations
        )
        image_service.apply_transformations()

        TransformationThumbnail.assert_called_once_with(
            image=mock_img_opened,
            filters={},
        )
        TransformationBlackAndWhite.assert_called_once_with(
            image=mock_img_opened,
            filters={},
        )
        TransformationBlur.assert_called_once_with(
            image=mock_img_opened,
            filters={},
        )


def test_initialize_image_service():
    img_path = "path/to/image.jpg"
    transformations = [
        ImageTransformationDataClass(name=ImageTransformations.THUMBNAIL),
        ImageTransformationDataClass(name=ImageTransformations.BLUR),
        ImageTransformationDataClass(name=ImageTransformations.BLACK_AND_WHITE),
    ]

    image_service = ImageTransformationService(
        img_path, "root", "parent", transformations
    )

    assert image_service.transformations == transformations
    assert image_service.image_path == img_path
    assert image_service.root_folder == "root"
    assert image_service.parent_folder == "parent"
    assert len(image_service._transformation_callables) == len(transformations)


def test_create_transformations_folders():
    root_folder = "root"
    parent_folder = "parent"
    transformations = [
        ImageTransformationDataClass(name=ImageTransformations.THUMBNAIL),
        ImageTransformationDataClass(name=ImageTransformations.BLUR),
        ImageTransformationDataClass(name=ImageTransformations.BLACK_AND_WHITE),
    ]

    ImageTransformationService(
        "path/to/image.jpg", root_folder, parent_folder, transformations
    )

    for transformation in transformations:
        assert os.path.exists(
            f"{settings.MEDIA_ROOT}/processed/{root_folder}/{parent_folder}/{transformation.name}"
        )


def test_create_transformations_folder_unsupported_transformation():
    root_folder = "root"
    parent_folder = "parent"
    transformations = [
        ImageTransformationDataClass(name="testing"),
        ImageTransformationDataClass(name=ImageTransformations.BLUR),
        ImageTransformationDataClass(name=ImageTransformations.BLACK_AND_WHITE),
    ]

    image_service = ImageTransformationService(
        "path/to/image.jpg", root_folder, parent_folder, transformations
    )

    assert len(image_service._transformation_callables) == 2
