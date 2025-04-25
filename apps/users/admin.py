from django.contrib import admin

from apps.users.models import BaseUser


@admin.register(BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "is_admin",
        "is_superuser",
        "is_active",
    )
    search_fields = ("email",)
    list_filter = ("is_active", "is_admin", "is_superuser")

    readonly_fields = (
        "last_login",
        "is_superuser",
    )
