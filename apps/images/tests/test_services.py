import re
import uuid
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from django.conf import settings
from PIL import Image, ImageFilter

from apps.images import services as images_services
from apps.images.constants import ImageTransformations


def test_image_outfile_name():
    process = ImageTransformations.THUMBNAIL
    root_folder = "test_root"
    parent_folder = "test_parent"
    expected_regex = rf"{settings.MEDIA_ROOT}/processed/{root_folder}/{parent_folder}/{process.value}/[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-5][0-9a-f]{{3}}-[089ab][0-9a-f]{{3}}-[0-9a-f]{{12}}\.png"

    outfile = images_services.image_outfile_name(process, root_folder, parent_folder)

    assert re.match(expected_regex, outfile)


@patch("apps.images.services.settings")
def test_create_processed_media_folder_structure(mock_settings):
    mock_media_root = patch("pathlib.Path").start()
    mock_settings.MEDIA_ROOT = mock_media_root
    root_folder = "test_root"
    parent_folder = "test_parent"

    images_services.create_processed_media_folder_structure(root_folder, parent_folder)

    expected_paths = [
        f"processed/{root_folder}",
        f"processed/{root_folder}/{parent_folder}",
    ]
    for trans in ImageTransformations:
        expected_paths.append(f"processed/{root_folder}/{parent_folder}/{trans.value}")

    assert mock_media_root.joinpath.call_count == len(expected_paths)


@patch("apps.images.services.image_generate_black_and_white")
@patch("apps.images.services.image_generate_blur")
@patch("apps.images.services.image_generate_thumbnail")
@patch("apps.images.services.image_outfile_name")
@patch("apps.images.services.cfutures.wait")
@patch("apps.images.services.cfutures.ProcessPoolExecutor")
@patch("apps.images.services.PImage.open", autospec=True)
@patch("apps.images.services.create_processed_media_folder_structure")
def test_image_apply_generators(
    mock_create_structure,
    mock_pil_open,
    mock_executor,
    mock_process_wait,
    mock_image_outfile_name,
    mock_image_generate_thumbnail,
    mock_image_generate_blur,
    mock_image_generate_black_and_white,
):
    image_path = "dummy/path/to/image.png"
    root_folder = "root"
    parent_folder = "parent"

    mock_img_opened = MagicMock()
    mock_img_copy = MagicMock()
    mock_img_opened.copy.return_value = mock_img_copy
    mock_pil_open.return_value.__enter__.return_value = mock_img_opened

    mock_pool_executor_instance = mock_executor.return_value.__enter__.return_value

    images_services.image_apply_generators(image_path, root_folder, parent_folder)

    mock_create_structure.assert_called_once_with(root_folder, parent_folder)
    mock_pil_open.assert_called_once_with(image_path)
    mock_process_wait.assert_called_once()
    mock_image_outfile_name.assert_has_calls(
        [
            call(ImageTransformations.THUMBNAIL, root_folder, parent_folder),
            call(ImageTransformations.BLUR, root_folder, parent_folder),
            call(ImageTransformations.BLACK_AND_WHITE, root_folder, parent_folder),
        ]
    )
    mock_pool_executor_instance.submit.assert_has_calls(
        [
            call(
                images_services.image_generate_thumbnail,
                mock_img_copy,
                mock_image_outfile_name.return_value,
            ),
            call(
                images_services.image_generate_blur,
                mock_img_copy,
                mock_image_outfile_name.return_value,
            ),
            call(
                images_services.image_generate_black_and_white,
                mock_img_copy,
                mock_image_outfile_name.return_value,
            ),
        ]
    )


@patch("apps.images.services.PImage.open")
def test_image_apply_generators_exception(mock_pil_open):
    image_path = "dummy/path/to/image.png"
    root_folder = "root"
    parent_folder = "parent"
    mock_pil_open.side_effect = Exception("Test Error")

    with pytest.raises(Exception) as excinfo:
        images_services.image_apply_generators(image_path, root_folder, parent_folder)


@patch("PIL.Image.Image")
def test_image_generate_thumbnail(MockImage):
    mock_img_instance = MockImage()
    file_name = "thumbnail.png"

    result = images_services.image_generate_thumbnail(mock_img_instance, file_name)

    mock_img_instance.thumbnail.assert_called_once_with((128, 128))
    mock_img_instance.save.assert_called_once_with(file_name)
    assert result == file_name


@patch("PIL.Image.Image")
def test_image_generate_blur(MockImage):
    mock_img_instance = MockImage()
    mock_filtered_img = MockImage()
    mock_img_instance.filter.return_value = mock_filtered_img
    file_name = "blur.png"

    result = images_services.image_generate_blur(mock_img_instance, file_name)

    mock_img_instance.filter.assert_called_once_with(ImageFilter.BLUR)
    mock_filtered_img.save.assert_called_once_with(file_name)
    assert result == file_name


@patch("PIL.Image.Image")
def test_image_generate_black_and_white(MockImage):
    mock_img_instance = MockImage()
    mock_converted_img = MockImage()
    mock_img_instance.convert.return_value = mock_converted_img
    file_name = "bw.png"

    result = images_services.image_generate_black_and_white(
        mock_img_instance, file_name
    )

    mock_img_instance.convert.assert_called_once_with("L")
    mock_converted_img.save.assert_called_once_with(file_name)
    assert result == file_name
