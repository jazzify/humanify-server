from unittest.mock import patch

from PIL import ImageFilter

from apps.images import transformations as image_transformations


@patch("PIL.Image.Image")
def test_image_generate_thumbnail(MockImage):
    mock_img_instance = MockImage()
    file_name = "thumbnail.png"

    image_transformations.TransformationThumbnail(mock_img_instance, file_name)

    mock_img_instance.thumbnail.assert_called_once_with((128, 128))


@patch("PIL.Image.Image")
def test_image_generate_blur(MockImage):
    mock_img_instance = MockImage()
    file_name = "blur.png"

    image_transformations.TransformationBlur(mock_img_instance, file_name)

    mock_img_instance.filter.assert_called_once_with(ImageFilter.BLUR)


@patch("PIL.Image.Image")
def test_image_generate_black_and_white(MockImage):
    mock_img_instance = MockImage()
    file_name = "bw.png"

    image_transformations.TransformationBlackAndWhite(mock_img_instance, file_name)

    mock_img_instance.convert.assert_called_once_with("L")
