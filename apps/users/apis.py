from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import BaseUserSerializer


class AuthMeAPIView(APIView):
    @extend_schema(
        summary="Auth Me",
        responses={status.HTTP_200_OK: BaseUserSerializer},
    )
    def get(self, request: Request) -> Response:
        serializer = BaseUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
