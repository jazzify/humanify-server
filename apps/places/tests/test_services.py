from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.places.constants import PLACE_IMAGES_LIMIT
from apps.places.services import (
    create_place,
    create_place_images,
    get_all_places_by_user,
)
from apps.places.tests.factories import PlaceFactory, PlaceImageFactory, PlaceTagFactory


@pytest.mark.django_db
def test_get_all_places_by_user_empty(user):
    places = get_all_places_by_user(user)
    assert len(places) == 0


@pytest.mark.django_db
def test_get_all_places_by_user_with_places(user, other_user):
    [PlaceFactory(user=user) for _ in range(3)]

    # Create 2 places for another user (should not be returned)
    [PlaceFactory(user=other_user) for _ in range(2)]

    user_places = get_all_places_by_user(user)

    assert len(user_places) == 3
    for place in user_places:
        assert place.user == user


@pytest.mark.django_db
def test_get_all_places_by_user_num_queries(user, django_assert_num_queries):
    place = PlaceFactory(user=user)
    tags = [PlaceTagFactory(user=user) for _ in range(2)]
    place.tags.add(*tags)
    [PlaceImageFactory(place=place) for _ in range(2)]

    with django_assert_num_queries(3):
        places = get_all_places_by_user(user)
        assert len(places) == 1


@pytest.mark.django_db
def test_get_all_places_by_user_with_related_data(user):
    place = PlaceFactory(user=user)
    tags = [PlaceTagFactory(user=user) for _ in range(2)]
    place.tags.add(*tags)
    [PlaceImageFactory(place=place) for _ in range(2)]

    places = get_all_places_by_user(user)

    assert len(places) == 1
    assert places[0].tags.count() == 2
    assert places[0].images.count() == 2


@pytest.mark.django_db
def test_create_place_basic(user):
    place = create_place(
        user=user,
        name="Test Place",
        city="Test City",
        latitude=40.7128,
        longitude=-74.0060,
    )

    # Check that place was created correctly
    assert place.user == user
    assert place.name == "Test Place"
    assert place.city == "Test City"
    assert place.latitude == 40.7128
    assert place.longitude == -74.0060
    assert place.favorite is False
    assert place.description is None
    assert place.tags.count() == 0
    assert place.images.count() == 0


@pytest.mark.django_db
def test_create_place_with_optional_fields(user):
    place = create_place(
        user=user,
        name="Test Place",
        city="Test City",
        latitude=40.7128,
        longitude=-74.0060,
        favorite=True,
        description="Test description",
    )

    # Check that place was created correctly
    assert place.favorite is True
    assert place.description == "Test description"


@pytest.mark.django_db
def test_create_place_with_tags(user):
    tag_names = ["tag1", "tag2", "tag3"]

    place = create_place(
        user=user,
        name="Test Place",
        city="Test City",
        latitude=40.7128,
        longitude=-74.0060,
        tag_names=tag_names,
    )

    # Check that tags were created and associated with the place
    assert place.tags.count() == 3
    db_tag_names = [tag.name for tag in place.tags.all()]
    for tag_name in tag_names:
        assert tag_name in db_tag_names

    # Check that tags are associated with the user
    for tag in place.tags.all():
        assert tag.user == user


@patch("apps.places.services.process_uploaded_images")
@pytest.mark.django_db
def test_create_place_images(mock_process_uploaded_images, user):
    place = PlaceFactory(user=user)

    image1 = SimpleUploadedFile(
        name="test_image1.jpg",
        content=b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        content_type="image/jpeg",
    )
    SimpleUploadedFile(
        name="test_image2.jpg",
        content=b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        content_type="image/jpeg",
    )

    create_place_images(
        place_id=place.id,
        images=[image1],
    )

    assert place.images.count() == 1

    mock_process_uploaded_images.enqueue.assert_called_once_with(
        file_path=f"{settings.MEDIA_ROOT}/place_images/test_image1.jpg",
        root_folder="place_images",
        parent_folder=str(1),
    )


@pytest.mark.django_db
def test_create_place_images_exceed_limit(user):
    place = PlaceFactory(user=user)
    images = [
        SimpleUploadedFile(
            name=f"test_image_{i}.jpg",
            content=b"dummy_content",
            content_type="image/jpeg",
        )
        for i in range(PLACE_IMAGES_LIMIT)
    ]
    create_place_images(place_id=place.id, images=images)
    assert place.images.count() == PLACE_IMAGES_LIMIT
    extra_image = SimpleUploadedFile(
        name="extra_image.jpg",
        content=b"extra_dummy_content",
        content_type="image/jpeg",
    )
    with pytest.raises(
        ValidationError,
        match=f"A place cannot have more than {PLACE_IMAGES_LIMIT} images.",
    ):
        create_place_images(place_id=place.id, images=[extra_image])
    assert place.images.count() == PLACE_IMAGES_LIMIT


@pytest.mark.django_db
def test_create_place_images_invalid_place():
    invalid_place_id = 999999
    image = SimpleUploadedFile(
        name="test_image.jpg",
        content=b"dummy_content",
        content_type="image/jpeg",
    )
    with pytest.raises(ValidationError, match="Place with id"):
        create_place_images(place_id=invalid_place_id, images=[image])
