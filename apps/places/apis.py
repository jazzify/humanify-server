from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.places.serializers import PlaceCreateSerializer, PlaceSerializer
from apps.places.services import create_place, get_all_places_by_user


class CreateListPlaceAPIView(APIView):
    @extend_schema(
        summary="Create Place",
        request=PlaceCreateSerializer,
        responses={status.HTTP_201_CREATED: PlaceSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = PlaceCreateSerializer(data=request.data)
        if serializer.is_valid():
            new_place = create_place(
                user=request.user,
                name=serializer.validated_data["name"],
                description=serializer.validated_data["description"],
                city=serializer.validated_data["city"],
                latitude=serializer.validated_data["latitude"],
                longitude=serializer.validated_data["longitude"],
                tag_names=serializer.validated_data["tags"],
                images=serializer.validated_data["images"],
                favorite=serializer.validated_data["favorite"],
            )
            return Response(
                PlaceSerializer(new_place).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="List Places",
        responses={status.HTTP_200_OK: PlaceSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        places = get_all_places_by_user(user=request.user)
        serializer = PlaceSerializer(places, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
