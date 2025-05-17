from enum import StrEnum, auto


# Using auto() with StrEnum results in the lower-cased member name as the value.
class ImageTransformations(StrEnum):
    THUMBNAIL = auto()
    BLUR = auto()
    BLACK_AND_WHITE = auto()


TRANSFORMATIONS_MULTIPROCESS_TRESHOLD = 3
