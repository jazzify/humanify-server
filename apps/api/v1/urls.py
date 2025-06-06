from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.users.apis import AuthMeAPI

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", AuthMeAPI.as_view(), name="auth_me"),
    path("docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("users/", include("apps.users.urls")),
    path("places/", include("apps.places.urls")),
    path("image_processing/", include("apps.image_processing.api.urls")),
]
