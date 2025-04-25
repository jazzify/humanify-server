import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.places.constants import PLACE_IMAGES_LIMIT
from apps.places.models import PlaceImage
from apps.places.tests.factories import PlaceFactory


@pytest.mark.django_db
def test_place_image_limit_validation(user):
    """Test that saving more than PLACE_IMAGES_LIMIT images for a place raises ValidationError."""
    place = PlaceFactory(user=user)

    # Create PLACE_IMAGES_LIMIT images successfully
    for i in range(PLACE_IMAGES_LIMIT):
        image_file = SimpleUploadedFile(
            name=f"test_image_{i}.jpg",
            content=b"dummy_content",
            content_type="image/jpeg",
        )
        PlaceImage.objects.create(place=place, image=image_file)

    # Verify the count is correct so far
    assert place.images.count() == PLACE_IMAGES_LIMIT

    # Attempt to create one more image (the 11th one)
    extra_image_file = SimpleUploadedFile(
        name="extra_image.jpg",
        content=b"extra_dummy_content",
        content_type="image/jpeg",
    )
    extra_image = PlaceImage(place=place, image=extra_image_file)

    # Expect a ValidationError when saving the 11th image directly
    with pytest.raises(
        ValidationError,
        match=f"A place cannot have more than {PLACE_IMAGES_LIMIT} images.",
    ):
        extra_image.save()  # This should trigger the model's save validation

    # Ensure the 11th image was not actually saved
    assert place.images.count() == PLACE_IMAGES_LIMIT
