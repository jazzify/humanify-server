from rest_framework import serializers

from apps.places.constants import PLACE_IMAGES_LIMIT
from apps.places.models import Place, PlaceImage, PlaceTag
from apps.users.serializers import BaseUserSerializer


class PlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImage
        fields = ["id", "image_url"]


class PlaceTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceTag
        fields = ["id", "name"]


class PlaceCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(
        max_length=500, required=False, allow_blank=True
    )
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    tags = serializers.ListField(child=serializers.CharField(max_length=10))
    favorite = serializers.BooleanField(required=False)


class PlaceImageCreateSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.ImageField(write_only=True, required=False),
        write_only=True,
        required=False,
        max_length=PLACE_IMAGES_LIMIT,
    )


class PlaceImageDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    place = serializers.ReadOnlyField(source="place.id")
    image = serializers.ImageField()


class PlaceSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    images = PlaceImageDetailSerializer(many=True)

    def get_tags(self, obj: Place) -> list[str]:
        return [tag.name for tag in obj.tags.all()]

    class Meta:
        model = Place
        fields = [
            "id",
            "name",
            "description",
            "city",
            "latitude",
            "longitude",
            "tags",
            "images",
            "favorite",
            "description",
            "user_id",
            "created_at",
            "updated_at",
        ]
