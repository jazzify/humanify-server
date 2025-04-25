import pytest
from django.core.exceptions import ValidationError

from apps.users.models import BaseUser
from apps.users.services import user_create


@pytest.mark.django_db
def test_user_without_password_is_created_with_unusable_one():
    user = user_create(email="random_user@example.io")
    assert not user.has_usable_password()


@pytest.mark.django_db
def test_user_with_capitalized_email_cannot_be_created():
    user_create(email="random_user@example.io")
    with pytest.raises(ValidationError):
        user_create(email="RANDOM_user@example.io")
    assert BaseUser.objects.count() == 1


@pytest.mark.django_db
def test_user_with_password_is_created_with_usable_one():
    user = user_create(email="user_with_pass@example.io", password="securepass123")
    assert user.has_usable_password()
    assert user.check_password("securepass123")


@pytest.mark.django_db
def test_user_with_duplicate_email_raises_error():
    user_create(email="duplicate@example.io")
    with pytest.raises(ValidationError):
        user_create(email="duplicate@example.io")
    assert BaseUser.objects.count() == 1


@pytest.mark.django_db
def test_user_with_invalid_email_raises_error():
    with pytest.raises(ValidationError):
        user_create(email="not-an-email")
    assert BaseUser.objects.count() == 0


@pytest.mark.django_db
def test_user_with_empty_email_raises_error():
    with pytest.raises(ValueError):
        user_create(email=None)
    assert BaseUser.objects.count() == 0


@pytest.mark.django_db
def test_user_email_is_normalized():
    user = user_create(email="MiXeDCase@Example.IO")
    assert user.email == "mixedcase@example.io"


@pytest.mark.django_db
def test_user_is_active_by_default():
    user = user_create(email="active@example.io")
    assert user.is_active


@pytest.mark.django_db
def test_user_is_not_admin_or_superuser_by_default():
    user = user_create(email="normal@example.io")
    assert not user.is_admin
    assert not user.is_superuser
