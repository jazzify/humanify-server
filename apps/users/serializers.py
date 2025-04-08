from rest_framework import serializers

from apps.users.models import BaseUser


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ["id", "email", "first_name", "last_name", "is_active"]
