from enum import StrEnum, auto

TRANSFORMATIONS_MULTIPROCESS_TRESHOLD = 5


class TRANSFORMATION_FILTER_THUMBNAIL_RESAMPLING(StrEnum):
    NEAREST = auto()
    BOX = auto()
    BILINEAR = auto()
    HAMMING = auto()
    BICUBIC = auto()
    LANCZOS = auto()


class TRANSFORMATION_FILTER_BLUR_FILTER(StrEnum):
    BLUR = auto()
    BOX_BLUR = auto()
    GAUSSIAN_BLUR = auto()


class TRANSFORMATION_FILTER_DITHER(StrEnum):
    FLOYDSTEINBERG = auto()
    NONE = auto()
    # ORDERED = auto()  # Not yet implemented (by PIL team)
    # RASTERIZE = auto()  # Not yet implemented (by PIL team)
