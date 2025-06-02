from enum import StrEnum, auto


# IMPORTANT: Run migrations over image_processing.api models to
# update TransformationBatch support
class InternalTransformerNames(StrEnum):
    MULTIPROCESS = auto()
    SEQUENTIAL = auto()
    CHAIN = auto()
