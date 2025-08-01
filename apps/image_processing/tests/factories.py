import factory
from django.core.files.base import ContentFile
from factory.django import DjangoModelFactory

from apps.common.tests import faker
from apps.image_processing.models import ProcessingImage, TransformationBatch
from apps.users.tests.factories import BaseUserFactory


class ProcessingImageFactory(DjangoModelFactory):
    class Meta:
        model = ProcessingImage
        skip_postgeneration_save = True

    user = factory.SubFactory(BaseUserFactory)

    @factory.lazy_attribute
    def file(self):
        img_content = ContentFile(
            name=faker.text(max_nb_chars=255),
            content=b"0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff,0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xf0",
        )
        return img_content


class TransformationBatchFactory(DjangoModelFactory):
    class Meta:
        model = TransformationBatch
        skip_postgeneration_save = True

    input_image = factory.SubFactory(ProcessingImageFactory)
