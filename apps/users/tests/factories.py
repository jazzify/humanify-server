import factory
from factory.django import DjangoModelFactory

from apps.common.tests import faker
from apps.users.models import BaseUser


class BaseUserFactory(DjangoModelFactory):
    class Meta:
        model = BaseUser
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")  # Unique username
    email = factory.LazyFunction(lambda: faker.email())
    first_name = factory.LazyFunction(lambda: faker.first_name())
    last_name = factory.LazyFunction(lambda: faker.last_name())
    is_active = True
    is_admin = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if create:
            self.set_password(extracted or "password")
