import factory
from factory.django import DjangoModelFactory

from apps.common.tests import faker
from apps.users.models import BaseUser


class BaseUserFactory(DjangoModelFactory):
    class Meta:
        model = BaseUser
        skip_postgeneration_save = True

    email = factory.LazyFunction(lambda: faker.email())
    is_active = True
    is_admin = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if create:
            self.set_password(extracted or "password")
