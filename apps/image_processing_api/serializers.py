from typing import Any, Type

from rest_framework import serializers
from rest_framework.exceptions import ParseError, ValidationError

from apps.image_processing.models import ProcessingImage
from apps.image_processing_api.constants import (
    ImageTransformations,
    TransformationFilterBlurFilter,
)


class ImageProcessingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingImage
        fields = ["id", "file"]


class ImageProcessingCreateInputSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.ImageField(write_only=True, required=False),
        write_only=True,
        required=False,
        max_length=10,
    )


class ImageFilterSerializer(serializers.Serializer):
    pass


class BlurFilterSerializer(ImageFilterSerializer):
    filter = serializers.ChoiceField(
        choices=[name.value for name in TransformationFilterBlurFilter]
    )
    radius = serializers.FloatField(required=False)


class ImageTransformationSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=100)
    transformation = serializers.ChoiceField(
        choices=[name.value for name in ImageTransformations]
    )
    filters = serializers.DictField(required=False)

    def _get_filter_serializer(
        self, transformation: str
    ) -> Type[ImageFilterSerializer]:
        if transformation == ImageTransformations.BLUR:
            return BlurFilterSerializer
        raise ParseError(
            f"Filters not yet supported for transformation: {transformation}"
        )

    def to_internal_value(self, data: Any) -> Any:
        internal = super().to_internal_value(data)

        if data.get("filters") is None:
            return internal

        filter_serializer = self._get_filter_serializer(data.get("transformation"))
        new_filters = filter_serializer(data=data.get("filters"))
        is_valid = new_filters.is_valid()
        if not is_valid:
            raise ValidationError({"filters": "Invalid filters for transformation"})
        internal["filters"] = new_filters.validated_data
        return internal


class ImageProcessInputSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.UUIDField(), write_only=True)
    apply_chain = serializers.BooleanField(required=False, default=False)
    transformations = ImageTransformationSerializer(many=True)
