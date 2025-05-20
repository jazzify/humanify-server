from enum import StrEnum, auto


class ImageTransformations(StrEnum):
    THUMBNAIL = auto()
    BLUR = auto()
    BLACK_AND_WHITE = auto()


class TransformationFilterThumbnailResampling(StrEnum):
    NEAREST = auto()
    BOX = auto()
    BILINEAR = auto()
    HAMMING = auto()
    BICUBIC = auto()
    LANCZOS = auto()


class TransformationFilterBlurFilter(StrEnum):
    BLUR = auto()
    BOX_BLUR = auto()
    GAUSSIAN_BLUR = auto()


class TransformationFilterDither(StrEnum):
    FLOYDSTEINBERG = auto()
    NONE = auto()
    # ORDERED = auto()  # Not yet implemented (by PIL team)
    # RASTERIZE = auto()  # Not yet implemented (by PIL team)


TRANSFORMATIONS_MULTIPROCESS_TRESHOLD = 5
