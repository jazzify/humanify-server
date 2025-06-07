from typing import Generator, Sequence

from ultralytics import YOLO

from apps.image_processing.data_models import (
    DetectorImage,
    DetectorObjectResult,
    DetectorResult,
)


class CommonObjectDetector:
    _MODEL = YOLO("yolo11l.pt", task="detect")

    def __init__(self, images: Sequence[DetectorImage]) -> None:
        self.images = images
        _images = [image.image for image in images]
        self._results = self._MODEL(_images, stream=True)
        self.results = self._process_results()

    def _process_results(self) -> Generator[DetectorResult]:
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
