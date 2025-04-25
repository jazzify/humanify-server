import shutil

import pytest
from django.conf import settings

from apps.users.tests.factories import BaseUserFactory


@pytest.fixture
def user() -> BaseUserFactory:
    return BaseUserFactory()


@pytest.fixture
def other_user() -> BaseUserFactory:
    return BaseUserFactory()


@pytest.fixture(scope="session", autouse=True)
def clean_test_media() -> None:
    """
    Fixture to ensure the test media directory is clean before and after tests.
    """
    test_media_root = settings.MEDIA_ROOT
    # Clean up before tests run
    if test_media_root.exists():
        shutil.rmtree(test_media_root)
    test_media_root.mkdir(parents=True, exist_ok=True)

    # Yield control to the tests
    yield

    # Clean up after tests run
    if test_media_root.exists():
        shutil.rmtree(test_media_root)
