from dataclasses import dataclass, field

from PIL import Image as PImage


@dataclass
class DetectorObjectResult:
    type: int
    name: str
    box: list[float]


@dataclass
class DetectorResult:
    identifier: str | int
    objects: list[DetectorObjectResult] = field(default_factory=list)


@dataclass
class DetectorImage:
    identifier: str | int
    image: PImage.Image | str
