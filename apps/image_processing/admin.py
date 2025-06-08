from django.contrib import admin
from django.utils.html import format_html

from apps.image_processing.models import (
    ImageTransformation,
    ProcessedImage,
    ProcessingImage,
    TransformationBatch,
)


@admin.register(ProcessingImage)
class ProcessingImageAdmin(admin.ModelAdmin):
    pass


@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    pass


class ImageTransformationInline(admin.TabularInline):
    model = ImageTransformation
    fields = ("identifier", "transformation", "filters", "display_processed_image")
    readonly_fields = (
        "identifier",
        "transformation",
        "filters",
        "display_processed_image",
    )
    extra = 0  # Do not show extra empty forms
    can_delete = (
        False  # Usually we don't want to delete transformations from batch view
    )

    def display_processed_image(self, obj):
        if (
            hasattr(obj, "processed_image")
            and obj.processed_image
            and obj.processed_image.file
        ):
            return format_html(
                '<a href="{0}" target="_blank"><img src="{0}" width="100" height="100"/></a><br/><a href="{0}" target="_blank">View Full Image</a>',
                obj.processed_image.file.url,
            )
        return "No processed image yet or not applicable."

    display_processed_image.short_description = "Processed Image"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(TransformationBatch)
class TransformationBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "input_image", "transformer", "created_at", "updated_at")
    list_filter = ("transformer", "created_at")
    search_fields = ("id", "input_image__file")
    readonly_fields = ("id", "input_image", "transformer", "created_at", "updated_at")
    inlines = [ImageTransformationInline]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("imagetransformation_set__processed_image")
        )


@admin.register(ImageTransformation)
class ImageTransformationAdmin(admin.ModelAdmin):
    pass
