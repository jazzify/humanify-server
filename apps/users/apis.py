from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import BaseUserSerializer
from apps.users.services import user_create


class AuthMeAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Auth me",
        responses={status.HTTP_200_OK: BaseUserSerializer},
    )
    def get(self, request: Request) -> Response:
        serializer = BaseUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    @extend_schema(
        summary="Create user",
        request=InputSerializer,
        responses={status.HTTP_201_CREATED: None},
    )
    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_create(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)
