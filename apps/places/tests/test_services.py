from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.places.constants import PLACE_IMAGES_LIMIT
from apps.places.models import Place
from apps.places.services import (
    place_create,
    place_delete_by_id_and_user,
    place_images_create,
    place_images_retrive_by_place_id_and_user,
    place_retrieve_all_by_user,
    place_retrieve_by_id_and_user,
)
from apps.places.tests.factories import PlaceFactory, PlaceImageFactory, PlaceTagFactory


@pytest.mark.django_db
def test_place_retrieve_all_by_user_empty(user):
    places = place_retrieve_all_by_user(user)
    assert len(places) == 0


@pytest.mark.django_db
def test_place_retrieve_all_by_user_with_places(user, other_user):
    [PlaceFactory(user=user) for _ in range(3)]

    # Create 2 places for another user (should not be returned)
    [PlaceFactory(user=other_user) for _ in range(2)]

    user_places = place_retrieve_all_by_user(user)

    assert len(user_places) == 3
    for place in user_places:
        assert place.user == user


@pytest.mark.django_db
def test_place_retrieve_all_by_user_num_queries(user, django_assert_num_queries):
    place = PlaceFactory(user=user)
    tags = [PlaceTagFactory(user=user) for _ in range(2)]
    place.tags.add(*tags)
    [PlaceImageFactory(place=place) for _ in range(2)]

    with django_assert_num_queries(3):
        places = place_retrieve_all_by_user(user)
        assert len(places) == 1


@pytest.mark.django_db
def test_place_retrieve_all_by_user_with_related_data(user):
    place = PlaceFactory(user=user)
    tags = [PlaceTagFactory(user=user) for _ in range(2)]
    place.tags.add(*tags)
    [PlaceImageFactory(place=place) for _ in range(2)]

    places = place_retrieve_all_by_user(user)

    assert len(places) == 1
    assert places[0].tags.count() == 2
    assert places[0].images.count() == 2


@pytest.mark.django_db
def test_place_create_basic(user):
    place = place_create(
        user=user,
        name="Test Place",
        city="Test City",
        latitude=40.7128,
        longitude=-74.0060,
    )

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
def test_place_create_with_optional_fields(user):
    place = place_create(
        user=user,
        name="Test Place",
        city="Test City",
        latitude=40.7128,
        longitude=-74.0060,
        favorite=True,
        description="Test description",
    )

    assert place.favorite is True
    assert place.description == "Test description"


@pytest.mark.django_db
def test_place_create_with_tags(user):
    tag_names = ["tag1", "tag2", "tag3"]

    place = place_create(
        user=user,
        name="Test Place",
        city="Test City",
        latitude=40.7128,
        longitude=-74.0060,
        tag_names=tag_names,
    )

    assert place.tags.count() == 3
    db_tag_names = [tag.name for tag in place.tags.all()]
    for tag_name in tag_names:
        assert tag_name in db_tag_names

    for tag in place.tags.all():
        assert tag.user == user


@patch("apps.places.services.transform_uploaded_images")
@pytest.mark.django_db
def test_place_images_create(mock_transform_uploaded_images, user):
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

    place_images_create(
        place_id=place.id,
        images=[image1],
    )

    assert place.images.count() == 1

    mock_transform_uploaded_images.enqueue.assert_called_once_with(
        file_path=f"{settings.MEDIA_ROOT}/place_images/test_image1.jpg",
        root_folder="place_images",
        parent_folder=str(1),
    )


@pytest.mark.django_db
def test_place_images_create_exceed_limit(user):
    place = PlaceFactory(user=user)
    images = [
        SimpleUploadedFile(
            name=f"test_image_{i}.jpg",
            content=b"dummy_content",
            content_type="image/jpeg",
        )
        for i in range(PLACE_IMAGES_LIMIT)
    ]
    place_images_create(place_id=place.id, images=images)
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
        place_images_create(place_id=place.id, images=[extra_image])
    assert place.images.count() == PLACE_IMAGES_LIMIT


@pytest.mark.django_db
def test_place_images_create_invalid_place():
    invalid_place_id = 999999
    image = SimpleUploadedFile(
        name="test_image.jpg",
        content=b"dummy_content",
        content_type="image/jpeg",
    )
    with pytest.raises(ValidationError, match="Place with id"):
        place_images_create(place_id=invalid_place_id, images=[image])


@pytest.mark.django_db
def test_place_retrieve_by_id_and_user_success(user, django_assert_num_queries):
    place = PlaceFactory(user=user)

    with django_assert_num_queries(1):
        retrieved_place = place_retrieve_by_id_and_user(place_id=place.id, user=user)
        assert retrieved_place == place
        assert retrieved_place.user == user


@pytest.mark.django_db
def test_place_retrieve_by_id_and_user_not_found(user):
    non_existent_place_id = 99999
    with pytest.raises(ValidationError) as excinfo:
        place_retrieve_by_id_and_user(place_id=non_existent_place_id, user=user)
        assert (
            str(excinfo.value.message_dict["place_id"][0])
            == f"Place with id {non_existent_place_id} does not exist for user {user.email}"
        )


@pytest.mark.django_db
def test_place_retrieve_by_id_and_user_different_user(user, other_user):
    place_other_user = PlaceFactory(user=other_user)
    with pytest.raises(ValidationError) as excinfo:
        place_retrieve_by_id_and_user(place_id=place_other_user.id, user=user)
        assert (
            str(excinfo.value.message_dict["place_id"][0])
            == f"Place with id {place_other_user.id} does not exist for user {user.email}"
        )


@pytest.mark.django_db
def test_place_delete_by_id_and_user_success(user, django_assert_num_queries):
    place = PlaceFactory(user=user)
    place_id = place.id

    with django_assert_num_queries(4):
        place_delete_by_id_and_user(place_id=place_id, user=user)

    with pytest.raises(Place.DoesNotExist):
        Place.objects.get(id=place_id)


@pytest.mark.django_db
def test_place_delete_by_id_and_user_not_found(user):
    non_existent_place_id = 999999
    with pytest.raises(ValidationError) as excinfo:
        place_delete_by_id_and_user(place_id=non_existent_place_id, user=user)
    assert "place_id" in excinfo.value.message_dict
    assert (
        f"Place with id {non_existent_place_id} does not exist for user {user.email}"
        in excinfo.value.message_dict["place_id"]
    )


@pytest.mark.django_db
def test_place_delete_by_id_and_user_different_user(user, other_user):
    place_other_user = PlaceFactory(user=other_user)

    with pytest.raises(ValidationError) as excinfo:
        place_delete_by_id_and_user(place_id=place_other_user.id, user=user)

    assert "place_id" in excinfo.value.message_dict
    assert (
        f"Place with id {place_other_user.id} does not exist for user {user.email}"
        in excinfo.value.message_dict["place_id"]
    )

    assert Place.objects.filter(id=place_other_user.id).exists()


@pytest.mark.django_db
def test_place_images_retrive_by_place_id_and_user_success(
    user, django_assert_num_queries
):
    place = PlaceFactory(user=user)
    image1 = PlaceImageFactory(place=place)
    image2 = PlaceImageFactory(place=place)

    with django_assert_num_queries(1):
        retrieved_images = place_images_retrive_by_place_id_and_user(place.id, user)
        assert len(retrieved_images) == 2
        for image in retrieved_images:
            assert image.place == place
            assert image in [image1, image2]


@pytest.mark.django_db
def test_place_images_retrive_by_place_id_and_user_no_images(user):
    place = PlaceFactory(user=user)
    retrieved_images = place_images_retrive_by_place_id_and_user(place.id, user)
    assert len(retrieved_images) == 0


@pytest.mark.django_db
def test_place_images_retrive_by_place_id_and_user_different_user(user, other_user):
    place_other_user = PlaceFactory(user=other_user)
    PlaceImageFactory(place=place_other_user)
    retrieved_images = place_images_retrive_by_place_id_and_user(
        place_other_user.id, user
    )
    assert len(retrieved_images) == 0


@pytest.mark.django_db
def test_place_images_retrive_by_place_id_and_user_invalid_place(user):
    invalid_place_id = 999999
    retrieved_images = place_images_retrive_by_place_id_and_user(invalid_place_id, user)
    assert len(retrieved_images) == 0
