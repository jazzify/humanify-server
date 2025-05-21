"""https://docs.djangoproject.com/en/5.2/topics/http/urls/"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

#### Apps
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.api.urls")),
]

#### Django Debug Toolbar
if settings.DEBUG:
    urlpatterns = [
        *urlpatterns,
        path("__debug__/", include("debug_toolbar.urls")),
    ]
