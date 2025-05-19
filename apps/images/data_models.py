from dataclasses import dataclass, field
from typing import Any

from apps.images.constants import ImageTransformations


@dataclass
class ImageTransformationDataClass:
    identifier: str
    transformation: ImageTransformations
    filters: dict[str, Any] = field(default_factory=lambda: {})
