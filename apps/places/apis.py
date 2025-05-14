from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
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
    place_create,
    place_delete_by_id_and_user,
    place_images_create,
    place_retrieve_all_by_user,
    place_retrieve_by_id_and_user,
)


class PlaceImageAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

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

        place_images_create(
            place_id=place_id,
            images=serializer.validated_data["files"],
        )

        return Response(status=status.HTTP_201_CREATED)


class PlaceDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve place",
        responses={
            status.HTTP_200_OK: PlaceSerializer,
            status.HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
        },
    )
    def get(self, request: Request, place_id: int) -> Response:
        place = place_retrieve_by_id_and_user(place_id=place_id, user=request.user)
        serializer = PlaceSerializer(place)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete place",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
        },
    )
    def delete(self, request: Request, place_id: int) -> Response:
        place_delete_by_id_and_user(place_id=place_id, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlaceAPI(APIView):
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
        place_create(
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
        places = place_retrieve_all_by_user(user=request.user)
        serializer = PlaceSerializer(places, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
