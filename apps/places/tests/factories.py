import factory
from django.core.files.base import ContentFile
from factory.django import DjangoModelFactory

from apps.common.tests import faker
from apps.places.models import Place, PlaceImage, PlaceTag
from apps.users.tests.factories import BaseUserFactory


class PlaceTagFactory(DjangoModelFactory):
    class Meta:
        model = PlaceTag
        django_get_or_create = ("user", "name")

    user = factory.SubFactory(BaseUserFactory)
    name = factory.LazyFunction(lambda: faker.word()[:10])  # Max length is 10


class PlaceFactory(DjangoModelFactory):
    class Meta:
        model = Place
        skip_postgeneration_save = True

    user = factory.SubFactory(BaseUserFactory)
    name = factory.LazyFunction(lambda: faker.company())
    city = factory.LazyFunction(lambda: faker.city())
    description = factory.LazyFunction(lambda: faker.text(max_nb_chars=500))
    latitude = factory.LazyFunction(lambda: float(faker.latitude()))
    longitude = factory.LazyFunction(lambda: float(faker.longitude()))
    favorite = factory.LazyFunction(lambda: faker.boolean())

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for tag in extracted:
            self.tags.add(tag)


class PlaceImageFactory(DjangoModelFactory):
    class Meta:
        model = PlaceImage

    place = factory.SubFactory(PlaceFactory)

    @factory.lazy_attribute
    def image(self):
        img_content = ContentFile(
            name=faker.text(max_nb_chars=500),
            content=b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00"
            b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        )
        return img_content
