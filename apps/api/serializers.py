from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers


class BaseErrorSerializer(serializers.Serializer):
    message = serializers.CharField()
    extra = serializers.DictField(label="Can be empty", allow_empty=True)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Validation error",
            value={
                "message": "Validation error",
                "extra": {
                    "fields": {
                        "field_name": ["error1", "error2"],
                        "field_name2": ["error1", "error2"],
                    }
                },
            },
        ),
    ]
)
class ValidationErrorSerializer(serializers.Serializer):
    message = serializers.CharField()
    extra = serializers.DictField(
        child=serializers.DictField(
            child=serializers.ListField(child=serializers.CharField())
        )
    )
