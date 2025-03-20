from collections import OrderedDict
from typing import Any, Type

from django.db.models import QuerySet
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_serializer,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.pagination import (
    BasePagination,
)
from rest_framework.pagination import (
    LimitOffsetPagination as _LimitOffsetPagination,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView


class LimitOffsetPagination(_LimitOffsetPagination):
    default_limit = 10
    max_limit = 50

    def get_paginated_data(self, data: dict[str, Any]) -> OrderedDict[str, Any]:
        return OrderedDict(
            [
                ("limit", self.limit),
                ("offset", self.offset),
                ("count", self.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data: dict[str, Any]) -> Response:
        """
        We redefine this method in order to return `limit` and `offset`.
        This is used by the frontend to construct the pagination itself.
        """
        return Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )


def get_paginated_response(
    *,
    pagination_class: Type[BasePagination],
    serializer_class: Type[BaseSerializer],
    queryset: QuerySet[Any],
    request: Request,
    view: APIView,
) -> Response:
    paginator = pagination_class()
    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)
    return Response(data=serializer.data)


def get_paginated_response_schema(
    schema: serializers.SerializerMetaclass,
    examples: list[OpenApiExample] | None = None,
) -> serializers.Serializer[Any]:
    pagination_next_schema = "https://example.com/api/v1/resource/?limit=5&offset=15"
    pagination_previous_schema = "https://example.com/api/v1/resource/?limit=5&offset=5"

    paginated_schema = inline_serializer(
        name=f"PaginatedResponse{schema.__name__}",
        fields={
            "limit": serializers.IntegerField(
                label="Default value for example purposes", default=5
            ),
            "offset": serializers.IntegerField(
                label="Default value for example purposes", default=10
            ),
            "count": serializers.IntegerField(
                label="Default value for example purposes", default=16
            ),
            "next": serializers.URLField(
                label="Default value for example purposes",
                allow_null=True,
                default=pagination_next_schema,
            ),
            "previous": serializers.URLField(
                label="Default value for example purposes",
                allow_null=True,
                default=pagination_previous_schema,
            ),
            "results": schema(many=True),
        },
    )

    # If the original schema has examples, create paginated versions
    if examples:
        paginated_examples = []
        for example in examples:
            # Create a paginated version of each example
            paginated_example = OpenApiExample(
                name=f"Paginated {example.name}",
                value={
                    "limit": 10,
                    "offset": 0,
                    "count": 1,
                    "next": pagination_next_schema,
                    "previous": pagination_previous_schema,
                    "results": [example.value],
                },
                response_only=example.response_only,
                request_only=example.request_only,
            )
            paginated_examples.append(paginated_example)

        # Apply the paginated examples to the schema
        return extend_schema_serializer(examples=paginated_examples)(paginated_schema)

    return paginated_schema
