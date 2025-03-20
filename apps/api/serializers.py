from rest_framework import serializers


class BaseErrorSerializer(serializers.Serializer):
    message = serializers.CharField()
    extra = serializers.DictField(label="Can be empty", allow_empty=True)
