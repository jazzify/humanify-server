import pytest
from PIL import Image as PImage

from apps.image_processing.core.transformations.black_and_white import (
    ExternalTransformationFiltersBlackAndWhite,
    TransformationBlackAndWhite,
)
from apps.image_processing.core.transformations.blur import (
    ExternalTransformationFiltersBlur,
    TransformationBlur,
)
from apps.image_processing.core.transformations.thumbnail import (
    ExternalTransformationFiltersThumbnail,
    TransformationThumbnail,
)
from apps.image_processing.core.transformers.base import (
    ExternalImageTransformationDefinition,
    InternalImageTransformationDefinition,
)
from apps.image_processing.tests.factories import ProcessingImageFactory


@pytest.fixture
def temp_image_file():
    """Creates a temporary image file and returns its path."""
    return PImage.new("RGB", (60, 30), color="red")


@pytest.fixture
def processing_image_base():
    return ProcessingImageFactory()


@pytest.fixture
def image_transformations():
    return [
        InternalImageTransformationDefinition(
            identifier="BLUR/radius_80",
            transformation=TransformationBlur,
            filters=ExternalTransformationFiltersBlur(radius=80),
        ),
        InternalImageTransformationDefinition(
            identifier="THUMBNAIL/size_64",
            transformation=TransformationThumbnail,
            filters=ExternalTransformationFiltersThumbnail(size=(64, 64)),
        ),
        InternalImageTransformationDefinition(
            identifier="BLACK_AND_WHITE/dither_none",
            transformation=TransformationBlackAndWhite,
            filters=ExternalTransformationFiltersBlackAndWhite(dither=None),
        ),
    ]


@pytest.fixture
def external_image_transformations():
    return [
        ExternalImageTransformationDefinition(
            identifier="BLUR/radius_80",
            transformation=TransformationBlur.name,
            filters=ExternalTransformationFiltersBlur(radius=80),
        ),
        ExternalImageTransformationDefinition(
            identifier="BLUR/none",
            transformation=TransformationBlur.name,
        ),
        ExternalImageTransformationDefinition(
            identifier="THUMBNAIL/size_64",
            transformation=TransformationThumbnail.name,
            filters=ExternalTransformationFiltersThumbnail(size=(64, 64)),
        ),
        ExternalImageTransformationDefinition(
            identifier="BLACK_AND_WHITE/dither_none",
            transformation=TransformationBlackAndWhite.name,
            filters=ExternalTransformationFiltersBlackAndWhite(dither=None),
        ),
    ]
