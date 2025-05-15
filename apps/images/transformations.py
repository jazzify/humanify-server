from PIL import ImageFilter

from apps.images.abstract_classes import ImageTransformationCallable


class TransformationThumbnail(ImageTransformationCallable):
    def _apply_transformation(self) -> None:
        self.image.thumbnail((128, 128))
        self.image.save(self.file_name)


class TransformationBlur(ImageTransformationCallable):
    def _apply_transformation(self) -> None:
        new_img = self.image.filter(ImageFilter.BLUR)
        new_img.save(self.file_name)


class TransformationBlackAndWhite(ImageTransformationCallable):
    def _apply_transformation(self) -> None:
        new_img = self.image.convert("L")
        new_img.save(self.file_name)
