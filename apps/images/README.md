# Images App

This app is responsible for handling image processing and transformations.

## Core Functionalities

- **Image Transformations**: Provides capabilities to transform images in various ways and provide different processing strategies.
- **Transformation Management**: Provides a high-level interface for general image operations.
- **Extensible Design**: Built with a clear separation of concerns, allowing for easy extension with new transformations or processing strategies.

## Key Components

- **`constants.py`**: Defines public constants and enums related to image transformations.
- **`data_models.py`**: Expose public data structures for image transformations and their configuration.
- **`services.py`**: Provides high-level functions to interact with the image processing capabilities.
- **`processing/` directory**: Contains the core logic for image manipulation.
    - **`transformations.py`**: Implements the actual image transformation logic using the Pillow (PIL) library.
    - **`transformers.py`**: Defines different strategies for applying transformations.
        - `ImageMultiProcessTransformer`: Applies transformations in parallel using a process pool, suitable for a large number of independent transformations.
        - `ImageSequentialTransformer`: Applies transformations one by one in sequence.
        - `ImageChainTransformer`: Applies transformations sequentially, where the output of one transformation becomes the input for the next.
    - **`managers.py`**: Manages the overall image processing workflow.
        - `ImageLocalManager`: Manages transformations for images stored locally on the filesystem. It opens the image, applies transformations using a specified transformer, and saves the resulting images to a structured directory.
    - **`data_models.py` (within `processing/`)**: Defines internal data structures used during the transformation process, such as `InternalImageTransformationFilters` which are direct mappings to PIL's internal representations.
    - **`utils.py`**: Provides utility functions for converting between user-facing data models and internal representations.

## How it Works (Example Flow from `apps.places.tasks.py`)

The `transform_uploaded_images` task in `apps.places.tasks.py` demonstrates how this `images` app is used:

1. A list of `ImageTransformationDefinition` objects is defined, each specifying an `identifier`, a `transformation` type (e.g., `ImageTransformations.THUMBNAIL`), and optional `filters`.
``` python
from apps.images.constants import (
        ImageTransformations,
        TransformationFilterBlurFilter,
        TransformationFilterDither,
        TransformationFilterThumbnailResampling,
    )
from apps.images.data_models import (
    ImageTransformationDefinition,
    TransformationFiltersBlackAndWhite,
    TransformationFiltersBlur,
    TransformationFiltersThumbnail,
)


transformations = [
    # Thumbnail
    ImageTransformationDefinition(
        identifier="THUMBNAIL/s_320_gap_8_lanczos",
        transformation=ImageTransformations.THUMBNAIL,
        filters=TransformationFiltersThumbnail(
            size=(320, 320),
            reducing_gap=8,
            resample=TransformationFilterThumbnailResampling.LANCZOS,
        ),
    ),
    # Black and White
    ImageTransformationDefinition(
        identifier="BNW/none",
        transformation=ImageTransformations.BLACK_AND_WHITE,
        filters=TransformationFiltersBlackAndWhite(
            dither=TransformationFilterDither.NONE
        ),
    ),
    # Blur
    ImageTransformationDefinition(
        identifier="BLUR/gaussian_86",
        transformation=ImageTransformations.BLUR,
        filters=TransformationFiltersBlur(
            filter=TransformationFilterBlurFilter.GAUSSIAN_BLUR,
            radius=86,
        ),
    )
]
```

2. Use the `image_local_transform` service with the `image_path`, the list of `transformations`, and a `parent_folder` name.
``` python
from images.services import image_local_transform

applied_transformations = image_local_transform(
    image_path="path/to/local/image.png",
    transformations=transformations,
    parent_folder="parent_folder",
)

for transformation in applied_transformations:
    logger.info(f"{transformation.identifier}: {transformation.path}")

```

## How It Works Inside:

### Transformations (`images.processing.transformations`):

The core logic for applying custom image transformations. This includes the actual transformation logic using the Pillow (PIL) library. They take an image, apply a transformation based on the provided filters, and return a transformed PIL image copy.

Make your own transformation like this:
```python
from apps.images.data_models import InternalImageTransformation
from PIL import Image as PImage


class TransformationCrop(InternalImageTransformation): # Inherit from InternalImageTransformation
    def _image_transform(
        self,
        image: PImage.Image,
        filters: InternalTransformationFiltersCrop # Each subclass must have its own filters
    ) -> PImage.Image:
        # Since PIL.Image.Image.crop returns another PIL.Image.Image instance
        # we can apply the transformation "in-place"
        new_img = image.crop(
            x_left=filters.x_left,
            y_top=filters.y_top,
            x_right=filters.x_right,
            y_bottom=filters.y_bottom,
        )
        return new_img  # Must return PIL.Image.Image instance

...

```

## Filters (`images.processing.data_models`):

Defines the internal representations of image transformations. Each subclass corresponds to a specific transformation type and its associated filters.

Make your own filters like this:
```python
from apps.images.processing.data_models import InternalImageTransformationFilters

@dataclass
class InternalTransformationFiltersCrop(InternalImageTransformationFilters): # Inherit from InternalImageTransformationFilters
    x_left: float
    y_top: float
    x_right: float
    y_bottom: float
```

### Transformers (`images.processing.transformers`):

Defines different strategies for applying transformations, they take a list of
`InternalImageTransformation` wich contains the `transformation` to apply with the corresponding `filters` and the provided `identifier`.

Make your own transformers like this:
```python
from apps.images.processing.data_models import InternalImageTransformationResult
from apps.images.processing.transformers import BaseImageTransformer

from PIL import Image as PImage


# Apply transformations one by one and returna list of
# the transformed images with their corresponding identifiers
class ImageSequentialTransformer(BaseImageTransformer):  # Inherit from BaseImageTransformer
    # Must implement the `transform` method
    def transform(self, image: PImage.Image) -> list[InternalImageTransformationResult]:
        transformations = []
        for transform_data in self.transformations_data:
            transformation = transform_data.transformation( # InternalImageTransformation instance
                image, # All transformations should return a new PIL.Image.Image instance
                transform_data.filters, # Matching `transformation` filter
            )
            transformations.append(
                InternalImageTransformationResult(
                    identifier=transform_data.identifier, # Return the same identifier
                    image=transformation.image_transformed, # Return the transformed image
                )
            )
        return transformations # Must return list[InternalImageTransformationResult]
```

### Managers (`images.processing.managers`):

Manages the overall image processing workflow. It takes an image path, a list of
transformations, and a parent folder name, and applies the transformations using
the selected transformer.

Make your own manager like this:
```python
import io

import boto3
from PIL import Image as PImage

from apps.images.processing.managers import BaseImageManager
from apps.images.processing.data_models import InternalTransformationManagerSaveResult


class ImageS3Manager(BaseImageManager): # Inherit from BaseImageManager
    @property
    def _s3_bucket(self):
        resource_s3 = boto3.resource('s3', region_name='us-outwest-1')
        the_bucket = resource_s3.Bucket("the_bucket")
        return the_bucket

    def _load_and_save(self, image: PImage.Image, identifier: str):
        image_buffer = BytesIO()
        image.save(image_buffer, format='png')
        image_buffer.seek(0)
        image_uploaded = self._s3_bucket.Object.put(
            body=image_buffer, Key=identifier
        )
        return image_uploaded.url

    # Must implement the `_get_image` method
    def _get_image(self) -> PImage.Image:
        # Handle your custom manager image loading logic
        # and convert to PIL.Image.Image
        image = self._s3_bucket().Object(key)
        response = image.get()
        file_stream = response['Body']
        return PImage.open(file_stream)

    # Must implement the `save` method to save the transformed images
    # returned by the self.transformer
    def save(self, parent_folder: str) -> list[InternalTransformationManagerSaveResult]:
        # Handle your custom manager image transformations saving logic
        # and return list[InternalTransformationManagerSaveResult]
        # with the identifier and path
        saved_images = []
        for transformation in self._transformations_applied:
            saved_images.append(
                InternalTransformationManagerSaveResult(
                    identifier=transformation.identifier,
                    path=self._load_and_save(transformation.image, transformation.identifier),
                )
            )
        return saved_images
```

### Mix all together:

```python
...
transformations= [
    InternalImageTransformationDefinition(
        identifier="CROP/default",
        transformation=TransformationCrop,
        filters=InternalTransformationFiltersCrop(
            x_left=80.4,
            y_top=20,
            x_right=2,
            y_bottom=0
        )
    ),
    ...
]
image_transformer = ImageSequentialTransformer(transformations)
image_manager = ImageS3Manager(
    image_path="s3/image/key",
    transformer=image_transformer,
)
image_manager.apply_transformations()
image_manager.save(parent_folder="output")
...

```
