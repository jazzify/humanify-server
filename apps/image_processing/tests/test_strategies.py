import pytest

from apps.image_processing.constants import TRANSFORMATIONS_MULTIPROCESS_TRESHOLD
from apps.image_processing.core.managers.local import ImageLocalManager
from apps.image_processing.core.transformers.chain import ImageChainTransformer
from apps.image_processing.core.transformers.multiprocess import (
    ImageMultiProcessTransformer,
)
from apps.image_processing.core.transformers.sequential import (
    ImageSequentialTransformer,
)
from apps.image_processing.strategies import (
    get_manager_strategy,
    get_transformer_strategy,
)


def test_get_manager_strategy():
    manager = get_manager_strategy()
    assert manager == ImageLocalManager


@pytest.mark.parametrize(
    "transformations, is_chain, expected_transformer",
    (
        ([1, 2], False, ImageSequentialTransformer),
        (
            [x for x in range(TRANSFORMATIONS_MULTIPROCESS_TRESHOLD + 1)],
            False,
            ImageMultiProcessTransformer,
        ),
        (
            [x for x in range(TRANSFORMATIONS_MULTIPROCESS_TRESHOLD + 1)],
            True,
            ImageChainTransformer,
        ),
    ),
)
def test_get_transformer_strategy(
    transformations,
    is_chain,
    expected_transformer,
):
    transformer = get_transformer_strategy(transformations, is_chain)

    assert transformer is not None
    assert transformer == expected_transformer
