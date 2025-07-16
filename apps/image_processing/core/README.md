# Images App

This app is responsible for handling image processing and transformations.

## Core concepts

- **Image Transformations**: Provides capabilities to transform images in various ways and provide different processing strategies.
- **Transformation Management**: Provides a high-level interface for general image operations.
- **Transformers**: Define different strategies for applying transformations, such as in parallel or one by one.
- **Detectors**: Detect objects in images using computer vision models.

## Key components

- **`transformations.py`**: Applies a transformation to an image using the Pillow (PIL) library and returns a transformed PIL image copy.
- **`transformers.py`**: Defines different strategies for applying transformations.
    - `ImageMultiProcessTransformer`: Applies transformations in parallel using a process pool, suitable for a large number of independent transformations.
    - `ImageSequentialTransformer`: Applies transformations one by one in sequence of independent transformations.
    - `ImageChainTransformer`: Applies transformations sequentially, where the output of one transformation becomes the input for the next.
- **`managers.py`**: Manages the overall image processing workflow.
    - `ImageLocalManager`: Manages transformations for images stored locally on the filesystem. It opens the image, applies transformations using a specified transformer, and saves the resulting images to a structured directory.

## How is expected to be used:

1. Define a list of transformation objects is defined, each specifying an `identifier`, a `transformation` name type (e.g., `thumbnail`), and optional `filters`.
``` python
    transformations = [
        {
            "identifier": "00",
            "transformation": "black_and_white"
        },
        {
            "identifier": "22",
            "transformation": "blur",
            "filters": {
                "filter": "box_blur",
                "radius": 10
            }
        },
        {
            "identifier": "11",
            "transformation": "thumbnail"
        }
    ]
```

2. Use the `image_processing_transform` function to apply transformations to an image, specifying the `user_id`, `image_path`, `transformations`, `parent_folder` (optional), and `chain` (optional).
``` python
from apps.image_processing.models import (
    ProcessingImage,
)
from apps.image_processing_api.services import image_processing_transform
...
image = ProcessingImage.objects.create(...)
applied_transformations = image_processing_transform(
    user=request.user.id,
    image_ids=[image.id],
    transformations=transformations,
    is_chain=True, # Defaults to False
)

for transformation in applied_transformations:
    logger.info(f"{transformation['id']} - {transformation['task_id']} - {transformation['task_status']}")
...
```

## How It Works Inside:

### Transformations (`image_processing.core.transformations`):

The core logic for applying custom image transformations. This includes the actual transformation logic using the Pillow (PIL) library. They take an image, apply a transformation based on the provided filters, and return a transformed PIL image copy.

Make your own transformation like this and create the corresponding filters interfaces:
```python
from PIL import Image as PImage

from .base import (
    ExternalTransformationFilters,
    InternalImageTransformation,
    InternalImageTransformationFilters,
)

# Define custom filters
@dataclass
class InternalTransformationFiltersCrop(InternalImageTransformationFilters):
    x : ComplexObject()
    y : ComplexObject2()


# Define external representation with native types and `to_internal` method
@dataclass
class ExternalTransformationFiltersCrop(InternalTransformationFiltersCrop):
    x : float
    y : float

    def to_internal(self) -> InternalTransformationFiltersCrop:
        return InternalTransformationFiltersCrop(
            x = ComplexObject(...),
            y = ComplexObject2(...)
        )

# Define the transformation
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

### Transformation filters (`image_processing.core.transformations.base`):

Each transformation has its own set of filters, which are defined in the `ExternalTransformationFilters` interface. These filters are used to specify the parameters for the transformation.

The `ExternalTransformationFilters` implementations must be able to be converted to the corresponding `InternalImageTransformationFilters` implementations using the `to_internal` method.

### Transformers (`image_processing.src.transformers`):

Defines different strategies for applying transformations, they take a list of
`InternalImageTransformation` wich contains the `transformation` to apply with the corresponding `filters` and the provided `identifier`.

Make your own transformers like this:
```python
from PIL import Image as PImage

from apps.image_processing.core.transformers.base import (
    InternalImageTransformationResult,
)
from apps.image_processing.models import TransformationBatch

from .base import BaseImageTransformer


class ImageSequentialTransformer(BaseImageTransformer): # Inherit from BaseImageTransformer
    name = TransformationBatch.SEQUENTIAL # Give it a name

    # Must implement the `_transform` method
    def _transform(
        self, image: PImage.Image
    ) -> list[InternalImageTransformationResult]:
        transformations = []
        for transform_data in self.transformations_data:
            transformation = transform_data.transformation( # InternalImageTransformation instance
                image, # All transformations should return a new PIL.Image.Image instance
                transform_data.filters, # Matching `transformation` filter
            )
            transformations.append(
                InternalImageTransformationResult(
                    identifier=transform_data.identifier, # Return the same identifier
                    transformation_name=transform_data.transformation.name,
                    applied_filters=transform_data.filters,
                    image=transformation.image_transformed, # Transformed image
                )
            )
        return transformations # Must return list[InternalImageTransformationResult]
```

### Managers (`image_processing.src.managers`):

Manages the overall image processing workflow. It takes an image path, a list of
transformations, and a parent folder name, and applies the transformations using
the selected transformer.

Make your own manager like this:
```python
import io

import boto3
from PIL import Image as PImage

from apps.image_processing.src.managers import BaseImageManager
from apps.image_processing.src.data_models import InternalTransformationManagerSaveResult


class ImageS3Manager(BaseImageManager): # Inherit from BaseImageManager
    # Must implement the `_get_image` method
    def _get_image(self) -> PImage.Image:
        # Handle your custom manager image loading logic
        # and convert to PIL.Image.Image
        image = self._s3_bucket().Object(key)
        response = image.get()
        file_stream = response['Body']
        return PImage.open(file_stream)

    # Can add extra custom properties
    @property
    def _s3_bucket(self):
        resource_s3 = boto3.resource('s3', region_name='us-outwest-1')
        the_bucket = resource_s3.Bucket("the_bucket")
        return the_bucket

    # Can define extra custom methods
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

    # Another custom method
    def _load_and_save(self, image: PImage.Image, identifier: str):
        image_buffer = BytesIO()
        image.save(image_buffer, format='png')
        image_buffer.seek(0)
        image_uploaded = self._s3_bucket.Object.put(
            body=image_buffer, Key=identifier
        )
        return image_uploaded.url
```

### Mix all together:

```python
from apps.image_processing.core.transformers.base import (
    InternalImageTransformationDefinition
)

...
image = ProcessingImage.objects.get(id=image_id, user_id=user_id)
transformations= [
    InternalImageTransformationDefinition(
        identifier="CROP/default",
        transformation=TransformationCrop,
        filters=InternalTransformationFiltersCrop(
            x=80.4,
            y=20,
        )
    ),
    ...
]
image_transformer = ImageSequentialTransformer(transformations)
s3_manager = ImageS3Manager(
    image=image,
    transformer=image_transformer,
)
s3_manager.apply_transformations()
s3_manager.save(parent_folder="output")
...

```
