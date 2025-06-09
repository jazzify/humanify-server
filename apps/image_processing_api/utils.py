from typing import Type

from apps.image_processing.core.transformations.base import (
    ExternalTransformationFilters,
)
from apps.image_processing.core.transformations.black_and_white import (
    ExternalTransformationFiltersBlackAndWhite,
)
from apps.image_processing.core.transformations.blur import (
    ExternalTransformationFiltersBlur,
)
from apps.image_processing.core.transformations.thumbnail import (
    ExternalTransformationFiltersThumbnail,
)
from apps.image_processing.models import ImageTransformation


def get_filters_dataclasses_by_transformation(
    transformation: str,
) -> Type[ExternalTransformationFilters]:
    filters = {
        ImageTransformation.THUMBNAIL: ExternalTransformationFiltersThumbnail,
        ImageTransformation.BLUR: ExternalTransformationFiltersBlur,
        ImageTransformation.BLACK_AND_WHITE: ExternalTransformationFiltersBlackAndWhite,
    }
    return filters[transformation]  # type: ignore[return-value]
