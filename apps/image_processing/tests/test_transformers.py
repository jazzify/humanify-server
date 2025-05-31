from unittest.mock import MagicMock, call, patch

from apps.image_processing.data_models import InternalImageTransformationDefinition
from apps.image_processing.transformations import (
    TransformationBlackAndWhite,
    TransformationBlur,
    TransformationThumbnail,
)
from apps.image_processing.transformers import (
    ImageChainTransformer,
    ImageMultiProcessTransformer,
    ImageSequentialTransformer,
)


@patch("apps.image_processing.transformers.cfutures.ProcessPoolExecutor")
def test_image_multiprocess_transformer(mock_executor):
    mock_image = MagicMock()
    mock_image_copy = MagicMock()
    mock_image.copy.return_value = mock_image_copy

    transformations = [
        InternalImageTransformationDefinition(
            identifier="THUMBNAIL",
            transformation=TransformationThumbnail,
            filters={"size": (64, 64)},
        ),
        InternalImageTransformationDefinition(
            identifier="BLUR",
            transformation=TransformationBlur,
            filters={"size": (64, 64)},
        ),
        InternalImageTransformationDefinition(
            identifier="BLACK_AND_WHITE",
            transformation=TransformationBlackAndWhite,
            filters={"size": (64, 64)},
        ),
    ]
    transformer = ImageMultiProcessTransformer(transformations=transformations)

    mock_pool_executor_instance = mock_executor.return_value.__enter__.return_value
    mock_future = mock_pool_executor_instance.submit.return_value
    with patch.object(transformer, "_callback_process") as mock_callback_process:
        transformer.transform(mock_image)
        assert_calls = [
            call(
                TransformationThumbnail,
                mock_image_copy,
                {"size": (64, 64)},
            ),
            call(
                TransformationBlackAndWhite,
                mock_image_copy,
                {"size": (64, 64)},
            ),
            call(
                TransformationBlur,
                mock_image_copy,
                {"size": (64, 64)},
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


def test_image_sequential_transformer():
    image = MagicMock()
    mock_thumbnail_t = MagicMock()
    mock_blur_t = MagicMock()
    mock_bnw_t = MagicMock()
    thumbnail_size = {"size": (64, 64)}

    transformations = [
        InternalImageTransformationDefinition(
            identifier="THUMBNAIL",
            transformation=mock_thumbnail_t,
            filters=thumbnail_size,
        ),
        InternalImageTransformationDefinition(
            identifier="BLUR", transformation=mock_blur_t, filters={}
        ),
        InternalImageTransformationDefinition(
            identifier="BLACK_AND_WHITE", transformation=mock_bnw_t, filters={}
        ),
    ]
    transformer = ImageSequentialTransformer(transformations=transformations)
    transformations_applied = transformer.transform(image)

    assert len(transformations_applied) == len(transformations)
    assert transformations_applied[0].identifier == "THUMBNAIL"
    assert transformations_applied[1].identifier == "BLUR"
    assert transformations_applied[2].identifier == "BLACK_AND_WHITE"
    mock_thumbnail_t.assert_called_with(image, {"size": (64, 64)})
    mock_blur_t.assert_called_with(image, {})
    mock_bnw_t.assert_called_with(image, {})


def test_image_chain_transformer():
    image = MagicMock()
    mock_thumbnail_t = MagicMock()
    mock_blur_t = MagicMock()
    mock_bnw_t = MagicMock()
    thumbnail_size = {"size": (64, 64)}

    transformations = [
        InternalImageTransformationDefinition(
            identifier="THUMBNAIL",
            transformation=mock_thumbnail_t,
            filters=thumbnail_size,
        ),
        InternalImageTransformationDefinition(
            identifier="BLACK_AND_WHITE", transformation=mock_bnw_t, filters={}
        ),
        InternalImageTransformationDefinition(
            identifier="BLUR", transformation=mock_blur_t, filters={}
        ),
    ]
    transformer = ImageChainTransformer(transformations=transformations)
    transformations_applied = transformer.transform(image)

    assert len(transformations_applied) == 1
    assert transformations_applied[0].identifier != (
        "THUMBNAIL",
        "BLACK_AND_WHITE",
        "BLUR",
    )
