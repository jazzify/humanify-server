from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers import ValidationErrorSerializer
from apps.places.serializers import (
    PlaceCreateSerializer,
    PlaceImageCreateSerializer,
    PlaceSerializer,
)
from apps.places.services import (
    create_place,
    create_place_images,
    get_all_places_by_user,
)


class CreatePlaceImageAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create place images",
        request=PlaceImageCreateSerializer,
        responses={
            status.HTTP_201_CREATED: None,
            status.HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
        },
    )
    def post(self, request: Request, place_id: int) -> Response:
        serializer = PlaceImageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_place_images(
            place_id=place_id,
            images=serializer.validated_data["files"],
        )

        return Response(status=status.HTTP_201_CREATED)


class CreateListPlaceAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create place",
        request=PlaceCreateSerializer,
        responses={
            status.HTTP_201_CREATED: None,
            status.HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = PlaceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_place(
            user=request.user,
            name=serializer.validated_data["name"],
            description=serializer.validated_data["description"],
            city=serializer.validated_data["city"],
            latitude=serializer.validated_data["latitude"],
            longitude=serializer.validated_data["longitude"],
            tag_names=serializer.validated_data["tags"],
            favorite=serializer.validated_data["favorite"],
        )
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="List places",
        responses={status.HTTP_200_OK: PlaceSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        places = get_all_places_by_user(user=request.user)
        serializer = PlaceSerializer(places, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
