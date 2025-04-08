from django.contrib import admin

from apps.places.models import Place, PlaceImage, PlaceTag


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    pass


@admin.register(PlaceImage)
class PlaceImageAdmin(admin.ModelAdmin):
    pass


@admin.register(PlaceTag)
class PlaceTagAdmin(admin.ModelAdmin):
    pass
