import pytest

from apps.users.tests.factories import BaseUserFactory


@pytest.fixture
def user() -> BaseUserFactory:
    return BaseUserFactory()


@pytest.fixture
def other_user() -> BaseUserFactory:
    return BaseUserFactory()
