from unittest.mock import MagicMock, call, patch

import pytest

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
    InternalImageTransformationDefinition,
)
from apps.image_processing.core.transformers.chain import (
    ImageChainTransformer,
)
from apps.image_processing.core.transformers.multiprocess import (
    ImageMultiProcessTransformer,
)
from apps.image_processing.core.transformers.sequential import (
    ImageSequentialTransformer,
)
from apps.image_processing.tests.factories import TransformationBatchFactory


@patch(
    "apps.image_processing.core.transformers.multiprocess.cfutures.ProcessPoolExecutor"
)
@pytest.mark.django_db
def test_image_multiprocess_transformer(mock_executor):
    # TODO: TEST DB OBJECTS CREATION
    transformation_batch = TransformationBatchFactory()
    mock_image = MagicMock()
    mock_image_copy = MagicMock()
    mock_image.copy.return_value = mock_image_copy
    mock_pool_executor_instance = mock_executor.return_value.__enter__.return_value
    mock_future = mock_pool_executor_instance.submit.return_value

    transformations = [
        InternalImageTransformationDefinition(
            identifier="THUMBNAIL",
            transformation=TransformationThumbnail,
            filters=ExternalTransformationFiltersThumbnail(size=(64, 64)),
        ),
        InternalImageTransformationDefinition(
            identifier="BLACK_AND_WHITE",
            transformation=TransformationBlackAndWhite,
            filters=ExternalTransformationFiltersBlackAndWhite(dither=None),
        ),
    ]
    transformer = ImageMultiProcessTransformer(transformations=transformations)
    with patch.object(transformer, "_callback_process") as mock_callback_process:
        transformer.transform(mock_image, transformation_batch=transformation_batch)
        assert_calls = [
            call(
                TransformationThumbnail,
                mock_image_copy,
                ExternalTransformationFiltersThumbnail(size=(64, 64)),
            ),
            call(
                TransformationBlackAndWhite,
                mock_image_copy,
                ExternalTransformationFiltersBlackAndWhite(dither=None),
            ),
        ]
        mock_pool_executor_instance.submit.assert_has_calls(
            assert_calls,
            any_order=True,
        )
        assert len(assert_calls) == len(transformations)

        for transformation in transformations:
            mock_future.add_done_callback.assert_called_with(
                mock_callback_process(transformation.identifier)
            )
            mock_callback_process.assert_called_with(transformation.identifier)


@pytest.mark.django_db
def test_image_sequential_transformer(temp_image_file):
    # TODO: TEST DB OBJECTS CREATION
    transformation_batch = TransformationBatchFactory()
    transformations = [
        InternalImageTransformationDefinition(
            identifier="THUMBNAIL",
            transformation=TransformationThumbnail,
            filters=ExternalTransformationFiltersThumbnail(size=(64, 64)),
        ),
        InternalImageTransformationDefinition(
            identifier="BLACK_AND_WHITE",
            transformation=TransformationBlackAndWhite,
            filters=ExternalTransformationFiltersBlackAndWhite(dither=None),
        ),
    ]
    transformer = ImageSequentialTransformer(transformations=transformations)
    transformations_applied = transformer.transform(
        temp_image_file, transformation_batch
    )

    assert len(transformations_applied) == len(transformations)
    assert transformations_applied[0].identifier == "THUMBNAIL"
    assert transformations_applied[1].identifier == "BLACK_AND_WHITE"


@pytest.mark.django_db
def test_image_chain_transformer(temp_image_file):
    # TODO: TEST DB OBJECTS CREATION
    transformation_batch = TransformationBatchFactory()
    transformations = [
        InternalImageTransformationDefinition(
            identifier="THUMBNAIL",
            transformation=TransformationThumbnail,
            filters=ExternalTransformationFiltersThumbnail(size=(64, 64)),
        ),
        InternalImageTransformationDefinition(
            identifier="BLACK_AND_WHITE",
            transformation=TransformationBlackAndWhite,
            filters=ExternalTransformationFiltersBlackAndWhite(dither=None),
        ),
        InternalImageTransformationDefinition(
            identifier="BLUR",
            transformation=TransformationBlur,
            filters=ExternalTransformationFiltersBlur(),
        ),
    ]
    transformer = ImageChainTransformer(transformations=transformations)
    transformations_applied = transformer.transform(
        temp_image_file, transformation_batch
    )

    assert len(transformations_applied) == 1
    assert transformations_applied[0].identifier != (
        "THUMBNAIL",
        "BLACK_AND_WHITE",
        "BLUR",
    )
