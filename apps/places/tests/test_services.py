import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.places.models import Place, PlaceImage, PlaceTag
from apps.places.services import create_place, get_all_places_by_user
from apps.places.tests.factories import PlaceFactory, PlaceImageFactory, PlaceTagFactory


@pytest.mark.django_db
def test_get_all_places_by_user_empty(user):
    """Test getting places when user has no places"""
    places = get_all_places_by_user(user)
    assert len(places) == 0


@pytest.mark.django_db
def test_get_all_places_by_user_with_places(user, other_user):
    """Test getting places when user has places"""
    # Create 3 places for the user
    places = [PlaceFactory(user=user) for _ in range(3)]

    # Create 2 places for another user (should not be returned)
    other_places = [PlaceFactory(user=other_user) for _ in range(2)]

    # Get places for the user
    user_places = get_all_places_by_user(user)

    # Check that only the user's places are returned
    assert len(user_places) == 3
    for place in user_places:
        assert place.user == user


@pytest.mark.django_db
def test_get_all_places_by_user_with_related_data(user):
    """Test that related data is prefetched"""
    # Create a place with tags and images
    place = PlaceFactory(user=user)

    # Add tags
    tags = [PlaceTagFactory(user=user) for _ in range(2)]
    place.tags.add(*tags)

    # Add images
    images = [PlaceImageFactory(place=place) for _ in range(2)]

    # Get places
    places = get_all_places_by_user(user)

    # Check that related data is prefetched
    assert len(places) == 1
    assert places[0].tags.count() == 2
    assert places[0].place_images.count() == 2


@pytest.mark.django_db
def test_create_place_basic(user):
    """Test creating a place with basic information"""
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
    assert place.place_images.count() == 0


@pytest.mark.django_db
def test_create_place_with_optional_fields(user):
    """Test creating a place with optional fields"""
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
    """Test creating a place with tags"""
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


@pytest.mark.django_db
def test_create_place_with_images(user):
    """Test creating a place with images"""
    # Create test image files
    image1 = SimpleUploadedFile(
        name="test_image1.jpg",
        content=b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        content_type="image/jpeg",
    )
    image2 = SimpleUploadedFile(
        name="test_image2.jpg",
        content=b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        content_type="image/jpeg",
    )

    place = create_place(
        user=user,
        name="Test Place",
        city="Test City",
        latitude=40.7128,
        longitude=-74.0060,
        images=[image1, image2],
    )

    # Check that images were created and associated with the place
    assert place.place_images.count() == 2


@pytest.mark.django_db
def test_create_place_with_all_fields(user):
    """Test creating a place with all fields"""
    tag_names = ["tag1", "tag2"]
    image = SimpleUploadedFile(
        name="test_image.jpg",
        content=b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        content_type="image/jpeg",
    )

    place = create_place(
        user=user,
        name="Test Place",
        city="Test City",
        latitude=40.7128,
        longitude=-74.0060,
        tag_names=tag_names,
        images=[image],
        favorite=True,
        description="Test description",
    )

    # Check that place was created correctly with all fields
    assert place.user == user
    assert place.name == "Test Place"
    assert place.city == "Test City"
    assert place.latitude == 40.7128
    assert place.longitude == -74.0060
    assert place.favorite is True
    assert place.description == "Test description"
    assert place.tags.count() == 2
    assert place.place_images.count() == 1
