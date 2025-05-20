from django.conf import settings
from PIL import Image as PImage

from apps.images.processing.managers import ImageLocalManager


class TestImageLocalManager:
    def test_image_loading(self, temp_image_file):
        manager = ImageLocalManager(image_path=temp_image_file)
        assert isinstance(manager._opened_image, PImage.Image)
        assert manager.get_image() == manager._opened_image

    def test_apply_transformations_with_transformer(
        self, temp_image_file, mock_transformer_with_data, blur_transformation_instance
    ):
        manager = ImageLocalManager(
            image_path=temp_image_file, transformer=mock_transformer_with_data
        )
        manager.apply_transformations()

        mock_transformer_with_data.transform.assert_called_once_with(
            image=manager._opened_image
        )
        assert len(manager._transformations_applied) == 1
        assert (
            manager._transformations_applied[0].identifier
            == blur_transformation_instance.identifier
        )
        assert isinstance(manager._transformations_applied[0].image, PImage.Image)

    def test_apply_transformations_without_transformer(self, temp_image_file):
        manager = ImageLocalManager(image_path=temp_image_file, transformer=None)
        manager.apply_transformations()
        assert len(manager._transformations_applied) == 0

    def test_save_with_transformations(
        self, temp_image_file, mock_transformer_with_data, blur_transformation_instance
    ):
        parent_folder_name = "test_save_parent"
        manager = ImageLocalManager(
            image_path=temp_image_file, transformer=mock_transformer_with_data
        )
        manager.apply_transformations()
        saved_urls = manager.save(parent_folder=parent_folder_name)

        transformation = saved_urls[0]

        expected_save_dir_base = (
            settings.MEDIA_ROOT
            / "processed"
            / parent_folder_name
            / blur_transformation_instance.identifier
        )
        saved_files_in_dir = list(expected_save_dir_base.glob("*.png"))

        assert len(saved_urls) == 1
        assert blur_transformation_instance.identifier == transformation.identifier
        assert expected_save_dir_base.exists()
        assert expected_save_dir_base.is_dir()
        assert len(saved_files_in_dir) == 1
        assert transformation.path == str(saved_files_in_dir[0])

    def test_save_without_applied_transformations(self, temp_image_file, tmp_path):
        manager = ImageLocalManager(image_path=temp_image_file, transformer=None)
        manager.apply_transformations()

        parent_folder_name = "test_save_no_trans"
        saved_urls = manager.save(parent_folder=parent_folder_name)

        assert len(saved_urls) == 0
        assert not (tmp_path / "processed" / parent_folder_name).exists()

    def test_save_with_transformer_but_empty_result(
        self, temp_image_file, mock_transformer_empty_result, tmp_path
    ):
        manager = ImageLocalManager(
            image_path=temp_image_file, transformer=mock_transformer_empty_result
        )
        manager.apply_transformations()

        parent_folder_name = "test_save_empty_trans_result"
        saved_urls = manager.save(parent_folder=parent_folder_name)

        assert len(saved_urls) == 0
        assert not (tmp_path / "processed" / parent_folder_name).exists()
