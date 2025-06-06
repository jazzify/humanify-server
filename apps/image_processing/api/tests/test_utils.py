from unittest.mock import MagicMock

import pytest
from PIL import Image as PImage
from PIL import ImageFilter

from apps.image_processing.api import utils
from apps.image_processing.api.constants import (
    TRANSFORMATIONS_MULTIPROCESS_TRESHOLD,
    ImageTransformations,
)
from apps.image_processing.api.data_models import ImageTransformationDefinition
from apps.image_processing.api.services import (
    get_local_transformer,
)
from apps.image_processing.src.data_models import (
    InternalImageTransformationDefinition,
    InternalTransformationFiltersBlackAndWhite,
    InternalTransformationFiltersBlur,
    InternalTransformationFiltersThumbnail,
    InternalTransformationMapper,
)
from apps.image_processing.src.transformations import (
    TransformationBlackAndWhite,
    TransformationBlur,
    TransformationThumbnail,
)
from apps.image_processing.src.transformers import (
    ImageChainTransformer,
    ImageMultiProcessTransformer,
    ImageSequentialTransformer,
)


@pytest.mark.parametrize(
    "transformation, expected_callable",
    [
        (
            ImageTransformations.THUMBNAIL,
            InternalTransformationMapper(
                transformation=TransformationThumbnail,
                filters=InternalTransformationFiltersThumbnail(
                    size=(128, 128), resample=PImage.Resampling.BICUBIC, reducing_gap=2
                ),
            ),
        ),
        (
            ImageTransformations.BLUR,
            InternalTransformationMapper(
                transformation=TransformationBlur,
                filters=InternalTransformationFiltersBlur(filter=ImageFilter.BLUR()),
            ),
        ),
        (
            ImageTransformations.BLACK_AND_WHITE,
            InternalTransformationMapper(
                transformation=TransformationBlackAndWhite,
                filters=InternalTransformationFiltersBlackAndWhite(
                    dither=PImage.Dither.FLOYDSTEINBERG
                ),
            ),
        ),
    ],
)
def test_transformations_mapper(transformation, expected_callable):
    mapper = utils.transformations_mapper(transformation)

    if transformation == ImageTransformations.BLUR:
        assert mapper.transformation == expected_callable.transformation
        assert isinstance(mapper.filters, expected_callable.filters.__class__)
    else:
        assert mapper == expected_callable


def test_transformations_mapper_invalid():
    with pytest.raises(KeyError):
        utils.transformations_mapper("INVALID_TRANSFORMATION")


def test_get_transformation_dataclasses_empty():
    result_dataclasses = utils.get_transformation_dataclasses([])
    assert result_dataclasses == []


def test_get_transformation_dataclasses_callable_mock():
    mock_transformation_data = [
        ImageTransformationDefinition(
            identifier="test1",
            transformation=ImageTransformations.THUMBNAIL,
            filters=None,
        )
    ]

    result_dataclasses = utils.get_transformation_dataclasses(mock_transformation_data)

    assert len(result_dataclasses) == 1
    assert result_dataclasses[0].filters == InternalTransformationFiltersThumbnail(
        size=(128, 128), resample=PImage.Resampling.BICUBIC, reducing_gap=2
    )
    assert result_dataclasses[0].identifier == "test1"


@pytest.mark.parametrize(
    "num_transformations, expected_transformer_type",
    [
        (TRANSFORMATIONS_MULTIPROCESS_TRESHOLD - 1, ImageSequentialTransformer),
        (TRANSFORMATIONS_MULTIPROCESS_TRESHOLD, ImageMultiProcessTransformer),
        (TRANSFORMATIONS_MULTIPROCESS_TRESHOLD + 1, ImageMultiProcessTransformer),
    ],
)
def test_get_local_transformer_seq_or_multi(
    num_transformations: int, expected_transformer_type: type
):
    mock_transformations = [
        MagicMock(spec=InternalImageTransformationDefinition)
        for _ in range(num_transformations)
    ]

    transformer = get_local_transformer(transformations=mock_transformations)

    assert isinstance(transformer, expected_transformer_type)
    if num_transformations > 0:
        assert transformer.transformations_data == mock_transformations
    else:
        assert transformer.transformations_data == []


def test_get_local_transformer_chain():
    mock_transformations = [
        MagicMock(spec=InternalImageTransformationDefinition) for _ in range(10)
    ]

    transformer = get_local_transformer(
        transformations=mock_transformations, is_chain=True
    )

    assert isinstance(transformer, ImageChainTransformer)
    assert transformer.transformations_data == mock_transformations
