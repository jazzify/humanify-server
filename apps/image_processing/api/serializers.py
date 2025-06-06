from rest_framework import serializers

from apps.image_processing.models import Image


class ImageProcessingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "file"]


class ImageProcessingCreateInputSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.ImageField(write_only=True, required=False),
        write_only=True,
        required=False,
        max_length=10,
    )
