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
from apps.image_processing.core.transformers.chain import (
    ImageChainTransformer,
)
from apps.image_processing.core.transformers.multiprocess import (
    ImageMultiProcessTransformer,
)
from apps.image_processing.core.transformers.sequential import (
    ImageSequentialTransformer,
)
from apps.image_processing.models import ImageTransformation, ProcessedImage
from apps.image_processing.tests.factories import TransformationBatchFactory


@patch(
    "apps.image_processing.core.transformers.multiprocess.cfutures.ProcessPoolExecutor"
)
@pytest.mark.django_db
def test_image_multiprocess_transformer(mock_executor, image_transformations):
    transformation_batch = TransformationBatchFactory()
    mock_image = MagicMock()
    mock_image_copy = MagicMock()
    mock_image.copy.return_value = mock_image_copy
    mock_pool_executor_instance = mock_executor.return_value.__enter__.return_value
    mock_future = mock_pool_executor_instance.submit.return_value

    transformer = ImageMultiProcessTransformer(transformations=image_transformations)
    with patch.object(transformer, "_callback_process") as mock_callback_process:
        transformer.transform(mock_image, transformation_batch=transformation_batch)
        assert_calls = [
            call(
                TransformationBlur,
                mock_image_copy,
                ExternalTransformationFiltersBlur(radius=80),
            ),
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
        assert len(assert_calls) == len(image_transformations)

        for transformation in image_transformations:
            mock_future.add_done_callback.assert_called_with(
                mock_callback_process(transformation.identifier)
            )
            mock_callback_process.assert_called_with(transformation.identifier)


@pytest.mark.django_db
def test_image_sequential_transformer(temp_image_file, image_transformations):
    transformation_batch = TransformationBatchFactory()
    transformer = ImageSequentialTransformer(transformations=image_transformations)
    transformations_applied = transformer.transform(
        temp_image_file, transformation_batch
    )

    assert len(transformations_applied) == len(image_transformations)
    assert transformations_applied[0].identifier == image_transformations[0].identifier
    assert transformations_applied[1].identifier == image_transformations[1].identifier
    assert ImageTransformation.objects.count() == len(image_transformations)
    assert ProcessedImage.objects.count() == len(image_transformations)


@pytest.mark.django_db
def test_image_chain_transformer(temp_image_file, image_transformations):
    transformation_batch = TransformationBatchFactory()
    transformer = ImageChainTransformer(transformations=image_transformations)
    transformations_applied = transformer.transform(
        temp_image_file, transformation_batch
    )
    identifiers = transformations_applied[0].identifier.split("-")
    local_identifiers = [transform.identifier for transform in image_transformations]

    assert identifiers == local_identifiers
    assert len(transformations_applied) == 1
    assert ImageTransformation.objects.count() == 1
    assert ProcessedImage.objects.count() == 1
