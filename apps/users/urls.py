from django.urls import path

from apps.users.apis import UserCreateApi

urlpatterns = [
    path("", UserCreateApi.as_view(), name="user-create"),
]
