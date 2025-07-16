from typing import Generator, Sequence

from ultralytics import YOLO

from apps.image_processing.core.detectors.base import (
    DetectorImage,
    DetectorObjectResult,
    DetectorResult,
)


class CommonObjectDetector:
    def __init__(self, images: Sequence[DetectorImage]) -> None:
        model = YOLO("yolo11l.pt", task="detect")
        self.images = images
        self._results = model([img.image for img in self.images], stream=True)

    @property
    def results(self) -> Generator[DetectorResult]:
        for i, r in enumerate(self._results):
            r_id = self.images[i].identifier
            yield DetectorResult(
                identifier=r_id,
                objects=[
                    DetectorObjectResult(
                        type=box.cls.int(),
                        name=r.names[box.cls.int().item()],
                        box=box.xyxy,
                    )
                    for box in r.boxes
                ],
            )
