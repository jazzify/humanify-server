from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.pagination import LimitOffsetPagination, get_paginated_response
from apps.api.serializers import ValidationErrorSerializer
from apps.image_processing.models import ProcessingImage
from apps.image_processing_api.serializers import (
    ImageProcessingCreateInputSerializer,
    ImageProcessingModelSerializer,
    ImageProcessInputSerializer,
)
from apps.image_processing_api.services import (
    image_processing_create,
    image_processing_transform,
)


class ImageProcessingCreateListApi(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    pagination_class = LimitOffsetPagination

    @extend_schema(
        summary="Create processing images",
        request=ImageProcessingCreateInputSerializer,
        responses={
            status.HTTP_201_CREATED: None,
            status.HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ImageProcessingCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_images = image_processing_create(
            user=request.user,
            images=serializer.validated_data["files"],
        )
        return get_paginated_response(
            pagination_class=self.pagination_class,
            serializer_class=ImageProcessingModelSerializer,
            queryset=created_images,
            request=request,
            view=self,
        )

    def get(self, request: Request) -> Response:
        # query_serializer = ImageProcessingListQuerySerializer(data=request.query_params)
        # query_serializer.is_valid(raise_exception=True)

        images = ProcessingImage.objects.filter(user=request.user)
        return get_paginated_response(
            pagination_class=self.pagination_class,
            serializer_class=ImageProcessingModelSerializer,
            queryset=images,
            request=request,
            view=self,
        )


class ImageProcessTransformApi(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Transform image",
        request=ImageProcessInputSerializer,
        responses={
            status.HTTP_201_CREATED: None,
            status.HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ImageProcessInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transformations = image_processing_transform(
            user=request.user,
            image_ids=serializer.validated_data["images"],
            transformations=serializer.validated_data["transformations"],
            is_chain=serializer.validated_data["apply_chain"],
        )
        # transformations = image_process(serializer.validated_data)

        return Response(transformations, status=status.HTTP_201_CREATED)

        # created_images = image_processing_create(
        #     user=request.user,
        #     images=serializer.validated_data["files"],
        # )
        # return get_paginated_response(
        #     pagination_class=self.pagination_class,
        #     serializer_class=ImageProcessingModelSerializer,
        #     queryset=created_images,
        #     request=request,
        #     view=self,
        # )
